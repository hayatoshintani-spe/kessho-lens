"""
JSONファイルベースのストレージモジュール
/data/ ディレクトリにJSONファイルで全データを保存する
"""

import json
import os
import asyncio
import aiofiles
from pathlib import Path
from typing import Any, List, Dict, Optional
from datetime import datetime
import threading

# データディレクトリのパス（リポジトリルートの /data/）
_BACKEND_DIR = Path(__file__).parent.parent.parent
_REPO_ROOT = _BACKEND_DIR.parent
DATA_DIR = _REPO_ROOT / "data"

# ファイルロック用（同時書き込みを防ぐ）
_file_locks: Dict[str, threading.Lock] = {}
_locks_lock = threading.Lock()


def _get_file_lock(filename: str) -> threading.Lock:
    """ファイルごとのロックを取得または作成"""
    with _locks_lock:
        if filename not in _file_locks:
            _file_locks[filename] = threading.Lock()
        return _file_locks[filename]


def ensure_data_dir():
    """データディレクトリと初期JSONファイルを作成"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 各JSONファイルを初期化（存在しない場合のみ）
    initial_files = {
        "portfolios.json": {},
        "trades.json": [],
        "meetings.json": [],
        "memories.json": {},
        "daily_reports.json": [],
        "discovery.json": [],
    }

    for filename, initial_data in initial_files.items():
        filepath = DATA_DIR / filename
        if not filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)


def read_json(filename: str) -> Any:
    """JSONファイルを同期的に読み込む"""
    ensure_data_dir()
    filepath = DATA_DIR / filename
    lock = _get_file_lock(filename)

    with lock:
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


def write_json(filename: str, data: Any) -> None:
    """JSONファイルに同期的に書き込む"""
    ensure_data_dir()
    filepath = DATA_DIR / filename
    lock = _get_file_lock(filename)

    with lock:
        # 一時ファイルに書いてからリネーム（原子的書き込み）
        tmp_path = filepath.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        tmp_path.replace(filepath)


async def read_json_async(filename: str) -> Any:
    """JSONファイルを非同期で読み込む"""
    ensure_data_dir()
    filepath = DATA_DIR / filename

    if not filepath.exists():
        return None

    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
        content = await f.read()
        return json.loads(content)


async def write_json_async(filename: str, data: Any) -> None:
    """JSONファイルに非同期で書き込む"""
    ensure_data_dir()
    filepath = DATA_DIR / filename
    tmp_path = filepath.with_suffix(".tmp")

    async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    # リネーム（同期）
    tmp_path.replace(filepath)


class Storage:
    """ストレージ操作の高レベルインターフェース"""

    # ポートフォリオ操作
    @staticmethod
    def get_all_portfolios() -> Dict:
        """全エージェントのポートフォリオを取得"""
        data = read_json("portfolios.json")
        return data or {}

    @staticmethod
    def get_portfolio(agent_id: str) -> Optional[Dict]:
        """特定エージェントのポートフォリオを取得"""
        portfolios = Storage.get_all_portfolios()
        return portfolios.get(agent_id)

    @staticmethod
    def save_portfolio(agent_id: str, portfolio: Dict) -> None:
        """エージェントのポートフォリオを保存"""
        portfolios = Storage.get_all_portfolios()
        portfolios[agent_id] = portfolio
        write_json("portfolios.json", portfolios)

    # 取引履歴操作
    @staticmethod
    def get_trades(agent_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """取引履歴を取得"""
        trades = read_json("trades.json") or []
        if agent_id:
            trades = [t for t in trades if t.get("agent_id") == agent_id]
        return trades[-limit:]

    @staticmethod
    def append_trade(trade: Dict) -> None:
        """取引記録を追加"""
        trades = read_json("trades.json") or []
        trades.append(trade)
        write_json("trades.json", trades)

    # ミーティングログ操作
    @staticmethod
    def get_meetings(limit: int = 30) -> List[Dict]:
        """ミーティングログ一覧を取得"""
        meetings = read_json("meetings.json") or []
        return sorted(meetings, key=lambda m: m.get("date", ""), reverse=True)[:limit]

    @staticmethod
    def get_meeting(date: str) -> Optional[Dict]:
        """特定日付のミーティングログを取得"""
        meetings = read_json("meetings.json") or []
        for meeting in meetings:
            if meeting.get("date") == date:
                return meeting
        return None

    @staticmethod
    def save_meeting(meeting: Dict) -> None:
        """ミーティングログを保存（同じ日付は上書き）"""
        meetings = read_json("meetings.json") or []
        date = meeting.get("date")
        # 同じ日付のミーティングを置き換え
        meetings = [m for m in meetings if m.get("date") != date]
        meetings.append(meeting)
        write_json("meetings.json", meetings)

    # エージェントメモリ操作
    @staticmethod
    def get_memories(agent_id: Optional[str] = None) -> Any:
        """エージェントのメモリを取得"""
        memories = read_json("memories.json") or {}
        if agent_id:
            return memories.get(agent_id, {})
        return memories

    @staticmethod
    def save_memory(agent_id: str, memory: Dict) -> None:
        """エージェントのメモリを保存"""
        memories = read_json("memories.json") or {}
        memories[agent_id] = memory
        write_json("memories.json", memories)

    # 日次レポート操作
    @staticmethod
    def get_reports(limit: int = 30) -> List[Dict]:
        """日次レポート一覧を取得"""
        reports = read_json("daily_reports.json") or []
        return sorted(reports, key=lambda r: r.get("date", ""), reverse=True)[:limit]

    @staticmethod
    def get_report(date: str) -> Optional[Dict]:
        """特定日付のレポートを取得"""
        reports = read_json("daily_reports.json") or []
        for report in reports:
            if report.get("date") == date:
                return report
        return None

    @staticmethod
    def save_report(report: Dict) -> None:
        """日次レポートを保存（同じ日付は上書き）"""
        reports = read_json("daily_reports.json") or []
        date = report.get("date")
        reports = [r for r in reports if r.get("date") != date]
        reports.append(report)
        write_json("daily_reports.json", reports)

    # 発見ログ操作
    @staticmethod
    def get_discoveries(agent_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """発見ログを取得"""
        discoveries = read_json("discovery.json") or []
        if agent_id:
            discoveries = [d for d in discoveries if d.get("agent_id") == agent_id]
        return sorted(discoveries, key=lambda d: d.get("date", ""), reverse=True)[:limit]

    @staticmethod
    def append_discovery(discovery: Dict) -> None:
        """発見ログを追加"""
        discoveries = read_json("discovery.json") or []
        discoveries.append(discovery)
        write_json("discovery.json", discoveries)

    @staticmethod
    def save_discoveries(discoveries: List[Dict]) -> None:
        """発見ログをまとめて保存（追記）"""
        existing = read_json("discovery.json") or []
        existing.extend(discoveries)
        write_json("discovery.json", existing)
