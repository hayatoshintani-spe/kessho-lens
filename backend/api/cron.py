"""
クロンエンドポイント
定期的なデイリーシミュレーション実行のためのエンドポイント
"""

import os
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Query
from datetime import datetime, date as date_type, timedelta, timezone
from typing import Optional

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
    # 認証チェック - CRON_SECRETは必須（spec準拠）
    cron_secret = os.getenv("CRON_SECRET", "")
    if not cron_secret:
        raise HTTPException(
            status_code=500,
            detail="サーバー設定エラー: CRON_SECRET が設定されていません",
        )

    auth = request.headers.get("Authorization", "")
    expected = f"Bearer {cron_secret}"
    if auth != expected:
        raise HTTPException(
            status_code=401,
            detail="認証に失敗しました。Authorization: Bearer <CRON_SECRET> が必要です。",
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


@router.post("/backfill")
async def run_backfill(
    background_tasks: BackgroundTasks,
    from_date: str = Query(..., description="開始日 (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="終了日 (YYYY-MM-DD)。省略時は今日。"),
    skip_weekends: bool = Query(True, description="土日をスキップするか"),
):
    """
    指定期間のデイリーシミュレーションを一括バックフィル実行する。
    過去データの補完用。Claude APIは使わず高速ルールベース生成を使用。
    バックグラウンドで実行し、すぐにレスポンスを返す。
    """
    today = datetime.now(timezone.utc).date()

    try:
        start = date_type.fromisoformat(from_date)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"from_date の形式が正しくありません: {from_date}")

    if to_date:
        try:
            end = date_type.fromisoformat(to_date)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"to_date の形式が正しくありません: {to_date}")
    else:
        end = today

    if start > end:
        raise HTTPException(status_code=400, detail="from_date は to_date より前の日付にしてください")

    if (end - start).days > 365:
        raise HTTPException(status_code=400, detail="バックフィル期間は最大365日です")

    # 対象日付リストを構築
    dates = []
    current = start
    while current <= end:
        if not skip_weekends or current.weekday() < 5:  # 0=月〜4=金
            dates.append(current.isoformat())
        current += timedelta(days=1)

    background_tasks.add_task(_run_backfill_task, dates)

    return {
        "status": "started",
        "message": f"{len(dates)} 日分のバックフィルをバックグラウンドで開始しました",
        "from_date": from_date,
        "to_date": end.isoformat(),
        "total_days": len(dates),
        "skip_weekends": skip_weekends,
        "dates": dates[:5],  # 先頭5件のみプレビュー
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _run_backfill_task(dates: list) -> None:
    """バックグラウンドでバックフィルを実行するタスク"""
    print(f"[バックフィル] {len(dates)} 日分の処理を開始")
    success_count = 0
    error_count = 0

    for date_str in dates:
        try:
            result = await run_daily_simulation(date_str, fast=True)
            if result.get("status") == "success":
                success_count += 1
                print(f"[バックフィル] {date_str} 完了 ({success_count}/{len(dates)})")
            else:
                error_count += 1
                print(f"[バックフィル] {date_str} エラー: {result.get('error')}")
        except Exception as e:
            error_count += 1
            print(f"[バックフィル] {date_str} 例外: {e}")
            import traceback
            traceback.print_exc()

    print(f"[バックフィル] 完了: 成功={success_count}, エラー={error_count}")
