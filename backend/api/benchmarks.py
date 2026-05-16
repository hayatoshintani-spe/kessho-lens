"""
ベンチマーク比較・寄与分析エンドポイント
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Query

from src.data.storage import Storage
from src.simulation.benchmarks import (
    BENCHMARK_SYMBOLS,
    fetch_all_benchmarks,
    to_return_series,
    align_series_by_date,
)
from src.simulation.consistency import reconcile_portfolio
from src.simulation.attribution import compute_attribution

router = APIRouter()


_FUND_AGENT_IDS = ["buffett", "soros", "lynch", "flat"]


def _build_agent_series_from_history(agent_id: str, days: int) -> List[Dict]:
    """
    NAV履歴から累積リターンシリーズを構築する。
    履歴が無ければ空リストを返す（呼び出し側で合成シリーズにフォールバック）。
    """
    history = Storage.get_nav_history(agent_id) or []
    if len(history) < 2:
        return []

    # 期間内に絞る
    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=days)).strftime("%Y-%m-%d")
    in_range = [h for h in history if h.get("date", "") >= cutoff]
    if len(in_range) < 2:
        return []

    base = float(in_range[0].get("total_value", 0) or 0)
    if base <= 0:
        return []

    series: List[Dict] = []
    for h in in_range:
        v = float(h.get("total_value", 0) or 0)
        ret = (v - base) / base * 100 if base > 0 else 0
        series.append({"date": h.get("date"), "return_pct": round(ret, 3)})
    return series


def _synthesize_agent_series(agent_id: str, days: int, dates: List[str]) -> List[Dict]:
    """
    NAV履歴が無い場合の合成シリーズ。
    最終リターンを `performance.total_return_pct` に合わせて、
    線形+小さなノイズで埋める。あくまでデモ表示用。
    """
    portfolio = Storage.get_portfolio(agent_id) or {}
    final_return = float(portfolio.get("performance", {}).get("total_return_pct", 0) or 0)

    if not dates:
        return []

    n = len(dates)
    series: List[Dict] = []
    for i, d in enumerate(dates):
        # 序盤は 0 付近、終盤で final_return に到達するように単調補間
        progress = i / max(n - 1, 1)
        # わずかにS字補間で見た目を自然に
        smoothed = progress * progress * (3 - 2 * progress)
        value = round(final_return * smoothed, 3)
        series.append({"date": d, "return_pct": value})
    return series


@router.get("/benchmarks")
async def get_benchmarks(days: int = Query(90, ge=7, le=365)):
    """
    ファンド・ベンチマーク（日経225・TOPIX・S&P500）の累積リターン時系列。

    Args:
        days: 取得日数（7〜365）

    Returns:
        {
          days, fetched_at,
          dates: [...],
          agents: {buffett: [...], ...},
          benchmarks: {n225: [...], topix: [...], sp500: [...]},
          benchmark_meta: {n225: {display_name, currency}, ...},
          summary: [{agent_id, fund_return, vs_n225, vs_topix, vs_sp500}, ...],
        }
    """
    # ベンチマーク取得 → 累積リターン化
    raw_bench = await fetch_all_benchmarks(days=days)
    bench_series = {k: to_return_series(v) for k, v in raw_bench.items()}

    # エージェントのリターンシリーズを構築
    agent_series: Dict[str, List[Dict]] = {}
    for agent_id in _FUND_AGENT_IDS:
        s = _build_agent_series_from_history(agent_id, days=days)
        agent_series[agent_id] = s  # 後で合成補完する

    # 日付軸を整列
    aligned = align_series_by_date(bench_series, agent_series)
    dates = aligned["dates"]

    # 履歴が空のエージェントは合成シリーズで埋める
    if dates:
        for agent_id in _FUND_AGENT_IDS:
            if not aligned["agents"].get(agent_id):
                synth = _synthesize_agent_series(agent_id, days=days, dates=dates)
                aligned["agents"][agent_id] = [s["return_pct"] for s in synth]

    # サマリー（最終日の値で比較）
    summary: List[Dict] = []
    for agent_id in _FUND_AGENT_IDS:
        a_series = aligned["agents"].get(agent_id, [])
        a_final = a_series[-1] if a_series else 0.0
        row = {
            "agent_id": agent_id,
            "fund_return_pct": round(a_final, 2),
        }
        for b_name in BENCHMARK_SYMBOLS.keys():
            b_series = aligned["benchmarks"].get(b_name, [])
            b_final = b_series[-1] if b_series else 0.0
            row[f"vs_{b_name}_pct"] = round(a_final - b_final, 2)
        summary.append(row)

    return {
        "days": days,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "dates": dates,
        "agents": aligned["agents"],
        "benchmarks": aligned["benchmarks"],
        "benchmark_meta": {
            k: {"display_name": v["display_name"], "currency": v["currency"]}
            for k, v in BENCHMARK_SYMBOLS.items()
        },
        "summary": summary,
    }


@router.get("/attribution/{agent_id}")
async def get_attribution(
    agent_id: str,
    benchmark: str = Query("topix", pattern="^(n225|topix|sp500)$"),
    days: int = Query(90, ge=7, le=365),
):
    """
    エージェントの超過リターンをキャッシュドラッグ + 銘柄選択効果に分解する。
    """
    agent_id = agent_id.lower()
    if agent_id not in _FUND_AGENT_IDS:
        raise HTTPException(status_code=404, detail=f"unknown agent: {agent_id}")
    if benchmark not in BENCHMARK_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"unknown benchmark: {benchmark}")

    # ベンチマーク累積リターンを取得
    raw = await fetch_all_benchmarks(days=days)
    bench_rows = to_return_series(raw.get(benchmark, []))
    benchmark_return = bench_rows[-1]["return_pct"] if bench_rows else 0.0
    display = BENCHMARK_SYMBOLS[benchmark]["display_name"]

    # ポートフォリオを再計算
    portfolio_raw = Storage.get_portfolio(agent_id) or {}
    portfolio = reconcile_portfolio(portfolio_raw)
    # performance はストレージ側に居るのでマージしておく
    portfolio["performance"] = portfolio_raw.get("performance", {})

    attribution = compute_attribution(
        portfolio=portfolio,
        benchmark_return_pct=benchmark_return,
        benchmark_name=benchmark,
        benchmark_display=display,
    )

    return {
        "agent_id": agent_id,
        "days": days,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        **attribution,
    }
