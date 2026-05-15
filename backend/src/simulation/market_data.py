"""
市場データモジュール

取得優先順位:
  1. yfinance（APIキー不要・全銘柄リアルタイム）
  2. Finnhub（FINNHUB_API_KEY が必要・全銘柄個別取得）
  3. Alpha Vantage（ALPHA_VANTAGE_API_KEY が必要・SPYのみ）
  4. モックデータ（完全フォールバック）
"""

import asyncio
import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx


# 対象銘柄メタ情報（base_price はフォールバック用、実価格はAPIで上書き）
_MOCK_TICKERS = {
    "AAPL": {"name": "Apple Inc.", "base_price": 189.50, "sector": "テクノロジー"},
    "NVDA": {"name": "NVIDIA Corp", "base_price": 875.20, "sector": "半導体"},
    "MSFT": {"name": "Microsoft Corp", "base_price": 415.30, "sector": "テクノロジー"},
    "GOOGL": {"name": "Alphabet Inc.", "base_price": 175.80, "sector": "テクノロジー"},
    "AMZN": {"name": "Amazon.com Inc.", "base_price": 198.40, "sector": "消費者サービス"},
    "META": {"name": "Meta Platforms", "base_price": 513.20, "sector": "ソーシャルメディア"},
    "TSLA": {"name": "Tesla Inc.", "base_price": 248.90, "sector": "電気自動車"},
    "KO": {"name": "Coca-Cola Co", "base_price": 62.30, "sector": "消費財"},
    "JNJ": {"name": "Johnson & Johnson", "base_price": 148.70, "sector": "ヘルスケア"},
    "BRK.B": {"name": "Berkshire Hathaway B", "base_price": 392.10, "sector": "金融"},
    "GLD": {"name": "SPDR Gold Shares", "base_price": 215.40, "sector": "コモディティ"},
    "SPY": {"name": "SPDR S&P 500 ETF", "base_price": 528.70, "sector": "インデックス"},
    "QQQ": {"name": "Invesco QQQ Trust", "base_price": 458.20, "sector": "インデックス"},
    "VTI": {"name": "Vanguard Total Market ETF", "base_price": 248.10, "sector": "インデックス"},
    "COST": {"name": "Costco Wholesale", "base_price": 728.50, "sector": "小売"},
    "SBUX": {"name": "Starbucks Corp", "base_price": 88.40, "sector": "フードサービス"},
    "NKE": {"name": "Nike Inc.", "base_price": 107.80, "sector": "消費者サービス"},
    "UUP": {"name": "Invesco DB USD Index", "base_price": 27.10, "sector": "為替"},
    "TLT": {"name": "iShares 20+ Year Treasury ETF", "base_price": 92.30, "sector": "債券"},
}

_MACRO_THEMES = [
    "FRBの利下げ観測と株式市場への影響",
    "AI半導体バブルとバリュエーション懸念",
    "日銀政策転換と円高トレンド",
    "インフレ再燃とグロース株の調整",
    "地政学リスクとコモディティ価格上昇",
    "消費者信頼感の低下と小売セクター",
    "中国経済減速と新興国市場",
    "クリーンエネルギー転換と化石燃料株",
]

_SYMBOLS = list(_MOCK_TICKERS.keys())


def _add_random_variation(base_price: float, max_pct: float = 3.0) -> float:
    variation = random.uniform(-max_pct, max_pct) / 100
    return round(base_price * (1 + variation), 2)


def _build_result(source: str, tickers: List[Dict], sp500_price: float, sp500_change: float) -> Dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "sp500_price": sp500_price,
        "sp500_change_pct": sp500_change,
        "market_theme": random.choice(_MACRO_THEMES),
        "fed_signals": "neutral",
        "tickers": tickers,
    }


# ─── 1. yfinance（APIキー不要） ────────────────────────────────────────────────

def _sync_fetch_yfinance(symbols: List[str]) -> Optional[Dict]:
    """yfinance で全銘柄を一括取得（同期）"""
    try:
        import yfinance as yf

        # yfinance はピリオドをハイフンに変換 (BRK.B → BRK-B)
        yf_map = {s: s.replace(".", "-") for s in symbols}
        yf_symbols = list(yf_map.values())

        raw = yf.download(
            yf_symbols,
            period="5d",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )

        if raw.empty:
            return None

        close = raw["Close"]
        if len(yf_symbols) == 1:
            close = close.to_frame(yf_symbols[0])

        tickers_data: List[Dict] = []
        for orig_sym, yf_sym in yf_map.items():
            info = _MOCK_TICKERS.get(orig_sym, {})
            base_price = info.get("base_price", 100.0)
            try:
                prices = close[yf_sym].dropna()
                if len(prices) >= 2:
                    price = float(prices.iloc[-1])
                    prev = float(prices.iloc[-2])
                    change_pct = round((price - prev) / prev * 100, 2)
                elif len(prices) == 1:
                    price = float(prices.iloc[-1])
                    change_pct = 0.0
                else:
                    raise ValueError("no data")
            except Exception:
                price = _add_random_variation(base_price, 0.5)
                change_pct = round((price - base_price) / base_price * 100, 2)

            tickers_data.append({
                "ticker": orig_sym,
                "name": info.get("name", orig_sym),
                "sector": info.get("sector", "その他"),
                "price": round(price, 2),
                "change_pct": change_pct,
                "volume": 0,
            })

        spy_col = yf_map.get("SPY", "SPY")
        spy_prices = close.get(spy_col, None)
        if spy_prices is not None and not spy_prices.dropna().empty:
            s = spy_prices.dropna()
            sp500_price = float(s.iloc[-1])
            sp500_prev = float(s.iloc[-2]) if len(s) >= 2 else sp500_price
            sp500_change = round((sp500_price - sp500_prev) / sp500_prev * 100, 2)
        else:
            sp500_price, sp500_change = 528.70, 0.0

        return _build_result("yfinance", tickers_data, sp500_price, sp500_change)

    except Exception as e:
        print(f"[market_data] yfinance error: {e}")
        return None


async def _fetch_yfinance() -> Optional[Dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_fetch_yfinance, _SYMBOLS)


# ─── 2. Finnhub 全銘柄個別取得（APIキーあり） ─────────────────────────────────

async def _fetch_finnhub_all(api_key: str) -> Optional[Dict]:
    """Finnhub で全銘柄を並列取得（60 req/min の無料枠で余裕）"""
    try:
        headers = {"X-Finnhub-Token": api_key}

        async with httpx.AsyncClient(timeout=15.0) as client:
            tasks = [
                client.get(
                    "https://finnhub.io/api/v1/quote",
                    headers=headers,
                    params={"symbol": sym},
                )
                for sym in _SYMBOLS
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        tickers_data: List[Dict] = []
        sp500_price, sp500_change = 528.70, 0.0

        for sym, resp in zip(_SYMBOLS, responses):
            info = _MOCK_TICKERS.get(sym, {})
            base_price = info.get("base_price", 100.0)
            try:
                if isinstance(resp, Exception):
                    raise resp
                data = resp.json()
                current = float(data.get("c", 0))
                prev_close = float(data.get("pc", 0))
                if current <= 0:
                    raise ValueError("invalid price")
                change_pct = round((current - prev_close) / prev_close * 100, 2) if prev_close else 0.0
                price = current
                if sym == "SPY":
                    sp500_price = price
                    sp500_change = change_pct
            except Exception:
                price = _add_random_variation(base_price, 0.5)
                change_pct = round((price - base_price) / base_price * 100, 2)

            tickers_data.append({
                "ticker": sym,
                "name": info.get("name", sym),
                "sector": info.get("sector", "その他"),
                "price": round(price, 2),
                "change_pct": change_pct,
                "volume": 0,
            })

        return _build_result("finnhub", tickers_data, sp500_price, sp500_change)

    except Exception as e:
        print(f"[market_data] Finnhub (all tickers) error: {e}")
        return None


# ─── 3. Alpha Vantage SPYのみ（APIキーあり） ──────────────────────────────────

async def _fetch_alpha_vantage_spy(api_key: str) -> Optional[Dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://www.alphavantage.co/query",
                params={"function": "GLOBAL_QUOTE", "symbol": "SPY", "apikey": api_key},
            )
        data = resp.json()
        quote = data.get("Global Quote", {})
        spy_price = float(quote.get("05. price", 528.70))
        spy_change = float(quote.get("10. change percent", "0.5%").replace("%", ""))
        return _build_result("alpha_vantage", _get_mock_tickers(), spy_price, spy_change)
    except Exception as e:
        print(f"[market_data] Alpha Vantage error: {e}")
        return None


# ─── メイン取得関数 ───────────────────────────────────────────────────────────────

async def get_market_data() -> Dict:
    """市場データを取得する（yfinance → Finnhub → Alpha Vantage → Mock）"""

    # 1. yfinance（APIキー不要）
    result = await _fetch_yfinance()
    if result is not None:
        print(f"[market_data] yfinance: {len(result['tickers'])} 銘柄のリアルタイム価格を取得")
        return result

    # 2. Finnhub（全銘柄個別取得）
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if finnhub_key:
        result = await _fetch_finnhub_all(finnhub_key)
        if result is not None:
            print(f"[market_data] Finnhub: {len(result['tickers'])} 銘柄のリアルタイム価格を取得")
            return result

    # 3. Alpha Vantage（SPYのみ、個別株はモック）
    alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if alpha_key:
        result = await _fetch_alpha_vantage_spy(alpha_key)
        if result is not None:
            print("[market_data] Alpha Vantage: SPYのみリアルタイム、個別株はモック")
            return result

    # 4. モックデータ
    print("[market_data] すべてのリアルタイムソース失敗 → モックデータを使用")
    return _get_mock_market_data()


# ─── モック / フォールバック ───────────────────────────────────────────────────

def _get_mock_tickers() -> List[Dict]:
    tickers = []
    for ticker, info in _MOCK_TICKERS.items():
        base = info["base_price"]
        price = _add_random_variation(base, max_pct=2.0)
        change_pct = round((price - base) / base * 100, 2)
        tickers.append({
            "ticker": ticker,
            "name": info["name"],
            "sector": info["sector"],
            "price": price,
            "change_pct": change_pct,
            "volume": random.randint(1_000_000, 50_000_000),
        })
    return tickers


def _get_mock_market_data() -> Dict:
    sp500_change = round(random.uniform(-1.5, 1.5), 2)
    sp500_price = round(5284.31 * (1 + sp500_change / 100), 2)
    fed_signals = random.choices(["dovish", "neutral", "hawkish"], weights=[0.3, 0.5, 0.2])[0]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
        "sp500_price": sp500_price,
        "sp500_change_pct": sp500_change,
        "nasdaq_change_pct": round(random.uniform(-2.0, 2.0), 2),
        "dow_change_pct": round(random.uniform(-1.0, 1.0), 2),
        "nikkei_change_pct": round(random.uniform(-1.5, 1.5), 2),
        "vix": round(random.uniform(12, 28), 1),
        "gold_price": _add_random_variation(2415.0, 1.0),
        "usd_jpy": round(random.uniform(148.0, 155.0), 2),
        "fed_signals": fed_signals,
        "market_theme": random.choice(_MACRO_THEMES),
        "tickers": _get_mock_tickers(),
        "top_movers": _get_top_movers(),
        "economic_calendar": _get_economic_calendar(),
    }


def _get_top_movers() -> Dict:
    tickers = list(_MOCK_TICKERS.keys())
    gainers = random.sample(tickers, 3)
    losers = random.sample([t for t in tickers if t not in gainers], 3)
    return {
        "gainers": [
            {"ticker": t, "name": _MOCK_TICKERS[t]["name"], "change_pct": round(random.uniform(2.0, 10.0), 2)}
            for t in gainers
        ],
        "losers": [
            {"ticker": t, "name": _MOCK_TICKERS[t]["name"], "change_pct": round(random.uniform(-8.0, -2.0), 2)}
            for t in losers
        ],
    }


def _get_economic_calendar() -> List[Dict]:
    return [
        {"event": "米小売売上高", "importance": "high", "timing": "本日15:30"},
        {"event": "FRB理事発言", "importance": "medium", "timing": "本日21:00"},
        {"event": "EU GDP速報値", "importance": "high", "timing": "明日17:00"},
    ]


def get_ticker_info(ticker: str) -> Optional[Dict]:
    info = _MOCK_TICKERS.get(ticker)
    if not info:
        return None
    price = _add_random_variation(info["base_price"])
    return {
        "ticker": ticker,
        "name": info["name"],
        "sector": info["sector"],
        "price": price,
        "change_pct": round((price - info["base_price"]) / info["base_price"] * 100, 2),
    }
