import pytest

from src.company_chat.analyze import analyze_messages
from src.company_chat.founder_voice import FounderVoice
from src.company_chat.normalize import normalize_messages
from src.company_chat.render import render_daily_brief


def analyze(text):
    return analyze_messages(normalize_messages([{"user": "Avery", "text": text}]))


@pytest.mark.parametrize("text", [
    "No longer blocked. Approval received. Ownership is clear.",
    "Owner assigned. Review completed.",
    "I reviewed the blog post.",
    "The trial went well; no approval needed.",
])
def test_resolved_or_incidental_language_is_not_an_open_concern(text):
    assert analyze(text)["people"]["Avery"]["blockers"] == []


def test_separate_active_issue_survives_a_resolved_clause():
    result = analyze("Not blocked on migration, but waiting for customer approval.")
    assert result["people"]["Avery"]["blockers"] == ["approval needed", "blocked"]


def test_resolved_approval_does_not_hide_an_independent_request():
    result = analyze("Approval received for pricing, need approval for the launch email")
    assert result["people"]["Avery"]["blockers"] == ["approval needed"]
    assert result["people"]["Avery"]["blocker_evidence"]["approval needed"] == ["need approval for the launch email"]


@pytest.mark.parametrize("text", [
    "Approval received for pricing, still need approval for the launch email.",
    "Waiting on legal approval.",
    "Can you approve the launch?",
])
def test_pending_approval_phrasings_remain_visible(text):
    assert "approval needed" in analyze(text)["people"]["Avery"]["blockers"]


def test_explicit_approve_verb_is_detected():
    assert "approval needed" in analyze("Need someone to approve the conversion copy")["people"]["Avery"]["blockers"]


def test_plural_customer_and_deal_terms_keep_their_commercial_meaning():
    result = analyze("Customers signed new deals")["people"]["Avery"]
    assert "sales" in result["workstreams"]
    assert "customer delivery impact" in result["commercial_relevance"]


def test_blocker_is_rendered_with_its_actual_evidence():
    messages = normalize_messages([
        {"user": "Avery", "text": "Published the pricing page."},
        {"user": "Avery", "text": "Blocked on customer migration."},
    ])
    result = analyze_messages(messages)
    evidence = result["people"]["Avery"]["blocker_evidence"]
    assert evidence["blocked"] == ["Blocked on customer migration"]
    brief = render_daily_brief(result, FounderVoice.from_file("docs/founder-voice.md"))
    assert "Concern evidence (blocked): Blocked on customer migration" in brief
    assert "not verified current status" in brief


def test_substrings_do_not_create_workstreams():
    assert analyze("Developing a triality theorem.")["people"]["Avery"]["workstreams"] == []


def test_empty_updates_preserve_expected_person_visibility_gap():
    items = normalize_messages([{"user": "Avery", "text": " "}])
    assert analyze_messages(items, expected_people=["Avery"])["visibility_gaps"]


def test_voice_profile_changes_rendered_guidance():
    result = analyze("Published the pricing page.")
    voice = FounderVoice(principles=("Use brief evidence-led notes.",))
    assert voice.opening() in render_daily_brief(result, voice)


@pytest.mark.parametrize("raw", [{}, [None], [{"text": {"nested": "unexpected"}}]])
def test_malformed_messages_are_rejected(raw):
    with pytest.raises(ValueError):
        normalize_messages(raw)
