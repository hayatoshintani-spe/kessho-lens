"""
レポートエンドポイント
AIファンドの日次レポートを返す
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from src.data.storage import Storage
from src.data.mock_data import get_mock_reports, get_mock_report

router = APIRouter()


@router.get("/reports")
async def list_reports(limit: int = 20):
    """
    日次レポートの一覧を返す（Markdownコンテンツは除く）
    """
    reports = Storage.get_reports(limit=limit)

    # データがない場合はモックデータを返す
    if not reports:
        reports = get_mock_reports()

    # 一覧用（contentは重いので除く）
    reports_list = []
    for report in reports:
        reports_list.append({
            "date": report.get("date"),
            "title": report.get("title", f"AIファンド日次レポート - {report.get('date', '')}"),
            "agent_summaries": report.get("agent_summaries", {}),
        })

    return {
        "reports": reports_list,
        "count": len(reports_list),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/reports/{date}")
async def get_report(date: str):
    """
    特定日付のフルレポートを返す（Markdown形式）

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
    report = Storage.get_report(date)

    # なければモックデータを確認
    if not report:
        report = get_mock_report(date)

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"{date} のレポートが見つかりません",
        )

    return {
        "report": report,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
