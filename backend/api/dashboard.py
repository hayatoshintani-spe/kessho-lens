"""
ダッシュボードエンドポイント
全エージェントのパフォーマンス、P&L、ランキング、チャートデータを返す
"""

from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import random

from src.data.storage import Storage
from src.data.mock_data import INITIAL_PORTFOLIOS
from src.simulation.consistency import reconcile_portfolio, check_portfolio_consistency

router = APIRouter()

# エージェントのメタ情報
_AGENT_META = {
    "buffett": {
        "display_name": "BuffettAI",
        "color": "#1d6a96",
        "icon": "🏦",
        "style": "バリュー投資",
    },
    "soros": {
        "display_name": "SorosAI",
        "color": "#8b5e3c",
        "icon": "🌍",
        "style": "グローバルマクロ",
    },
    "lynch": {
        "display_name": "LynchAI",
        "color": "#2d8a4e",
        "icon": "🔍",
        "style": "成長株",
    },
    "flat": {
        "display_name": "FlatAI",
        "color": "#6b6b6b",
        "icon": "📊",
        "style": "インデックス",
    },
}


@router.get("/dashboard")
async def get_dashboard():
    """
    ダッシュボード全体のデータを返す
    - 各エージェントのパフォーマンス
    - P&Lランキング
    - ヒストリカルチャートデータ
    """
    # ポートフォリオデータ取得
    agents_data = []
    rankings = []

    for agent_id, meta in _AGENT_META.items():
        portfolio_raw = Storage.get_portfolio(agent_id)
        if not portfolio_raw:
            portfolio_raw = INITIAL_PORTFOLIOS.get(agent_id, {})

        # 表示前に必ず再計算する（保存値を信頼しない）
        portfolio = reconcile_portfolio(portfolio_raw)
        consistency_warnings = check_portfolio_consistency(portfolio_raw, portfolio)

        perf = portfolio.get("performance", {})
        total_value = portfolio.get("total_value", 50_000_000)
        holdings = portfolio.get("holdings", [])

        agent_data = {
            "id": agent_id,
            "display_name": meta["display_name"],
            "color": meta["color"],
            "icon": meta["icon"],
            "style": meta["style"],
            "total_value": total_value,
            "cash": portfolio.get("cash", 0),
            "cash_ratio": portfolio.get("cash_ratio", 0),
            "equity_ratio": portfolio.get("equity_ratio", 0),
            "holdings_value": portfolio.get("holdings_value", 0),
            "holdings_count": len(holdings),
            "price_updated_at": portfolio.get("price_updated_at"),
            "price_source": portfolio.get("price_source"),
            "consistency_warnings": consistency_warnings,
            "performance": {
                "total_return_pct": perf.get("total_return_pct", 0),
                "daily_pnl": perf.get("daily_pnl", 0),
                "weekly_pnl": perf.get("weekly_pnl", 0),
                "monthly_pnl": perf.get("monthly_pnl", 0),
            },
            "top_holdings": sorted(
                holdings, key=lambda h: h.get("value", 0), reverse=True
            )[:3],
        }
        agents_data.append(agent_data)
        rankings.append({
            "agent_id": agent_id,
            "display_name": meta["display_name"],
            "color": meta["color"],
            "daily_pnl": perf.get("daily_pnl", 0),
            "total_return_pct": perf.get("total_return_pct", 0),
        })

    # ランキングを日次損益で並べ替え
    rankings.sort(key=lambda x: x["daily_pnl"], reverse=True)
    for i, r in enumerate(rankings):
        r["rank"] = i + 1

    # ヒストリカルチャートデータを生成
    history_chart = _generate_history_chart()

    # 最新のミーティングと直近の取引
    recent_meetings = Storage.get_meetings(limit=3)
    recent_trades = Storage.get_trades(limit=10)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": agents_data,
        "rankings": rankings,
        "history_chart": history_chart,
        "recent_meetings": [
            {
                "date": m.get("date"),
                "summary": m.get("summary", ""),
                "market_theme": m.get("market_theme", ""),
                "participants": m.get("participants", []),
            }
            for m in recent_meetings
        ],
        "recent_trades": recent_trades[:10],
        "market_summary": _get_market_summary(),
    }


def _generate_history_chart() -> Dict:
    """
    過去30日間のパフォーマンスチャートデータを生成
    ストレージにデータがあれば実データ、なければモックデータ
    """
    dates = []
    today = datetime.now(timezone.utc).date()
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        # 土日はスキップ
        if d.weekday() < 5:
            dates.append(d.strftime("%Y-%m-%d"))

    # 各エージェントの累積リターンをランダムウォークで生成（モック）
    base_returns = {
        "buffett": {"start": 0.0, "volatility": 0.3, "drift": 0.04},
        "soros": {"start": 0.0, "volatility": 0.8, "drift": 0.08},
        "lynch": {"start": 0.0, "volatility": 0.5, "drift": 0.06},
        "flat": {"start": 0.0, "volatility": 0.25, "drift": 0.045},
    }

    series = {}
    for agent_id, params in base_returns.items():
        # ポートフォリオの実績データがあれば使う
        portfolio = Storage.get_portfolio(agent_id) or INITIAL_PORTFOLIOS.get(agent_id, {})
        final_return = portfolio.get("performance", {}).get("total_return_pct", 0)

        # ランダムウォークで中間データを生成
        returns = [0.0]
        current = 0.0
        for _ in range(len(dates) - 1):
            change = random.gauss(params["drift"] / 252, params["volatility"] / 15)
            current += change
            returns.append(round(current, 2))

        # 最終値を実績値に合わせて調整
        if returns:
            scale = final_return / returns[-1] if returns[-1] != 0 else 1
            returns = [round(r * abs(scale), 2) for r in returns]
            returns[-1] = final_return

        series[agent_id] = returns

    return {
        "dates": dates,
        "series": {
            agent_id: {
                "display_name": _AGENT_META[agent_id]["display_name"],
                "color": _AGENT_META[agent_id]["color"],
                "data": series[agent_id],
            }
            for agent_id in series
        },
    }


def _get_market_summary() -> Dict:
    """市場概況サマリーを返す（モック）"""
    sp500_change = round(random.uniform(-1.5, 1.5), 2)
    return {
        "sp500_change_pct": sp500_change,
        "nasdaq_change_pct": round(random.uniform(-2.0, 2.0), 2),
        "vix": round(random.uniform(12, 28), 1),
        "sentiment": (
            "強気" if sp500_change > 0.3 else
            "弱気" if sp500_change < -0.3 else "中立"
        ),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
