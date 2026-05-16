"""
ベンチマーク価格モジュール

Stooq の無料 CSV API から日経225/TOPIX/S&P500 の日次終値を取得する。
API キー不要・クラウドIPブロックなし。

データ形式: CSV (Date,Open,High,Low,Close,Volume)
URL 例: https://stooq.com/q/d/l/?s=^nkx&i=d&d1=20240101&d2=20240131
"""

import asyncio
import csv
import io
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import httpx


# Stooq シンボル
BENCHMARK_SYMBOLS: Dict[str, Dict[str, str]] = {
    "n225": {
        "stooq_symbol": "^nkx",
        "fallback_symbol": "^n225",
        "display_name": "日経225",
        "currency": "JPY",
    },
    "topix": {
        "stooq_symbol": "^tpx",
        "fallback_symbol": "1306.jp",  # 1306.JP は TOPIX 連動 ETF（代替）
        "display_name": "TOPIX",
        "currency": "JPY",
    },
    "sp500": {
        "stooq_symbol": "^spx",
        "fallback_symbol": "spy.us",   # SPY は S&P 500 連動 ETF
        "display_name": "S&P 500",
        "currency": "USD",
    },
}


# 1時間のメモリキャッシュ
_CACHE: Dict[str, Tuple[datetime, List[Dict]]] = {}
_CACHE_TTL_SECONDS = 3600


def _parse_csv(text: str) -> List[Dict]:
    """Stooq CSV を [{date, close}] にパース"""
    rows: List[Dict] = []
    reader = csv.DictReader(io.StringIO(text))
    for r in reader:
        date_str = (r.get("Date") or "").strip()
        close_str = (r.get("Close") or "").strip()
        if not date_str or not close_str or close_str.upper() == "N/D":
            continue
        try:
            close = float(close_str)
        except ValueError:
            continue
        rows.append({"date": date_str, "close": round(close, 4)})
    return rows


async def _fetch_stooq(symbol: str, days: int) -> List[Dict]:
    """Stooq から CSV を取得して [{date, close}] にして返す"""
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days + 7)  # 週末・休場を考慮して少し多めに
    url = (
        f"https://stooq.com/q/d/l/"
        f"?s={symbol}&i=d&d1={start.strftime('%Y%m%d')}&d2={end.strftime('%Y%m%d')}"
    )
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code != 200 or not r.text or "Date" not in r.text[:50]:
                return []
            return _parse_csv(r.text)
    except Exception as e:
        print(f"[benchmarks] Stooq fetch failed for {symbol}: {e}")
        return []


async def fetch_benchmark_history(name: str, days: int = 90) -> List[Dict]:
    """
    指定ベンチマークの日次終値を取得する。

    Args:
        name: 'n225' | 'topix' | 'sp500'
        days: 取得日数

    Returns:
        [{date: 'YYYY-MM-DD', close: float}, ...] 古い順
    """
    if name not in BENCHMARK_SYMBOLS:
        return []

    # キャッシュチェック
    cache_key = f"{name}:{days}"
    if cache_key in _CACHE:
        fetched_at, rows = _CACHE[cache_key]
        age = (datetime.now(timezone.utc) - fetched_at).total_seconds()
        if age < _CACHE_TTL_SECONDS:
            return rows

    spec = BENCHMARK_SYMBOLS[name]
    rows = await _fetch_stooq(spec["stooq_symbol"], days)
    if not rows and spec.get("fallback_symbol"):
        rows = await _fetch_stooq(spec["fallback_symbol"], days)

    # 直近 days 日分にトリム
    rows = rows[-days:] if len(rows) > days else rows
    _CACHE[cache_key] = (datetime.now(timezone.utc), rows)
    return rows


async def fetch_all_benchmarks(days: int = 90) -> Dict[str, List[Dict]]:
    """全ベンチマークを並列で取得"""
    names = list(BENCHMARK_SYMBOLS.keys())
    results = await asyncio.gather(
        *[fetch_benchmark_history(n, days) for n in names], return_exceptions=True
    )
    out: Dict[str, List[Dict]] = {}
    for n, r in zip(names, results):
        out[n] = r if isinstance(r, list) else []
    return out


def to_return_series(rows: List[Dict]) -> List[Dict]:
    """
    価格シリーズを「最初の日からの累積リターン %」に変換する。

    Input: [{date, close}, ...]
    Output: [{date, return_pct}, ...]
    """
    if not rows:
        return []
    base = rows[0]["close"]
    if base <= 0:
        return [{"date": r["date"], "return_pct": 0.0} for r in rows]
    return [
        {"date": r["date"], "return_pct": round((r["close"] - base) / base * 100, 3)}
        for r in rows
    ]


def align_series_by_date(
    benchmark_series: Dict[str, List[Dict]],
    agent_series: Dict[str, List[Dict]],
) -> Dict:
    """
    複数のシリーズを共通の日付軸に整列する。

    Returns:
        {
          'dates': ['YYYY-MM-DD', ...],
          'agents': {agent_id: [return_pct, ...]},
          'benchmarks': {benchmark_name: [return_pct, ...]},
        }
    """
    # 全シリーズから日付集合を取る
    all_dates: set = set()
    for rows in list(benchmark_series.values()) + list(agent_series.values()):
        for r in rows:
            all_dates.add(r["date"])
    dates = sorted(all_dates)

    def to_dict(rows: List[Dict]) -> Dict[str, float]:
        return {r["date"]: float(r.get("return_pct", 0.0)) for r in rows}

    bench_maps = {k: to_dict(v) for k, v in benchmark_series.items()}
    agent_maps = {k: to_dict(v) for k, v in agent_series.items()}

    # 前方補完（直前の値を引き継ぎ、まだ値がなければ 0）
    def fill(series: Dict[str, float]) -> List[float]:
        out: List[float] = []
        last = 0.0
        for d in dates:
            if d in series:
                last = series[d]
            out.append(round(last, 3))
        return out

    return {
        "dates": dates,
        "agents": {k: fill(v) for k, v in agent_maps.items()},
        "benchmarks": {k: fill(v) for k, v in bench_maps.items()},
    }
