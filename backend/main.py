"""
Tsuburaya Intelligence Brief — Backend

外部ニュース・規制動向・技術トレンドを、円谷の事業機会・リスク・
経営論点に翻訳して経営層に届ける情報基盤。
"""

import sys
import os

# パスを設定してモジュールを読み込み可能にする
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# APIルーターをインポート
from api.health import router as health_router
from api.intel import router as intel_router

# FastAPIアプリケーションを初期化
app = FastAPI(
    title="Tsuburaya Intelligence Brief API",
    description="円谷向けインテリジェンス・ブリーフ生成と AI 会議の API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORSミドルウェアを設定
_explicit_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]
_frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
if _frontend_url:
    _explicit_origins.append(_frontend_url)

_extra = os.getenv("ALLOWED_ORIGINS", "")
if _extra:
    _explicit_origins.extend([o.strip().rstrip("/") for o in _extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_explicit_origins,
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\.)*(vercel\.app|netlify\.app|railway\.app|onrender\.com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(health_router, prefix="/api", tags=["ヘルスチェック"])
app.include_router(intel_router, prefix="/api", tags=["インテリジェンス"])


@app.on_event("startup")
async def restore_cards_from_notion_on_startup():
    """Render 無料プランは揮発性ディスクのため、起動時に Notion DB から
    カードを復元してローカル JSON にロードする。Notion 未設定なら no-op。
    """
    try:
        from src.intel import notion_sync
        if not notion_sync.is_enabled():
            return
        import asyncio
        result = await asyncio.to_thread(notion_sync.restore_local_from_notion)
        print(f"[startup] Notion restore: {result}")
    except Exception as e:
        print(f"[startup] Notion restore failed (non-fatal): {e}")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "name": "Tsuburaya Intelligence Brief",
        "description": "円谷向けインテリジェンス・ブリーフ API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "production") == "development",
    )
