"""改革ダッシュボード API (/api/intel/reform/*) の検証"""


def test_actions_crud_flow(client):
    # 初期状態は空
    res = client.get("/api/intel/reform/actions")
    assert res.status_code == 200
    assert res.json()["count"] == 0

    # 作成
    res = client.post("/api/intel/reform/actions", json={
        "title": "テストアクション",
        "owner": "経営企画",
        "deadline": "2026-08-01",
        "priority": "high",
        "memo": "メモ",
    })
    assert res.status_code == 200
    action = res.json()["action"]
    assert action["id"].startswith("act_")
    assert action["status"] == "not_started"
    assert action["created_at"] == action["updated_at"]

    # 更新 (ステータス)
    res = client.patch(f"/api/intel/reform/actions/{action['id']}",
                       json={"status": "in_progress"})
    assert res.status_code == 200
    assert res.json()["action"]["status"] == "in_progress"
    # 他フィールドは保持される
    assert res.json()["action"]["memo"] == "メモ"

    # 削除
    res = client.delete(f"/api/intel/reform/actions/{action['id']}")
    assert res.status_code == 200
    assert client.get("/api/intel/reform/actions").json()["count"] == 0


def test_action_invalid_enum_rejected(client):
    res = client.post("/api/intel/reform/actions", json={
        "title": "x", "owner": "y", "deadline": "2026-08-01", "priority": "bogus",
    })
    assert res.status_code == 422

    res = client.post("/api/intel/reform/actions", json={
        "title": "x", "owner": "y", "deadline": "2026-08-01",
    })
    aid = res.json()["action"]["id"]
    assert client.patch(f"/api/intel/reform/actions/{aid}",
                        json={"status": "bogus"}).status_code == 422


def test_action_not_found(client):
    assert client.patch("/api/intel/reform/actions/act_none",
                        json={"status": "done"}).status_code == 404
    assert client.delete("/api/intel/reform/actions/act_none").status_code == 404


def test_action_empty_title_rejected(client):
    res = client.post("/api/intel/reform/actions", json={
        "title": "   ", "owner": "y", "deadline": "2026-08-01",
    })
    assert res.status_code == 422


def test_kpi_upsert_and_list(client):
    res = client.put("/api/intel/reform/kpis/kpi_revenue", json={
        "value": 100, "target": 200, "period": "2026-Q2", "status": "at_risk",
    })
    assert res.status_code == 200

    # 同じ kpi_id への PUT は上書き
    res = client.put("/api/intel/reform/kpis/kpi_revenue", json={
        "value": 150, "period": "2026-Q3", "status": "on_track",
    })
    assert res.status_code == 200

    snaps = client.get("/api/intel/reform/kpis").json()["snapshots"]
    assert len(snaps) == 1
    assert snaps[0]["value"] == 150
    assert snaps[0]["period"] == "2026-Q3"
    # target 未指定の upsert では target は含まれない (完全置換)
    assert "target" not in snaps[0]


def test_kpi_invalid_status_rejected(client):
    res = client.put("/api/intel/reform/kpis/k1", json={
        "value": 1, "period": "2026-Q1", "status": "bogus",
    })
    assert res.status_code == 422


def test_agenda_save_and_get(client):
    assert client.get("/api/intel/reform/agenda").json()["agenda"] is None

    item = {
        "id": "agd_1", "rank": 1, "topic": "論点A", "week_of": "2026-07-13",
    }
    res = client.post("/api/intel/reform/agenda", json={
        "week_of": "2026-07-13", "items": [item], "source": "signals",
    })
    assert res.status_code == 200

    # 最新取得
    agenda = client.get("/api/intel/reform/agenda").json()["agenda"]
    assert agenda["week_of"] == "2026-07-13"
    assert agenda["items"][0]["topic"] == "論点A"
    assert agenda["source"] == "signals"

    # week_of 指定取得 / 存在しない週
    assert client.get(
        "/api/intel/reform/agenda?week_of=2026-07-13"
    ).json()["agenda"] is not None
    assert client.get(
        "/api/intel/reform/agenda?week_of=2000-01-01"
    ).json()["agenda"] is None
