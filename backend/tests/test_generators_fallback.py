"""カード/ブリーフ生成の API キーなしフォールバックの検証

ANTHROPIC_API_KEY なしでも全生成機能が動くことはこのプロダクトの
重要な設計制約 (CLAUDE.md 参照)。このテストが落ちる = 制約が壊れた。
"""

from src.intel.card_generator import build_intel_card
from src.intel.brief_generator import build_daily_brief


def _news(title: str) -> dict:
    return {
        "title": title,
        "url": "https://example.com/a",
        "publisher": "Example",
        "summary": "概要テキスト",
        "access_status": "full",
        "category": "ip_content",
        "importance": "A",
    }


def test_build_intel_card_without_api_key():
    card = build_intel_card(_news("テストニュース"), date="2026-07-12")
    # 必須フィールドが揃っている (フロント intel-types.ts と対応)
    for key in ("id", "date", "title", "one_liner", "category", "importance",
                "fact", "interpretation", "insight", "actions", "tags",
                "sources", "confidence"):
        assert key in card, f"missing field: {key}"
    assert card["date"] == "2026-07-12"
    assert card["category"] == "ip_content"
    assert card["importance"] == "A"
    assert card["sources"][0]["url"] == "https://example.com/a"
    assert isinstance(card["insight"].get("business_opportunity"), list)


def test_build_daily_brief_without_api_key():
    cards = [
        build_intel_card(_news("ニュース1"), date="2026-07-12"),
        build_intel_card(_news("ニュース2"), date="2026-07-12"),
    ]
    brief = build_daily_brief("2026-07-12", cards)
    for key in ("date", "brief_type", "title", "top_topics",
                "executive_summary", "sections", "generated_at"):
        assert key in brief, f"missing field: {key}"
    assert brief["brief_type"] == "daily"
    assert len(brief["top_topics"]) == 2
    assert brief["executive_summary"]
    headings = [s["heading"] for s in brief["sections"]]
    assert any("トピックス" in h for h in headings)


def test_build_daily_brief_with_no_cards():
    brief = build_daily_brief("2026-07-12", [])
    assert brief["date"] == "2026-07-12"
