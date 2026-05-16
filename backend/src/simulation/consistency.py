"""
ポートフォリオ整合性モジュール

ストレージに保存された値を信頼せず、必ず `cash + sum(shares × current_price)`
を再計算して表示用ポートフォリオを返す。同時に、株価の鮮度・総資産の乖離・
銘柄比率の整合性をチェックして警告を返す。
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional


# ─── しきい値 ────────────────────────────────────────────────────────────────────

TOTAL_VALUE_DRIFT_THRESHOLD_PCT = 1.0   # 保存値と再計算値の許容乖離 %
STALE_PRICE_HOURS = 24                  # 株価がこの時間以上古ければ警告
EXTREME_DAILY_CHANGE_PCT = 20.0         # 前日比がこの絶対値以上で警告


def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        # `Z` 終端などにも対応
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _hours_since(ts: Optional[str]) -> Optional[float]:
    dt = _parse_iso(ts)
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0


def reconcile_portfolio(portfolio: Dict) -> Dict:
    """
    ポートフォリオを再計算して返す（破壊的に書き換えはしない・コピーを返す）。

    - 各保有銘柄の value = shares × current_price で再計算
    - 各保有銘柄の gain_pct = (current_price - avg_cost) / avg_cost × 100
    - 各保有銘柄の weight = value / total_value × 100
    - total_value = cash + sum(holdings.value)
    """
    p = dict(portfolio or {})
    cash = float(p.get("cash", 0) or 0)

    reconciled_holdings: List[Dict] = []
    holdings_value_sum = 0.0
    for h in p.get("holdings", []) or []:
        h2 = dict(h)
        shares = float(h2.get("shares", 0) or 0)
        price = float(h2.get("current_price", 0) or 0)
        avg_cost = float(h2.get("avg_cost", 0) or 0)
        value = round(shares * price, 2)
        gain_pct = round((price - avg_cost) / avg_cost * 100, 2) if avg_cost > 0 else 0.0
        h2["value"] = value
        h2["gain_pct"] = gain_pct
        reconciled_holdings.append(h2)
        holdings_value_sum += value

    total_value = round(cash + holdings_value_sum, 2)
    for h2 in reconciled_holdings:
        h2["weight"] = round(h2["value"] / total_value * 100, 2) if total_value > 0 else 0.0

    p["holdings"] = reconciled_holdings
    p["holdings_value"] = round(holdings_value_sum, 2)
    p["total_value"] = total_value
    p["equity_ratio"] = round(holdings_value_sum / total_value * 100, 2) if total_value > 0 else 0.0
    p["cash_ratio"] = round(cash / total_value * 100, 2) if total_value > 0 else 0.0
    return p


def check_portfolio_consistency(portfolio_before: Dict, portfolio_after: Dict) -> List[Dict]:
    """
    再計算前後を比較して整合性警告を返す。

    各警告は {level, code, message} の dict。
    level は 'info' | 'warning' | 'error'。
    """
    warnings: List[Dict] = []

    # 1. 保存値と再計算値の乖離
    stored_total = float(portfolio_before.get("total_value", 0) or 0)
    computed_total = float(portfolio_after.get("total_value", 0) or 0)
    if stored_total > 0 and computed_total > 0:
        drift_pct = abs(stored_total - computed_total) / computed_total * 100
        if drift_pct > TOTAL_VALUE_DRIFT_THRESHOLD_PCT:
            warnings.append({
                "level": "warning",
                "code": "total_value_drift",
                "message": (
                    f"保存された総資産 ¥{stored_total:,.0f} と "
                    f"再計算値 ¥{computed_total:,.0f} の差が {drift_pct:.1f}% あります"
                ),
            })

    # 2. 株価の鮮度（最古の銘柄を見る）
    holdings = portfolio_after.get("holdings", []) or []
    oldest_hours: Optional[float] = None
    oldest_ticker: Optional[str] = None
    for h in holdings:
        hrs = _hours_since(h.get("price_updated_at"))
        if hrs is None:
            continue
        if oldest_hours is None or hrs > oldest_hours:
            oldest_hours = hrs
            oldest_ticker = h.get("ticker")
    if oldest_hours is not None and oldest_hours > STALE_PRICE_HOURS:
        warnings.append({
            "level": "warning",
            "code": "stale_price",
            "message": (
                f"{oldest_ticker} の株価が {oldest_hours:.0f} 時間以上前のデータです"
            ),
        })

    # 3. 前日比が極端な銘柄
    for h in holdings:
        prev = h.get("prev_price")
        cur = h.get("current_price")
        if prev and cur and float(prev) > 0:
            change_pct = (float(cur) - float(prev)) / float(prev) * 100
            if abs(change_pct) >= EXTREME_DAILY_CHANGE_PCT:
                warnings.append({
                    "level": "info",
                    "code": "extreme_daily_change",
                    "message": (
                        f"{h.get('ticker')} が前日比 {change_pct:+.1f}% — "
                        f"株式分割・決算・誤データの可能性を確認してください"
                    ),
                })

    # 4. 銘柄比率と現金比率の合計が 100% 近辺か
    cash_ratio = float(portfolio_after.get("cash_ratio", 0) or 0)
    equity_ratio = float(portfolio_after.get("equity_ratio", 0) or 0)
    total_ratio = cash_ratio + equity_ratio
    if abs(total_ratio - 100.0) > 0.5:
        warnings.append({
            "level": "error",
            "code": "ratio_mismatch",
            "message": (
                f"現金比率 {cash_ratio:.1f}% + 株式比率 {equity_ratio:.1f}% "
                f"= {total_ratio:.1f}% （100% から乖離）"
            ),
        })

    return warnings
