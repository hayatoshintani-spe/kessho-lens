"""cron 認証と暴走課金ガードの検証(外部 API なしで完結)"""

import os


def test_cron_requires_secret_configured(client, monkeypatch):
    monkeypatch.delenv("CRON_SECRET", raising=False)
    res = client.post("/api/intel/cron/daily-brief")
    assert res.status_code == 500  # サーバー側未設定はエラーとして表面化


def test_cron_rejects_wrong_token(client, monkeypatch):
    monkeypatch.setenv("CRON_SECRET", "correct")
    res = client.post(
        "/api/intel/cron/daily-brief",
        headers={"Authorization": "Bearer wrong"},
    )
    assert res.status_code == 401
    # ヘッダなしも拒否
    assert client.post("/api/intel/cron/daily-brief").status_code == 401


def test_cron_runs_and_skips_without_cards(client, monkeypatch):
    """カードなし + 自動取得オフなら Brief 生成を安全にスキップする"""
    monkeypatch.setenv("CRON_SECRET", "s")
    monkeypatch.setenv("INTEL_AUTO_INGEST", "0")

    res = client.post(
        "/api/intel/cron/daily-brief",
        headers={"Authorization": "Bearer s"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "started"
    assert body["daily_limit"] == 5  # 既定値

    # TestClient は BackgroundTask 完了後に返るため、状態は確定している
    status = client.get("/api/intel/cron/status").json()
    assert status["state"] == "skipped"


def test_cron_rate_limit(client, monkeypatch):
    """24h 実行上限を超えたら 429(Anthropic 暴走課金防止)"""
    monkeypatch.setenv("CRON_SECRET", "s")
    monkeypatch.setenv("INTEL_AUTO_INGEST", "0")
    monkeypatch.setenv("DAILY_BRIEF_MAX_RUNS_PER_DAY", "2")
    headers = {"Authorization": "Bearer s"}

    assert client.post("/api/intel/cron/daily-brief", headers=headers).status_code == 200
    assert client.post("/api/intel/cron/daily-brief", headers=headers).status_code == 200
    res = client.post("/api/intel/cron/daily-brief", headers=headers)
    assert res.status_code == 429


def test_cron_ingest_requires_auth(client, monkeypatch):
    monkeypatch.setenv("CRON_SECRET", "s")
    res = client.post(
        "/api/intel/cron/ingest",
        headers={"Authorization": "Bearer wrong"},
    )
    assert res.status_code == 401
