"""
ミーティングエンドポイント
AI投資会議のログを返す
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Optional

from src.data.storage import Storage
from src.data.mock_data import get_mock_meetings, get_mock_meeting

router = APIRouter()


@router.get("/meetings")
async def list_meetings(limit: int = 20):
    """
    ミーティングログの一覧を返す
    date, participants, summary, key_decisions, market_theme を含む
    """
    meetings = Storage.get_meetings(limit=limit)

    # データがない場合はモックデータを返す
    if not meetings:
        meetings = get_mock_meetings()

    # 一覧用に必要な情報だけ返す（messagesは除く）
    meetings_list = []
    for meeting in meetings:
        meetings_list.append({
            "date": meeting.get("date"),
            "participants": meeting.get("participants", []),
            "summary": meeting.get("summary", ""),
            "market_theme": meeting.get("market_theme", ""),
            "key_decisions": meeting.get("key_decisions", []),
            "message_count": len(meeting.get("messages", [])),
        })

    return {
        "meetings": meetings_list,
        "count": len(meetings_list),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/meetings/{date}")
async def get_meeting(date: str):
    """
    特定日付のミーティングログを返す（全メッセージを含む）

    date: YYYY-MM-DD 形式
    """
    # 日付バリデーション
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="日付はYYYY-MM-DD形式で指定してください（例: 2026-05-14）",
        )

    # ストレージから取得
    meeting = Storage.get_meeting(date)

    # なければモックデータを確認
    if not meeting:
        meeting = get_mock_meeting(date)

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail=f"{date} のミーティングログが見つかりません",
        )

    return {
        "meeting": meeting,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
