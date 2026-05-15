"""
kessho-lens バックエンド
AIが投資判断を下し、その思考プロセスを可視化するシミュレーター
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
from api.dashboard import router as dashboard_router
from api.agents import router as agents_router
from api.meetings import router as meetings_router
from api.reports import router as reports_router
from api.discovery import router as discovery_router
from api.cron import router as cron_router
from api.advisor import router as advisor_router

# FastAPIアプリケーションを初期化
app = FastAPI(
    title="kessho-lens API",
    description="AIインベストメントファンドシミュレーター - AIの思考プロセスを可視化",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORSミドルウェアを設定
# allow_origin_regex でワイルドカード相当のドメインを許可（FastAPIはallow_originsではワイルドカードを解釈しない）
_explicit_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]
_frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
if _frontend_url:
    _explicit_origins.append(_frontend_url)

# ALLOWED_ORIGINS env var (カンマ区切り) で追加可能
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
app.include_router(dashboard_router, prefix="/api", tags=["ダッシュボード"])
app.include_router(agents_router, prefix="/api", tags=["エージェント"])
app.include_router(meetings_router, prefix="/api", tags=["ミーティング"])
app.include_router(reports_router, prefix="/api", tags=["レポート"])
app.include_router(discovery_router, prefix="/api", tags=["発見ログ"])
app.include_router(cron_router, prefix="/api", tags=["クロン"])
app.include_router(advisor_router, prefix="/api", tags=["アドバイザー"])


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    try:
        from src.simulation.daily_runner import initialize_mock_data
        initialize_mock_data()
        print("[起動] モックデータの初期化完了")
    except Exception as e:
        print(f"[起動] 初期化エラー（続行します）: {e}")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "name": "kessho-lens",
        "description": "AIインベストメントファンドシミュレーター",
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
