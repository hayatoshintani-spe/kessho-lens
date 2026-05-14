"""
発見ログエンドポイント
AIエージェントによる銘柄発見ログを返す
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Optional

from src.data.storage import Storage
from src.data.mock_data import get_mock_discoveries

router = APIRouter()


@router.get("/discovery")
async def get_discovery_logs(
    agent_id: Optional[str] = Query(None, description="エージェントID（buffett, soros, lynch, flat）"),
    limit: int = Query(50, description="取得件数上限"),
):
    """
    銘柄発見ログを返す
    オプションでエージェントIDでフィルタリング可能
    """
    discoveries = Storage.get_discoveries(agent_id=agent_id, limit=limit)

    # データがない場合はモックデータを返す
    if not discoveries:
        mock = get_mock_discoveries()
        if agent_id:
            mock = [d for d in mock if d.get("agent_id") == agent_id]
        discoveries = mock[:limit]

    # エージェント名のマッピング
    agent_display_names = {
        "buffett": "BuffettAI",
        "soros": "SorosAI",
        "lynch": "LynchAI",
        "flat": "FlatAI",
    }

    # 表示用にエージェント名を追加
    for d in discoveries:
        d_agent_id = d.get("agent_id", "")
        if "agent_name" not in d:
            d["agent_name"] = agent_display_names.get(d_agent_id, d_agent_id)

    return {
        "discoveries": discoveries,
        "count": len(discoveries),
        "filtered_by_agent": agent_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
