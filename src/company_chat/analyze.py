"""Analyze normalized team chat into founder-ready operating signals."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


WORKSTREAM_KEYWORDS = {
    "sales": {"sales", "demo", "demos", "customer", "customers", "pipeline", "pipelines", "call", "calls", "deal", "deals", "trial", "trials"},
    "marketing": {"marketing", "post", "posts", "launch", "launches", "published", "pricing", "conversion", "conversions", "signup", "signups"},
    "operations": {"ops", "operation", "operations", "support", "queue", "queues", "migration", "migrations", "process", "processes", "cleanup"},
    "product": {"product", "products", "feature", "features", "bug", "bugs", "release", "releases", "website", "websites", "landing"},
}

BLOCKER_PATTERNS = {
    "approval needed": r"\b(?:(?:need|needs|awaiting|pending|waiting for)\s+(?:\w+\s+){0,3}(?:approval|approve|review)|(?:approval|review)\s+(?:(?:is|still)\s+)?(?:needed|required|pending))\b",
    "blocked": r"\b(?:blocked|stuck|waiting)\b",
    "ownership unclear": r"\b(?:(?:ownership|owner)\s+(?:is\s+)?(?:unclear|missing|unassigned)|unclear\s+(?:owner|ownership)|(?:need|needs|missing|no|without)\s+(?:\w+\s+){0,3}owner)\b",
}

RESOLVED_PATTERNS = {
    "approval needed": r"\b(?:(?:approval|review)\s+(?:is\s+)?(?:received|complete|completed|granted)|approved|no\s+(?:approval|review)\s+(?:needed|required))\b",
    "blocked": r"\b(?:no longer (?:blocked|stuck|waiting)|not blocked|unblocked|(?:blocker|issue)\s+(?:is\s+)?resolved)\b",
    "ownership unclear": r"\b(?:(?:ownership|owner)\s+(?:is\s+)?(?:clear|assigned|confirmed)|no\s+(?:ownership|owner)\s+issue)\b",
}

COMMERCIAL_KEYWORDS = {
    "conversion or pipeline impact": {"conversion", "conversions", "signup", "signups", "demo", "demos", "pipeline", "pipelines", "trial", "trials", "revenue"},
    "customer delivery impact": {"customer", "customers", "migration", "migrations", "support", "launch", "launches"},
    "marketing distribution impact": {"campaign", "campaigns"},
}


def analyze_messages(
    messages: list[dict[str, str]],
    *,
    expected_people: list[str] | None = None,
) -> dict[str, Any]:
    people: dict[str, dict[str, Any]] = defaultdict(_empty_person)
    for message in messages:
        person = message["person"]
        text = message["text"]
        lowered = text.lower()
        people[person]["messages"].append(text)
        people[person]["workstreams"].update(_matches(lowered, WORKSTREAM_KEYWORDS))
        for label, evidence in _blocker_mentions(text).items():
            people[person]["blockers"].add(label)
            people[person]["blocker_evidence"].setdefault(label, []).extend(evidence)
        people[person]["commercial_relevance"].update(_matches(lowered, COMMERCIAL_KEYWORDS))
        people[person]["evidence"].append(text)

    expected = sorted(people.keys()) if expected_people is None else expected_people
    visibility_gaps = [
        f"{person} had no visible update in the review window."
        for person in expected
        if person not in people
    ]

    return {
        "people": {
            person: {
                "messages": data["messages"],
                "workstreams": sorted(data["workstreams"]),
                "blockers": sorted(data["blockers"]),
                "commercial_relevance": sorted(data["commercial_relevance"]),
                "evidence": data["evidence"],
                "blocker_evidence": data["blocker_evidence"],
            }
            for person, data in sorted(people.items())
        },
        "visibility_gaps": visibility_gaps,
        "message_count": len(messages),
        "analysis_method": "deterministic_rules",
        "needs_human_review": True,
    }


def _empty_person() -> dict[str, Any]:
    return {
        "messages": [],
        "workstreams": set(),
        "blockers": set(),
        "commercial_relevance": set(),
        "evidence": [],
        "blocker_evidence": {},
    }


def _matches(text: str, groups: dict[str, set[str]]) -> set[str]:
    matches: set[str] = set()
    for label, keywords in groups.items():
        if any(re.search(r"\b" + re.escape(keyword) + r"\b", text) for keyword in keywords):
            matches.add(label)
    return matches


def _blocker_mentions(text: str) -> dict[str, list[str]]:
    """Find explicit concerns; do not infer current project state from chat."""
    found: dict[str, list[str]] = {}
    split = (
        r"[.!?;]+|\b(?:but|however)\b|"
        r",\s*(?:and\s+)?(?=(?:please|we|they|i|need|needs|waiting|approval|ownership|owner)\b)|"
        r"\band\s+(?=(?:please|we|they|i|need|needs|waiting|approval|ownership|owner)\b)"
    )
    for clause in re.split(split, text, flags=re.IGNORECASE):
        clause = clause.strip()
        lowered = clause.lower().replace("’", "'")
        for label, pattern in BLOCKER_PATTERNS.items():
            if re.search(pattern, lowered) and not re.search(RESOLVED_PATTERNS[label], lowered):
                found.setdefault(label, []).append(clause)
    return found
