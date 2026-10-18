# Company Chat Founder Brief - Public Showcase

This repo is a public showcase of a company-chat operating layer. It takes Slack-like team updates, extracts what each person appears to be working on, identifies blockers and commercial relevance, and renders founder-ready daily briefs and weekly meeting talking points in a consistent founder voice.

The purpose is simple: help a founder understand what is happening across the team without reading every chat message or walking into meetings cold.

## Executable Scope

This offline sample uses local JSON, deterministic rules, and Markdown templates. It has no live Slack connection, model inference, or scheduling.

- Topics match whole words.
- Explicit concerns exclude common resolved phrases such as "no longer blocked," "approval received," and "ownership is clear."
- Every concern includes the clause that produced it.
- Concern flags are mentions to review, not verified current project state. Chronology, unrelated threads, sarcasm, and conflicting updates are not reconciled.
- The voice profile supplies rendering guidance rather than model-based voice adaptation.
- Missing updates mean missing visibility, not poor performance.

Use Python 3.10+. Install the test dependency with `python3 -m pip install -r requirements.txt`.

## What This Demonstrates

- Chat context normalization from Slack-like exports.
- Evidence-first team update analysis.
- Per-person workstream, blocker, and commercial-read extraction.
- Visibility gaps when the team has not posted enough evidence.
- Founder voice grounding, similar to a reusable `soul.md`.
- Daily founder brief generation.
- Weekly meeting talking-point generation.
- Reference architecture with fake data only.

## Why This Matters

In low-communication companies, the founder often has to reconstruct reality from scattered updates. This system improves the operating rhythm by turning team chat into:

- who moved work forward
- who needs help
- where ownership is unclear
- what has customer, revenue, sales, BD, or marketing impact
- what to ask in weekly meetings
- what cannot be known from the visible evidence

It does not invent hidden work. If the chat has low signal, the system says that directly.

## Code Review Path

The core code path is intentionally small:

```text
examples/slack-messages.json
  -> normalize_messages
  -> analyze_messages
  -> FounderVoice
  -> render_daily_brief / render_weekly_meeting_prep
```

Files to inspect:

- `src/company_chat/normalize.py`
- `src/company_chat/analyze.py`
- `src/company_chat/founder_voice.py`
- `src/company_chat/render.py`
- `tests/test_company_chat.py`

## Safe Local Run

```bash
python3 -m pytest
python3 -m src.company_chat.cli --mode daily
python3 -m src.company_chat.cli --mode weekly
```

## Example Outputs

- `examples/founder-brief.md`
- `examples/weekly-meeting-prep.md`

## Public Safety

This repo contains no private Slack data, employee records, API keys, tokens, webhook URLs, or real channel IDs. All sample messages and names are fake.
