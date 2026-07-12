"""
JSONファイルベースのストレージモジュール
/data/ ディレクトリに各種JSONファイルで全データを保存する
"""

import json
import aiofiles
from pathlib import Path
from typing import Any, Callable, List, Dict, Optional
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

    initial_files = {
        "intel_cards.json": [],
        "intel_briefs.json": [],
        "intel_council.json": [],
        "intel_watchlist.json": [],
        "reform_actions.json": [],
        "reform_kpis.json": [],
        "reform_agendas.json": [],
    }

    for filename, initial_data in initial_files.items():
        filepath = DATA_DIR / filename
        if not filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)


def _read_json_unlocked(filepath: Path) -> Any:
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_unlocked(filepath: Path, data: Any) -> None:
    tmp_path = filepath.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    tmp_path.replace(filepath)


def read_json(filename: str) -> Any:
    """JSONファイルを同期的に読み込む"""
    ensure_data_dir()
    with _get_file_lock(filename):
        return _read_json_unlocked(DATA_DIR / filename)


def write_json(filename: str, data: Any) -> None:
    """JSONファイルに同期的に書き込む（原子的書き込み）"""
    ensure_data_dir()
    with _get_file_lock(filename):
        _write_json_unlocked(DATA_DIR / filename, data)


def update_json(filename: str, mutate: Callable[[Any], Any]) -> None:
    """ロックを保持したまま read → 変更 → write を行う。
    read/write を別ロックで行うと read-modify-write が競合し得るため、
    リスト更新系は必ずこちらを使う。
    """
    ensure_data_dir()
    filepath = DATA_DIR / filename
    with _get_file_lock(filename):
        data = _read_json_unlocked(filepath)
        _write_json_unlocked(filepath, mutate(data))


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

    tmp_path.replace(filepath)


class Storage:
    """ストレージ操作の高レベルインターフェース"""

    # ─── Intelligence Brief: Cards ──────────────────────────────────────

    @staticmethod
    def get_intel_cards(
        category: Optional[str] = None,
        importance: Optional[str] = None,
        limit: int = 200,
    ) -> List[Dict]:
        cards = read_json("intel_cards.json") or []
        if category:
            cards = [c for c in cards if c.get("category") == category]
        if importance:
            cards = [c for c in cards if c.get("importance") == importance]
        cards.sort(key=lambda c: c.get("date", ""), reverse=True)
        return cards[:limit]

    @staticmethod
    def get_intel_card(card_id: str) -> Optional[Dict]:
        cards = read_json("intel_cards.json") or []
        for c in cards:
            if c.get("id") == card_id:
                return c
        return None

    @staticmethod
    def save_intel_card(card: Dict) -> None:
        cards = read_json("intel_cards.json") or []
        card_id = card.get("id")
        cards = [c for c in cards if c.get("id") != card_id]
        cards.append(card)
        write_json("intel_cards.json", cards)

    @staticmethod
    def save_intel_cards(cards: List[Dict]) -> None:
        """カードリストを上書き保存（シード用）"""
        write_json("intel_cards.json", cards)

    # ─── Intelligence Brief: Briefs ─────────────────────────────────────

    @staticmethod
    def get_intel_briefs(brief_type: Optional[str] = None, limit: int = 60) -> List[Dict]:
        briefs = read_json("intel_briefs.json") or []
        if brief_type:
            briefs = [b for b in briefs if b.get("brief_type") == brief_type]
        briefs.sort(key=lambda b: b.get("date", ""), reverse=True)
        return briefs[:limit]

    @staticmethod
    def get_intel_brief(date: str, brief_type: str = "daily") -> Optional[Dict]:
        briefs = read_json("intel_briefs.json") or []
        for b in briefs:
            if b.get("date") == date and b.get("brief_type") == brief_type:
                return b
        return None

    @staticmethod
    def save_intel_brief(brief: Dict) -> None:
        briefs = read_json("intel_briefs.json") or []
        date = brief.get("date")
        btype = brief.get("brief_type", "daily")
        briefs = [
            b for b in briefs
            if not (b.get("date") == date and b.get("brief_type") == btype)
        ]
        briefs.append(brief)
        write_json("intel_briefs.json", briefs)

    # ─── Intelligence Brief: Council Sessions ──────────────────────────

    @staticmethod
    def get_council_sessions(limit: int = 30) -> List[Dict]:
        sessions = read_json("intel_council.json") or []
        sessions.sort(key=lambda s: s.get("date", ""), reverse=True)
        return sessions[:limit]

    @staticmethod
    def get_council_session(session_id: str) -> Optional[Dict]:
        sessions = read_json("intel_council.json") or []
        for s in sessions:
            if s.get("id") == session_id:
                return s
        return None

    @staticmethod
    def save_council_session(session: Dict) -> None:
        sessions = read_json("intel_council.json") or []
        sid = session.get("id")
        sessions = [s for s in sessions if s.get("id") != sid]
        sessions.append(session)
        write_json("intel_council.json", sessions)

    # ─── Intelligence Brief: Watchlist ─────────────────────────────────

    @staticmethod
    def get_watchlists() -> List[Dict]:
        return read_json("intel_watchlist.json") or []

    @staticmethod
    def save_watchlists(watchlists: List[Dict]) -> None:
        write_json("intel_watchlist.json", watchlists)

    # ─── Reform: 共通 upsert ────────────────────────────────────────────

    @staticmethod
    def _upsert_by_key(filename: str, key_field: str, item: Dict) -> None:
        """key_field の一致する既存要素を置き換えて追記(ロック保持で原子的)"""
        update_json(
            filename,
            lambda items: [
                i for i in (items or []) if i.get(key_field) != item.get(key_field)
            ] + [item],
        )

    # ─── Reform: Actions ────────────────────────────────────────────────

    @staticmethod
    def get_reform_actions() -> List[Dict]:
        actions = read_json("reform_actions.json") or []
        actions.sort(key=lambda a: a.get("deadline", ""))
        return actions

    @staticmethod
    def get_reform_action(action_id: str) -> Optional[Dict]:
        for a in read_json("reform_actions.json") or []:
            if a.get("id") == action_id:
                return a
        return None

    @staticmethod
    def save_reform_action(action: Dict) -> None:
        Storage._upsert_by_key("reform_actions.json", "id", action)

    @staticmethod
    def delete_reform_action(action_id: str) -> bool:
        result = {"removed": False}

        def mutate(items):
            items = items or []
            remaining = [a for a in items if a.get("id") != action_id]
            result["removed"] = len(remaining) != len(items)
            return remaining

        update_json("reform_actions.json", mutate)
        return result["removed"]

    # ─── Reform: KPI Snapshots ─────────────────────────────────────────

    @staticmethod
    def get_kpi_snapshots() -> List[Dict]:
        return read_json("reform_kpis.json") or []

    @staticmethod
    def save_kpi_snapshot(snapshot: Dict) -> None:
        """kpi_id をキーに upsert(1 KPI = 最新スナップショット 1 件)"""
        Storage._upsert_by_key("reform_kpis.json", "kpi_id", snapshot)

    # ─── Reform: Weekly Agendas ────────────────────────────────────────

    @staticmethod
    def get_reform_agendas() -> List[Dict]:
        agendas = read_json("reform_agendas.json") or []
        agendas.sort(key=lambda a: a.get("week_of", ""), reverse=True)
        return agendas

    @staticmethod
    def get_reform_agenda(week_of: Optional[str] = None) -> Optional[Dict]:
        """week_of 指定でその週の、未指定で最新のアジェンダを返す"""
        agendas = Storage.get_reform_agendas()
        if week_of:
            for a in agendas:
                if a.get("week_of") == week_of:
                    return a
            return None
        return agendas[0] if agendas else None

    @staticmethod
    def save_reform_agenda(agenda: Dict) -> None:
        """week_of をキーに upsert"""
        Storage._upsert_by_key("reform_agendas.json", "week_of", agenda)
