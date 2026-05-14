"""
クロンエンドポイント
定期的なデイリーシミュレーション実行のためのエンドポイント
"""

import os
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from datetime import datetime, timezone

from src.simulation.daily_runner import run_daily_simulation

router = APIRouter()


@router.post("/run-daily")
async def run_daily_manual(background_tasks: BackgroundTasks):
    """
    デイリーシミュレーションを手動で実行するエンドポイント
    バックグラウンドで実行し、すぐにレスポンスを返す
    """
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # バックグラウンドで実行
    background_tasks.add_task(_run_simulation_task, date)

    return {
        "status": "started",
        "message": f"{date} のデイリーシミュレーションを開始しました",
        "date": date,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/cron/run-daily")
async def cron_run_daily(request: Request, background_tasks: BackgroundTasks):
    """
    クロンジョブからのデイリーシミュレーション実行
    CRON_SECRETヘッダーで認証
    """
    # 認証チェック
    auth = request.headers.get("Authorization", "")
    cron_secret = os.getenv("CRON_SECRET", "")

    if not cron_secret:
        # CRON_SECRETが設定されていない場合はローカル環境として許可
        if os.getenv("ENV") == "production":
            raise HTTPException(
                status_code=500,
                detail="CRON_SECRETが設定されていません",
            )
    else:
        expected = f"Bearer {cron_secret}"
        if auth != expected:
            raise HTTPException(
                status_code=401,
                detail="認証に失敗しました。正しいCRON_SECRETを設定してください。",
            )

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # バックグラウンドで実行
    background_tasks.add_task(_run_simulation_task, date)

    return {
        "status": "started",
        "message": f"クロンジョブ: {date} のデイリーシミュレーションを開始しました",
        "date": date,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _run_simulation_task(date: str) -> None:
    """バックグラウンドでシミュレーションを実行するタスク"""
    try:
        result = await run_daily_simulation(date)
        print(f"[クロン] シミュレーション完了: {result}")
    except Exception as e:
        print(f"[クロン] シミュレーションエラー: {e}")
        import traceback
        traceback.print_exc()
