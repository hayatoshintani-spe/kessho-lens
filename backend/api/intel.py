"""
Tsuburaya Intelligence Brief API
- カード一覧/詳細/生成
- ブリーフ一覧/詳細/生成
- AIエージェント会議
- カテゴリ・ウォッチリスト
"""

import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.data.storage import Storage
from src.intel.categories import CATEGORY_META, list_categories
from src.intel.experts import EXPERT_META, list_experts, IMPORTANCE_LABELS
from src.intel.card_generator import build_intel_card
from src.intel.brief_generator import build_daily_brief, build_weekly_brief
from src.intel.council import generate_council_session
from src.intel import notion_sync

router = APIRouter()


# ─── Cards ───────────────────────────────────────────────────────────────


@router.get("/intel/cards")
async def list_intel_cards(
    category: Optional[str] = Query(None),
    importance: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    cards = Storage.get_intel_cards(category=category, importance=importance, limit=limit)
    return {
        "cards": cards,
        "count": len(cards),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/intel/cards/{card_id}")
async def get_intel_card(card_id: str):
    card = Storage.get_intel_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"カード '{card_id}' が見つかりません")
    return {"card": card}


class CardCreateRequest(BaseModel):
    title: str
    url: Optional[str] = None
    publisher: Optional[str] = None
    summary: Optional[str] = None
    user_note: Optional[str] = None
    access_status: Optional[str] = "full"
    category: Optional[str] = None
    importance: Optional[str] = None
    date: Optional[str] = None  # YYYY-MM-DD
    sync_to_notion: Optional[bool] = True  # デフォルト同期、Notion未設定なら自動skip


@router.post("/intel/cards")
async def create_intel_card(req: CardCreateRequest):
    """新規カードを生成して保存。Notion設定済みなら自動同期"""
    payload = req.model_dump(exclude_none=True)
    date = payload.pop("date", None)
    sync_flag = payload.pop("sync_to_notion", True)
    card = build_intel_card(payload, date=date)
    Storage.save_intel_card(card)

    notion_result = None
    if sync_flag and notion_sync.is_enabled():
        notion_result = notion_sync.sync_card(card)

    return {
        "card": card,
        "message": "カードを生成しました",
        "notion": notion_result,
    }


# ─── Briefs ──────────────────────────────────────────────────────────────


@router.get("/intel/briefs")
async def list_briefs(brief_type: Optional[str] = Query(None)):
    briefs = Storage.get_intel_briefs(brief_type=brief_type)
    # 軽量化: sections は最初の100文字だけ返す
    summary_list = []
    for b in briefs:
        summary_list.append({
            "date": b.get("date"),
            "brief_type": b.get("brief_type", "daily"),
            "title": b.get("title"),
            "executive_summary": b.get("executive_summary", ""),
            "card_count": len(b.get("top_topics", [])),
        })
    return {"briefs": summary_list, "count": len(summary_list)}


@router.get("/intel/briefs/daily/{date}")
async def get_daily_brief(date: str):
    brief = Storage.get_intel_brief(date, "daily")
    if not brief:
        raise HTTPException(
            status_code=404,
            detail=f"{date}のDaily Briefが見つかりません",
        )
    # トップカードの詳細を埋める
    top_topic_ids = brief.get("top_topics", [])
    top_cards = [Storage.get_intel_card(cid) for cid in top_topic_ids]
    top_cards = [c for c in top_cards if c]
    council = None
    if brief.get("council_session_id"):
        council = Storage.get_council_session(brief["council_session_id"])
    return {
        "brief": brief,
        "top_cards": top_cards,
        "council": council,
    }


class BriefBuildRequest(BaseModel):
    date: str  # YYYY-MM-DD
    generate_council: bool = False
    council_topic: Optional[str] = None


@router.post("/intel/briefs/daily/build")
async def build_daily(req: BriefBuildRequest):
    """指定日のカードからDaily Briefを組み立てる"""
    all_cards = Storage.get_intel_cards(limit=500)
    cards_today = [c for c in all_cards if c.get("date") == req.date]
    if not cards_today:
        raise HTTPException(
            status_code=404,
            detail=f"{req.date}のカードが見つかりません。先にカードを登録してください。",
        )

    council_id = None
    if req.generate_council:
        topic = req.council_topic or (
            f"{req.date}の最重要トピックに対する戦略議論"
        )
        # 重要度A/Bのカードを文脈として渡す
        ctx = [c for c in cards_today if c.get("importance") in ("A", "B")][:5]
        session = generate_council_session(topic, ctx, date=req.date)
        Storage.save_council_session(session)
        council_id = session["id"]

    brief = build_daily_brief(req.date, cards_today, council_session_id=council_id)
    Storage.save_intel_brief(brief)
    return {"brief": brief, "council_session_id": council_id}


# ─── Council ─────────────────────────────────────────────────────────────


@router.get("/intel/council")
async def list_council_sessions():
    sessions = Storage.get_council_sessions()
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/intel/council/{session_id}")
async def get_council_session(session_id: str):
    session = Storage.get_council_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    # 関連カードを埋める
    related_cards = [
        Storage.get_intel_card(cid) for cid in session.get("trigger_card_ids", [])
    ]
    related_cards = [c for c in related_cards if c]
    return {"session": session, "related_cards": related_cards}


class CouncilCreateRequest(BaseModel):
    topic: str
    card_ids: List[str] = []
    date: Optional[str] = None


@router.post("/intel/council")
async def create_council_session(req: CouncilCreateRequest):
    cards = [Storage.get_intel_card(cid) for cid in req.card_ids]
    cards = [c for c in cards if c]
    session = generate_council_session(req.topic, cards, date=req.date)
    Storage.save_council_session(session)
    return {"session": session}


# ─── Metadata: categories, experts, importance ──────────────────────────


@router.get("/intel/meta")
async def get_intel_meta():
    """カテゴリ・エキスパート・重要度のメタ情報"""
    return {
        "categories": list_categories(),
        "experts": list_experts(),
        "importance": list(IMPORTANCE_LABELS.values()),
    }


# ─── Watchlist ──────────────────────────────────────────────────────────


# ─── Notion ──────────────────────────────────────────────────────────────


@router.get("/intel/notion/status")
async def notion_status():
    """Notion接続状況とDB情報を返す"""
    return notion_sync.get_status()


class NotionSyncRequest(BaseModel):
    card_id: Optional[str] = None  # 指定なしなら全カード


@router.post("/intel/notion/sync")
async def notion_sync_endpoint(req: NotionSyncRequest):
    """カードをNotionに同期する。card_id指定で個別、なしで全件"""
    if not notion_sync.is_enabled():
        raise HTTPException(
            status_code=400,
            detail="NOTION_API_KEY または NOTION_CARDS_DB_ID が未設定です",
        )
    if req.card_id:
        card = Storage.get_intel_card(req.card_id)
        if not card:
            raise HTTPException(status_code=404, detail="カードが見つかりません")
        return {"mode": "single", "result": notion_sync.sync_card(card)}
    else:
        cards = Storage.get_intel_cards(limit=500)
        return {"mode": "all", "result": notion_sync.sync_all_cards(cards)}


class NotionSetupRequest(BaseModel):
    parent_page_id: str


@router.post("/intel/notion/setup")
async def notion_setup(req: NotionSetupRequest):
    """
    Notion DB を新規作成する。
    Notion Integration を親ページに招待しておく必要がある。
    """
    if not os.getenv("NOTION_API_KEY"):
        raise HTTPException(status_code=400, detail="NOTION_API_KEY が未設定です")
    result = notion_sync.create_cards_database(req.parent_page_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/intel/watchlist")
async def get_watchlist():
    lists = Storage.get_watchlists()
    if not lists:
        # デフォルトのウォッチリストを返す（カテゴリ別の targets を流用）
        lists = []
        for cat_id, meta in CATEGORY_META.items():
            lists.append({
                "category": cat_id,
                "label": meta["label"],
                "description": " / ".join(meta["watch_angles"][:2]),
                "targets": meta["targets"],
                "items": [
                    {
                        "keyword": t,
                        "category": cat_id,
                        "rationale": meta["watch_angles"][0] if meta["watch_angles"] else "",
                        "priority": "medium",
                    }
                    for t in meta["targets"][:6]
                ],
            })
    return {"watchlists": lists}
