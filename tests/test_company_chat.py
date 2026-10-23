from src.company_chat.analyze import analyze_messages
from src.company_chat.founder_voice import FounderVoice
from src.company_chat.normalize import normalize_messages
from src.company_chat.render import render_daily_brief, render_weekly_meeting_prep


def test_normalize_messages_keeps_public_safe_fields_only():
    raw = [
        {
            "user": "Avery",
            "text": "Published the landing-page update; next step is measuring demo clicks.",
            "ts": "2026-05-06T10:15:00-04:00",
            "channel": "company-chat",
            "private_email": "avery@example.invalid",
        }
    ]

    normalized = normalize_messages(raw)

    assert normalized == [
        {
            "person": "Avery",
            "text": "Published the landing-page update; next step is measuring demo clicks.",
            "timestamp": "2026-05-06T10:15:00-04:00",
            "channel": "company-chat",
        }
    ]


def test_analyze_messages_groups_people_and_visibility_gaps():
    messages = normalize_messages(
        [
            {
                "user": "Avery",
                "text": "Published the pricing page. Need approval on the conversion copy before email goes out.",
                "ts": "2026-05-06T10:15:00-04:00",
                "channel": "company-chat",
            },
            {
                "user": "Jordan",
                "text": "Working on support queue cleanup.",
                "ts": "2026-05-06T11:30:00-04:00",
                "channel": "company-chat",
            },
        ]
    )

    analysis = analyze_messages(messages, expected_people=["Avery", "Jordan", "Morgan"])

    assert analysis["people"]["Avery"]["workstreams"] == ["marketing"]
    assert analysis["people"]["Avery"]["blockers"] == ["approval needed"]
    assert analysis["people"]["Avery"]["commercial_relevance"] == ["conversion or pipeline impact"]
    assert analysis["people"]["Jordan"]["workstreams"] == ["operations"]
    assert analysis["visibility_gaps"] == ["Morgan had no visible update in the review window."]


def test_render_daily_brief_uses_founder_voice_and_sections():
    messages = normalize_messages(
        [
            {
                "user": "Avery",
                "text": "Published the pricing page. Need approval on the conversion copy before email goes out.",
                "ts": "2026-05-06T10:15:00-04:00",
                "channel": "company-chat",
            }
        ]
    )
    analysis = analyze_messages(messages, expected_people=["Avery"])
    voice = FounderVoice.from_file("docs/founder-voice.md")

    brief = render_daily_brief(analysis, voice)

    assert "Company Chat Founder Brief" in brief
    assert "Bottom line" in brief
    assert "Avery" in brief
    assert "approval needed" in brief
    assert voice.principles[0] in brief


def test_render_weekly_meeting_prep_creates_talking_points():
    messages = normalize_messages(
        [
            {
                "user": "Avery",
                "text": "100 trial signups came from the launch post. Need next step owner.",
                "ts": "2026-05-06T10:15:00-04:00",
                "channel": "company-chat",
            },
            {
                "user": "Jordan",
                "text": "Blocked on customer migration because ownership is unclear.",
                "ts": "2026-05-06T11:30:00-04:00",
                "channel": "company-chat",
            },
        ]
    )
    analysis = analyze_messages(messages, expected_people=["Avery", "Jordan"])
    voice = FounderVoice.from_file("docs/founder-voice.md")

    prep = render_weekly_meeting_prep(analysis, voice)

    assert "Weekly Meeting Prep" in prep
    assert "Talking points" in prep
    assert "Ask Avery" in prep
    assert "Ask Jordan" in prep
    assert "commercial impact" in prep
