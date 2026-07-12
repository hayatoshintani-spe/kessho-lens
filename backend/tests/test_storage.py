"""Storage クラスの JSON 永続化の検証"""

from src.data.storage import Storage


def _card(card_id: str, date: str, importance: str = "B") -> dict:
    return {"id": card_id, "date": date, "title": f"t-{card_id}", "importance": importance}


def test_card_roundtrip_and_upsert():
    Storage.save_intel_card(_card("c1", "2026-07-10"))
    Storage.save_intel_card(_card("c2", "2026-07-11"))
    assert Storage.get_intel_card("c1")["title"] == "t-c1"

    # 同一 ID は上書き (重複しない)
    updated = _card("c1", "2026-07-10")
    updated["title"] = "updated"
    Storage.save_intel_card(updated)
    cards = Storage.get_intel_cards()
    assert len(cards) == 2
    assert Storage.get_intel_card("c1")["title"] == "updated"

    # 日付降順ソート
    assert cards[0]["id"] == "c2"


def test_cards_filter_by_category_and_importance():
    a = _card("c1", "2026-07-10", importance="A")
    a["category"] = "ip_content"
    b = _card("c2", "2026-07-10", importance="C")
    b["category"] = "ai_agent"
    Storage.save_intel_card(a)
    Storage.save_intel_card(b)
    assert [c["id"] for c in Storage.get_intel_cards(category="ip_content")] == ["c1"]
    assert [c["id"] for c in Storage.get_intel_cards(importance="C")] == ["c2"]


def test_brief_upsert_by_date_and_type():
    Storage.save_intel_brief({"date": "2026-07-12", "brief_type": "daily", "title": "v1"})
    Storage.save_intel_brief({"date": "2026-07-12", "brief_type": "daily", "title": "v2"})
    Storage.save_intel_brief({"date": "2026-07-12", "brief_type": "weekly", "title": "w1"})
    assert Storage.get_intel_brief("2026-07-12", "daily")["title"] == "v2"
    assert Storage.get_intel_brief("2026-07-12", "weekly")["title"] == "w1"
    assert len(Storage.get_intel_briefs()) == 2


def test_reform_action_save_and_delete():
    Storage.save_reform_action({"id": "a1", "title": "x", "deadline": "2026-08-01"})
    Storage.save_reform_action({"id": "a2", "title": "y", "deadline": "2026-07-01"})
    # 期限昇順で返る
    assert [a["id"] for a in Storage.get_reform_actions()] == ["a2", "a1"]
    assert Storage.delete_reform_action("a1") is True
    assert Storage.delete_reform_action("a1") is False
    assert Storage.get_reform_action("a1") is None


def test_kpi_snapshot_upsert_keeps_one_per_id():
    Storage.save_kpi_snapshot({"kpi_id": "k1", "value": 1, "period": "2026-Q1"})
    Storage.save_kpi_snapshot({"kpi_id": "k1", "value": 2, "period": "2026-Q2"})
    Storage.save_kpi_snapshot({"kpi_id": "k2", "value": 9, "period": "2026-Q1"})
    snaps = Storage.get_kpi_snapshots()
    assert len(snaps) == 2
    k1 = [s for s in snaps if s["kpi_id"] == "k1"][0]
    assert k1["value"] == 2
    assert k1["period"] == "2026-Q2"


def test_agenda_upsert_by_week_and_latest():
    Storage.save_reform_agenda({"week_of": "2026-07-06", "items": [1]})
    Storage.save_reform_agenda({"week_of": "2026-07-13", "items": [2]})
    Storage.save_reform_agenda({"week_of": "2026-07-06", "items": [3]})
    assert len(Storage.get_reform_agendas()) == 2
    # 未指定は最新週
    assert Storage.get_reform_agenda()["week_of"] == "2026-07-13"
    # week_of 指定は upsert 後の中身
    assert Storage.get_reform_agenda("2026-07-06")["items"] == [3]
    assert Storage.get_reform_agenda("2000-01-01") is None
