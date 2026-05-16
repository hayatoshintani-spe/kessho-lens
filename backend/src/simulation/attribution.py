"""
パフォーマンス寄与分析モジュール

ファンドリターンとベンチマークリターンの差（超過リターン）を、
キャッシュドラッグと銘柄選択効果に分解する。

- excess_return     = fund_return - benchmark_return
- cash_drag         = -(cash_ratio × benchmark_return)
                      ※ 現金を持っていたことでベンチマーク連動を逃した分
- selection_effect  = Σ(holding_weight × (holding_return - benchmark_return))
                      ※ 各保有銘柄の選択効果の合計
"""

from typing import Dict, List, Optional


def _holding_return_pct(h: Dict) -> float:
    """各保有銘柄の購入時からの単純リターン %"""
    avg = float(h.get("avg_cost", 0) or 0)
    cur = float(h.get("current_price", 0) or 0)
    if avg <= 0:
        return 0.0
    return (cur - avg) / avg * 100.0


def compute_attribution(
    portfolio: Dict,
    benchmark_return_pct: float,
    benchmark_name: str = "topix",
    benchmark_display: str = "TOPIX",
) -> Dict:
    """
    ポートフォリオの超過リターンを分解する。

    Args:
        portfolio: 再計算済みポートフォリオ（reconcile_portfolio 通過後を想定）
        benchmark_return_pct: 比較期間でのベンチマーク累積リターン %
        benchmark_name: ベンチマーク識別子（n225 | topix | sp500）
        benchmark_display: 表示用ベンチマーク名

    Returns:
        {
          benchmark, benchmark_display,
          fund_return_pct, benchmark_return_pct, excess_return_pct,
          cash_drag_pct, selection_effect_pct, residual_pct,
          top_contributors: [...], top_detractors: [...],
          narrative: str,
        }
    """
    total_value = float(portfolio.get("total_value", 0) or 0)
    cash = float(portfolio.get("cash", 0) or 0)
    fund_return = float(portfolio.get("performance", {}).get("total_return_pct", 0) or 0)

    cash_ratio = (cash / total_value) if total_value > 0 else 0.0

    # キャッシュドラッグ: 現金部分がベンチマークに乗っていなかった「逃した分」
    cash_drag_pct = -(cash_ratio * benchmark_return_pct)

    # 銘柄ごとの寄与
    holdings = portfolio.get("holdings", []) or []
    contributions: List[Dict] = []
    selection_effect_pct = 0.0
    for h in holdings:
        weight_pct = float(h.get("weight", 0) or 0)  # %
        ret_pct = _holding_return_pct(h)
        # 寄与 = 銘柄比率 × (銘柄リターン − ベンチマークリターン) / 100
        excess_per_holding = ret_pct - benchmark_return_pct
        contrib = weight_pct / 100.0 * excess_per_holding
        selection_effect_pct += contrib
        contributions.append({
            "ticker": h.get("ticker", ""),
            "name": h.get("name", h.get("ticker", "")),
            "weight_pct": round(weight_pct, 2),
            "return_pct": round(ret_pct, 2),
            "vs_benchmark_pct": round(excess_per_holding, 2),
            "contribution_pct": round(contrib, 3),
        })

    contributions.sort(key=lambda c: c["contribution_pct"], reverse=True)
    top_contributors = [c for c in contributions if c["contribution_pct"] > 0][:5]
    top_detractors = sorted(
        [c for c in contributions if c["contribution_pct"] < 0],
        key=lambda c: c["contribution_pct"],
    )[:5]

    excess_return_pct = fund_return - benchmark_return_pct
    residual_pct = excess_return_pct - cash_drag_pct - selection_effect_pct

    narrative = _build_narrative(
        fund_return=fund_return,
        benchmark_return=benchmark_return_pct,
        benchmark_display=benchmark_display,
        excess=excess_return_pct,
        cash_drag=cash_drag_pct,
        cash_ratio=cash_ratio * 100,
        top_contributors=top_contributors,
        top_detractors=top_detractors,
    )

    return {
        "benchmark": benchmark_name,
        "benchmark_display": benchmark_display,
        "fund_return_pct": round(fund_return, 2),
        "benchmark_return_pct": round(benchmark_return_pct, 2),
        "excess_return_pct": round(excess_return_pct, 2),
        "cash_drag_pct": round(cash_drag_pct, 2),
        "cash_ratio_pct": round(cash_ratio * 100, 2),
        "selection_effect_pct": round(selection_effect_pct, 2),
        "residual_pct": round(residual_pct, 2),
        "top_contributors": top_contributors,
        "top_detractors": top_detractors,
        "narrative": narrative,
    }


def _build_narrative(
    fund_return: float,
    benchmark_return: float,
    benchmark_display: str,
    excess: float,
    cash_drag: float,
    cash_ratio: float,
    top_contributors: List[Dict],
    top_detractors: List[Dict],
) -> str:
    """寄与分析の自然文サマリーを生成"""
    direction = "アウトパフォーム" if excess >= 0 else "アンダーパフォーム"
    sign = "+" if excess >= 0 else ""
    parts = [
        f"ファンドリターン {fund_return:+.1f}% に対して {benchmark_display} は {benchmark_return:+.1f}%。"
        f"超過リターンは {sign}{excess:.1f}%（{direction}）。"
    ]

    if abs(cash_drag) >= 0.1:
        if cash_drag < 0:
            parts.append(
                f"現金比率 {cash_ratio:.0f}% のため、ベンチマーク連動を逃した分が {cash_drag:.1f}% 効いています（キャッシュドラッグ）。"
            )
        else:
            parts.append(
                f"市場下落局面で現金比率 {cash_ratio:.0f}% が下落の影響を {cash_drag:+.1f}% 緩和しました。"
            )

    if top_contributors:
        t = top_contributors[0]
        parts.append(
            f"最大の貢献は {t['name']}（{t['ticker']}、寄与 {t['contribution_pct']:+.1f}%）。"
        )

    if top_detractors:
        d = top_detractors[0]
        parts.append(
            f"最も足を引っ張ったのは {d['name']}（{d['ticker']}、寄与 {d['contribution_pct']:+.1f}%）。"
        )

    return "".join(parts)
