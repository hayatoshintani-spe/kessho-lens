"""
pytest 共通設定。

重要: storage.DATA_DIR を tmp_path に差し替えることで、
リポジトリの data/*.json (シードデータ) をテストが汚さないようにする。
外部 API (Anthropic / Notion / Resend) のキーは削除し、
全テストがフォールバック実装のみで完結するようにする。
"""

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

EXTERNAL_KEYS = [
    "ANTHROPIC_API_KEY",
    "NOTION_API_KEY",
    "NOTION_CARDS_DB_ID",
    "NOTION_BRIEFS_DB_ID",
    "RESEND_API_KEY",
    "CRON_SECRET",
    "DAILY_BRIEF_MAX_RUNS_PER_DAY",
    "INTEL_AUTO_INGEST",
]


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """各テストを一時データディレクトリ + 外部キーなしの環境で実行する"""
    from src.data import storage

    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    for key in EXTERNAL_KEYS:
        monkeypatch.delenv(key, raising=False)
    yield tmp_path


@pytest.fixture
def client():
    """daily-brief の実行状態をリセットした TestClient"""
    from fastapi.testclient import TestClient
    from main import app
    from api import intel

    intel._DAILY_BRIEF_RUN_TIMESTAMPS.clear()
    intel._DAILY_BRIEF_STATE.update({
        "state": "idle",
        "date": None,
        "started_at": 0.0,
        "finished_at": 0.0,
        "message": "",
        "ingest": None,
        "email": None,
        "notion_cards": None,
        "notion_brief": None,
    })
    with TestClient(app) as c:
        yield c
