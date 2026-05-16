"""
ポートフォリオ管理モジュール
各エージェントのポートフォリオを管理し、取引を実行する
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from src.data.storage import Storage
from src.data.mock_data import INITIAL_PORTFOLIOS


def get_or_init_portfolio(agent_id: str) -> Dict:
    """
    エージェントのポートフォリオを取得、なければ初期化して返す
    """
    portfolio = Storage.get_portfolio(agent_id)
    if not portfolio:
        # モックデータから初期ポートフォリオを取得
        portfolio = INITIAL_PORTFOLIOS.get(agent_id, {
            "agent_id": agent_id,
            "cash": 10_000_000,
            "total_value": 50_000_000,
            "holdings": [],
            "performance": {
                "total_return_pct": 0.0,
                "daily_pnl": 0,
                "weekly_pnl": 0,
                "monthly_pnl": 0,
            },
        })
        Storage.save_portfolio(agent_id, portfolio)
    return portfolio


def execute_trade(
    agent_id: str,
    ticker: str,
    action: str,
    shares: int,
    price: float,
    reason: str,
) -> Dict:
    """
    取引を実行してポートフォリオを更新する

    Args:
        agent_id: エージェントID
        ticker: 銘柄コード
        action: "buy" | "sell"
        shares: 株数
        price: 現在価格
        reason: 取引理由（日本語）

    Returns:
        取引結果辞書
    """
    portfolio = get_or_init_portfolio(agent_id)
    total_cost = shares * price

    trade_record = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": agent_id,
        "ticker": ticker,
        "action": action,
        "shares": shares,
        "price": price,
        "total": total_cost,
        "reason": reason,
        "success": False,
        "message": "",
    }

    if action == "buy":
        if portfolio.get("cash", 0) < total_cost:
            trade_record["message"] = f"キャッシュ不足。必要: ¥{total_cost:,.0f}, 保有: ¥{portfolio.get('cash', 0):,.0f}"
            Storage.append_trade(trade_record)
            return trade_record

        # キャッシュを減らす
        portfolio["cash"] = portfolio.get("cash", 0) - total_cost

        # 保有銘柄に追加/更新
        holdings = portfolio.get("holdings", [])
        existing = next((h for h in holdings if h["ticker"] == ticker), None)
        if existing:
            total_shares = existing["shares"] + shares
            avg_cost = (existing["avg_cost"] * existing["shares"] + price * shares) / total_shares
            existing["shares"] = total_shares
            existing["avg_cost"] = round(avg_cost, 2)
            existing["current_price"] = price
            existing["value"] = round(total_shares * price, 2)
            existing["gain_pct"] = round((price - avg_cost) / avg_cost * 100, 2)
        else:
            holdings.append({
                "ticker": ticker,
                "name": ticker,
                "shares": shares,
                "avg_cost": price,
                "current_price": price,
                "value": round(shares * price, 2),
                "gain_pct": 0.0,
            })

        portfolio["holdings"] = holdings
        trade_record["success"] = True
        trade_record["message"] = f"{ticker} {shares}株を${price:.2f}で購入"

    elif action == "sell":
        holdings = portfolio.get("holdings", [])
        existing = next((h for h in holdings if h["ticker"] == ticker), None)

        if not existing or existing["shares"] < shares:
            trade_record["message"] = f"保有株数不足。保有: {existing['shares'] if existing else 0}株"
            Storage.append_trade(trade_record)
            return trade_record

        # キャッシュを増やす
        portfolio["cash"] = portfolio.get("cash", 0) + total_cost

        # 保有株を減らす
        existing["shares"] -= shares
        if existing["shares"] == 0:
            portfolio["holdings"] = [h for h in holdings if h["ticker"] != ticker]
        else:
            existing["current_price"] = price
            existing["value"] = round(existing["shares"] * price, 2)
            existing["gain_pct"] = round(
                (price - existing["avg_cost"]) / existing["avg_cost"] * 100, 2
            )

        trade_record["success"] = True
        trade_record["message"] = f"{ticker} {shares}株を${price:.2f}で売却"

    # ポートフォリオの合計価値を更新
    _update_portfolio_value(portfolio, price, ticker)
    Storage.save_portfolio(agent_id, portfolio)
    Storage.append_trade(trade_record)

    return trade_record


def _update_portfolio_value(portfolio: Dict, latest_price: float, latest_ticker: str) -> None:
    """ポートフォリオの合計価値を更新"""
    total_value = portfolio.get("cash", 0)
    for holding in portfolio.get("holdings", []):
        if holding["ticker"] == latest_ticker:
            holding["current_price"] = latest_price
            holding["value"] = round(holding["shares"] * latest_price, 2)
        total_value += holding.get("value", 0)
    portfolio["total_value"] = round(total_value, 2)


def update_prices(
    agent_id: str,
    price_updates: Dict[str, float],
    source: str = "unknown",
    fetched_at: Optional[str] = None,
) -> Dict:
    """
    市場価格の更新をポートフォリオに反映する

    Args:
        agent_id: エージェントID
        price_updates: {ticker: new_price} の辞書
        source: 株価データの取得元（"alpaca" | "finnhub" | "yfinance" | "alpha_vantage" | "mock"）
        fetched_at: 株価取得時刻（ISO 8601）。省略時は現在時刻。
    """
    portfolio = get_or_init_portfolio(agent_id)
    prev_value = portfolio.get("total_value", 0)
    timestamp = fetched_at or datetime.now(timezone.utc).isoformat()

    holdings = portfolio.get("holdings", [])
    total_holdings_value = 0

    for holding in holdings:
        ticker = holding["ticker"]
        if ticker in price_updates:
            new_price = price_updates[ticker]
            # 前回値を残して前日比チェックに使う
            old_price = holding.get("current_price")
            if old_price is not None:
                holding["prev_price"] = old_price
            holding["current_price"] = new_price
            holding["value"] = round(holding["shares"] * new_price, 2)
            holding["gain_pct"] = round(
                (new_price - holding["avg_cost"]) / holding["avg_cost"] * 100, 2
            )
            holding["price_updated_at"] = timestamp
            holding["price_source"] = source
        total_holdings_value += holding.get("value", 0)

    new_total = portfolio.get("cash", 0) + total_holdings_value
    daily_pnl = round(new_total - prev_value, 2)

    portfolio["total_value"] = round(new_total, 2)
    portfolio["holdings"] = holdings
    portfolio["price_updated_at"] = timestamp
    portfolio["price_source"] = source
    if "performance" not in portfolio:
        portfolio["performance"] = {}
    portfolio["performance"]["daily_pnl"] = daily_pnl

    Storage.save_portfolio(agent_id, portfolio)
    return portfolio


def get_portfolio_summary(agent_id: str) -> Dict:
    """ポートフォリオのサマリーを返す"""
    portfolio = get_or_init_portfolio(agent_id)
    holdings = portfolio.get("holdings", [])
    total_value = portfolio.get("total_value", 0)
    cash = portfolio.get("cash", 0)

    return {
        "agent_id": agent_id,
        "total_value": total_value,
        "cash": cash,
        "cash_pct": round(cash / total_value * 100, 1) if total_value > 0 else 0,
        "holdings_count": len(holdings),
        "performance": portfolio.get("performance", {}),
        "top_holding": (
            max(holdings, key=lambda h: h.get("value", 0)) if holdings else None
        ),
    }
