"""
ヘルスチェックエンドポイント
アプリケーションの稼働状態を返す
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
        "app": "kessho-lens",
        "description": "AIインベストメントファンドシミュレーター",
        "env": os.getenv("ENV", "production"),
        "has_anthropic_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "has_alpaca_keys": bool(
            os.getenv("ALPACA_API_KEY_ID") and os.getenv("ALPACA_API_SECRET_KEY")
        ),
        "has_finnhub_key": bool(os.getenv("FINNHUB_API_KEY")),
        "has_alpha_vantage_key": bool(os.getenv("ALPHA_VANTAGE_API_KEY")),
        "market_data_priority": (
            "alpaca"
            if os.getenv("ALPACA_API_KEY_ID") and os.getenv("ALPACA_API_SECRET_KEY")
            else "finnhub"
            if os.getenv("FINNHUB_API_KEY")
            else "yfinance"
        ),
    }
