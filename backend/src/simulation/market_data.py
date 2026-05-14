"""
市場データモジュール
Alpha Vantage / Finnhub APIからリアルデータを取得、
APIキーがない場合はモックデータを返す
"""

import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx


# モック市場データのベース値
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

# マクロテーマのリスト
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


def _add_random_variation(base_price: float, max_pct: float = 3.0) -> float:
    """基準価格にランダムな変動を加える"""
    variation = random.uniform(-max_pct, max_pct) / 100
    return round(base_price * (1 + variation), 2)


async def get_market_data() -> Dict:
    """
    市場データを取得する
    APIキーがある場合は実データ、ない場合はモックデータを返す
    """
    alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    if alpha_key:
        try:
            return await _fetch_alpha_vantage(alpha_key)
        except Exception as e:
            print(f"Alpha Vantage APIエラー: {e}")

    if finnhub_key:
        try:
            return await _fetch_finnhub(finnhub_key)
        except Exception as e:
            print(f"Finnhub APIエラー: {e}")

    return _get_mock_market_data()


async def _fetch_alpha_vantage(api_key: str) -> Dict:
    """Alpha Vantage APIから市場データを取得"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # S&P500のデータを取得
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": "SPY",
            "apikey": api_key,
        }
        response = await client.get(url, params=params)
        data = response.json()

        quote = data.get("Global Quote", {})
        spy_price = float(quote.get("05. price", 528.70))
        spy_change = float(quote.get("10. change percent", "0.5%").replace("%", ""))

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "alpha_vantage",
            "sp500_price": spy_price,
            "sp500_change_pct": spy_change,
            "market_theme": random.choice(_MACRO_THEMES),
            "fed_signals": "neutral",
            "tickers": _get_mock_tickers(),
        }


async def _fetch_finnhub(api_key: str) -> Dict:
    """Finnhub APIから市場データを取得"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"https://finnhub.io/api/v1/quote"
        headers = {"X-Finnhub-Token": api_key}
        params = {"symbol": "SPY"}
        response = await client.get(url, headers=headers, params=params)
        data = response.json()

        current = data.get("c", 528.70)
        prev_close = data.get("pc", 526.0)
        change_pct = ((current - prev_close) / prev_close) * 100 if prev_close else 0

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "finnhub",
            "sp500_price": current,
            "sp500_change_pct": round(change_pct, 2),
            "market_theme": random.choice(_MACRO_THEMES),
            "fed_signals": "neutral",
            "tickers": _get_mock_tickers(),
        }


def _get_mock_tickers() -> List[Dict]:
    """モックティッカーデータを生成"""
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
    """モック市場データを返す"""
    # ランダムな市場状況を生成
    sp500_change = round(random.uniform(-1.5, 1.5), 2)
    sp500_base = 5284.31
    sp500_price = round(sp500_base * (1 + sp500_change / 100), 2)

    fed_signals_options = ["dovish", "neutral", "hawkish"]
    fed_weights = [0.3, 0.5, 0.2]
    fed_signals = random.choices(fed_signals_options, weights=fed_weights)[0]

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
    """本日の主要な値動き銘柄"""
    tickers = list(_MOCK_TICKERS.keys())
    gainers = random.sample(tickers, 3)
    losers = random.sample([t for t in tickers if t not in gainers], 3)

    return {
        "gainers": [
            {
                "ticker": t,
                "name": _MOCK_TICKERS[t]["name"],
                "change_pct": round(random.uniform(2.0, 10.0), 2),
            }
            for t in gainers
        ],
        "losers": [
            {
                "ticker": t,
                "name": _MOCK_TICKERS[t]["name"],
                "change_pct": round(random.uniform(-8.0, -2.0), 2),
            }
            for t in losers
        ],
    }


def _get_economic_calendar() -> List[Dict]:
    """今後の経済指標カレンダー"""
    return [
        {"event": "米小売売上高", "importance": "high", "timing": "本日15:30"},
        {"event": "FRB理事発言", "importance": "medium", "timing": "本日21:00"},
        {"event": "EU GDP速報値", "importance": "high", "timing": "明日17:00"},
    ]


def get_ticker_info(ticker: str) -> Optional[Dict]:
    """特定銘柄の情報を返す"""
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
