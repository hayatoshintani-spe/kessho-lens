"""
ヘルスチェックエンドポイント
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """ヘルスチェック - アプリケーションの稼働状態を返す"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "app": "tsuburaya-intelligence-brief",
        "description": "円谷向けインテリジェンス・ブリーフ API",
        "env": os.getenv("ENV", "production"),
        "has_anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "has_notion_key": bool(os.getenv("NOTION_API_KEY")),
        "has_notion_db_id": bool(os.getenv("NOTION_CARDS_DB_ID")),
    }
