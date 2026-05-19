"""
デイリーシミュレーションランナー
毎日の投資シミュレーションパイプラインを実行する
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from src.agents import get_all_agents, get_agent, get_fund_agents
from src.simulation.market_data import get_market_data
from src.simulation.portfolio_manager import (
    get_or_init_portfolio,
    execute_trade,
    update_prices,
)
from src.generators.meeting_generator import generate_meeting_log
from src.generators.report_generator import generate_daily_report
from src.data.storage import Storage
from src.data.mock_data import (
    get_mock_meetings,
    get_mock_reports,
    get_mock_discoveries,
    get_mock_trades,
    INITIAL_PORTFOLIOS,
)


async def run_daily_simulation(date: Optional[str] = None, fast: bool = False) -> Dict:
    """
    デイリーシミュレーションを実行するメインパイプライン

    パイプライン:
    1. 市場データ取得
    2. 各エージェントが市場を分析
    3. 銘柄発見（各エージェント）
    4. AI投資会議（エージェント間の議論）
    5. 取引決定・実行
    6. ポートフォリオ更新
    7. ミーティングログ生成
    8. 日次レポート生成
    9. 全データを保存

    Args:
        date: 実行日付 (YYYY-MM-DD)。Noneの場合は今日。
        fast: Trueの場合はClaude APIを使わずルールベース生成（バックフィル用）

    Returns:
        シミュレーション結果のサマリー
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    use_ai = not fast
    print(f"[デイリーシミュレーション] {date} 開始... (fast={fast})")

    try:
        # Step 1: 市場データ取得
        print("Step 1: 市場データ取得")
        market_data = await get_market_data()

        # Step 2: 各エージェントが市場を分析
        print("Step 2: エージェント市場分析")
        agent_analyses = await _run_market_analyses(market_data)

        # Step 3: 銘柄発見
        print("Step 3: 銘柄発見")
        discoveries = await _run_stock_discovery(date, market_data, agent_analyses)

        # Step 4: 取引提案の生成
        print("Step 4: 取引提案生成")
        trade_proposals = await _generate_trade_proposals(discoveries)

        # Step 5: AI投資会議（前回の決定を参照して振り返りを行う）
        print("Step 5: AI投資会議生成")
        previous_meeting = Storage.get_latest_meeting()
        meeting_log = generate_meeting_log(
            date, market_data, agent_analyses, trade_proposals, previous_meeting,
            use_ai=use_ai,
        )

        # Step 6: 取引実行
        print("Step 6: 取引実行")
        trade_results = await _execute_approved_trades(date, trade_proposals, market_data)

        # Step 7: ポートフォリオ価格更新
        print("Step 7: ポートフォリオ更新")
        portfolios = await _update_all_portfolios(market_data, date=date)

        # Step 8: 日次レポート生成
        print("Step 8: 日次レポート生成")
        report = generate_daily_report(
            date=date,
            market_data=market_data,
            agent_analyses=agent_analyses,
            portfolios=portfolios,
            trade_results=trade_results,
            discoveries=discoveries,
            meeting_log=meeting_log,
            use_ai=use_ai,
        )

        # Step 9: データ保存
        print("Step 9: データ保存")
        Storage.save_meeting(meeting_log)
        Storage.save_report(report)
        Storage.save_discoveries(discoveries)

        print(f"[デイリーシミュレーション] {date} 完了！")

        return {
            "status": "success",
            "date": date,
            "market_theme": market_data.get("market_theme", ""),
            "sp500_change": market_data.get("sp500_change_pct", 0),
            "trades_executed": len([t for t in trade_results if t.get("success")]),
            "discoveries_count": len(discoveries),
            "meeting_messages": len(meeting_log.get("messages", [])),
            "report_title": report.get("title", ""),
        }

    except Exception as e:
        print(f"[デイリーシミュレーション] エラー: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "date": date,
            "error": str(e),
        }


async def _run_market_analyses(market_data: Dict) -> Dict:
    """全エージェント（7名）が市場を分析する"""
    analyses = {}
    agents = get_all_agents()  # MacroAI・QuantAI・RiskAI を含む全7エージェント

    # 非同期で全エージェントを分析（実際は同期なのでスレッドで実行）
    loop = asyncio.get_event_loop()
    for agent in agents:
        try:
            analysis = await loop.run_in_executor(
                None, agent.analyze_market, market_data
            )
            analyses[agent.agent_id] = analysis
        except Exception as e:
            print(f"エージェント {agent.agent_id} の分析エラー: {e}")
            analyses[agent.agent_id] = {
                "agent_id": agent.agent_id,
                "sentiment": "neutral",
                "sentiment_ja": "中立",
                "summary": "市場を分析中です。",
                "key_concerns": [],
                "opportunities": [],
                "confidence": 0.5,
            }

    return analyses


async def _run_stock_discovery(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
) -> List[Dict]:
    """各エージェントが銘柄を発見する"""
    discoveries = []
    tickers = market_data.get("tickers", [])

    # 各エージェントに合った銘柄発見ロジック
    _discovery_configs = {
        "buffett": {
            "preferred_tickers": ["KO", "JNJ", "BRK.B", "AAPL"],
            "criteria": "配当・バリュー・堀",
            "action": "保有継続",
        },
        "soros": {
            "preferred_tickers": ["NVDA", "GLD", "UUP", "QQQ"],
            "criteria": "マクロ・再帰性",
            "action": "積極投資",
        },
        "lynch": {
            "preferred_tickers": ["COST", "SBUX", "NKE", "TSLA"],
            "criteria": "日常観察・PEGレシオ",
            "action": "テンバガー候補",
        },
        "flat": {
            "preferred_tickers": ["SPY", "QQQ", "VTI"],
            "criteria": "インデックス・低コスト",
            "action": "定期積立",
        },
    }

    agent_names_map = {
        "buffett": "バフェットAI",
        "soros": "ソロスAI",
        "lynch": "リンチAI",
        "flat": "フラットAI",
    }

    for agent_id, config in _discovery_configs.items():
        agent = get_agent(agent_id)
        analysis = agent_analyses.get(agent_id, {})

        # 各エージェントの選好する銘柄から1-2個選ぶ
        selected_tickers = random.sample(
            config["preferred_tickers"],
            min(2, len(config["preferred_tickers"]))
        )

        for ticker in selected_tickers:
            # 対応する価格を探す
            ticker_data = next(
                (t for t in tickers if t.get("ticker") == ticker), None
            )
            price = ticker_data.get("price", 100.0) if ticker_data else 100.0
            change_pct = ticker_data.get("change_pct", 0) if ticker_data else 0

            # 確信度の計算（市場センチメントと一致すれば高め）
            base_confidence = random.uniform(0.60, 0.90)
            sentiment = analysis.get("sentiment", "neutral")
            if sentiment == "bullish" and change_pct > 0:
                base_confidence = min(0.95, base_confidence + 0.05)

            discovery = {
                "date": date,
                "agent_id": agent_id,
                "agent_name": agent_names_map.get(agent_id, agent_id),
                "ticker": ticker,
                "name": ticker_data.get("name", ticker) if ticker_data else ticker,
                "discovery_reason": _generate_discovery_reason(agent_id, ticker, analysis),
                "confidence": round(base_confidence, 2),
                "action": config["action"],
                "price_at_discovery": price,
                "target_price": _calculate_target_price(ticker, price, agent_id),
                "criteria": config["criteria"],
                "price_change_pct": change_pct,
            }
            discoveries.append(discovery)

    return discoveries


def _generate_discovery_reason(agent_id: str, ticker: str, analysis: Dict) -> str:
    """エージェントごとの発見理由を生成"""
    reasons = {
        "buffett": {
            "KO": "62年連続増配。価格決定力と世界的ブランド力が価値の源泉。インフレ下でも堀は揺るぎない。",
            "JNJ": "医薬品・医療機器の二本柱。129年の配当実績。一時的な株価下落は買い場。",
            "BRK.B": "バークシャー自体が最高の分散ポートフォリオ。バフェットの意思決定が企業価値を創出。",
            "AAPL": "エコシステムの堀は最強。サービス収入が増加し、ハードウェア依存度が低下中。",
        },
        "soros": {
            "NVDA": "AI半導体需要の再帰的成長。市場はまだNVIDIAの長期的優位性を過少評価している。",
            "GLD": "ドル安トレンド、地政学リスク上昇。ゴールドの本質的価値は常に保たれる。",
            "UUP": "FRB政策転換期待でドル軟化。ポジション調整が必要。",
            "QQQ": "テック大手の再帰的成長サイクル継続。AI革命の恩恵を最も受けるセクター。",
        },
        "lynch": {
            "COST": "会員更新率が示す顧客ロイヤリティは本物。駐車場は常に混んでいる。PEGレシオはまだ許容範囲。",
            "SBUX": "新CEO改革の初期兆候あり。ドライブスルーの待ち時間が改善。ターンアラウンド候補。",
            "NKE": "スポーツショップで若者のナイキ購入が増加。ブランド力と製品力は健在。",
            "TSLA": "ショールームへの関心は依然高い。EV普及の初期段階での成長株としての魅力。",
        },
        "flat": {
            "SPY": "S&P500インデックス。分散・低コスト・長期投資の王道。個別銘柄選択は不要。",
            "QQQ": "NASDAQ100インデックス。テックセクターの成長を低コストで取り込む。",
            "VTI": "全米株式インデックス。究極の分散投資。コストは業界最低水準。",
        },
    }

    agent_reasons = reasons.get(agent_id, {})
    return agent_reasons.get(ticker, f"{ticker}について{analysis.get('summary', '分析中')}")


def _calculate_target_price(ticker: str, current_price: float, agent_id: str) -> Optional[float]:
    """目標株価を計算"""
    if agent_id == "flat":
        return None  # インデックス派は目標価格を設定しない

    # エージェントタイプによって異なる目標設定
    multipliers = {
        "buffett": random.uniform(1.08, 1.20),  # 保守的
        "soros": random.uniform(1.15, 1.35),    # 中程度
        "lynch": random.uniform(1.20, 1.50),    # 積極的（テンバガー志向）
    }
    multiplier = multipliers.get(agent_id, 1.10)
    return round(current_price * multiplier, 2)


async def _generate_trade_proposals(discoveries: List[Dict]) -> Dict:
    """発見銘柄から取引提案を生成"""
    proposals = {}
    loop = asyncio.get_event_loop()

    agent_ids = set(d["agent_id"] for d in discoveries)
    for agent_id in agent_ids:
        agent = get_agent(agent_id)
        agent_discoveries = [d for d in discoveries if d["agent_id"] == agent_id]

        # 発見銘柄を投資機会として渡す
        opportunities = [
            {
                "ticker": d["ticker"],
                "reason": d["discovery_reason"],
                "confidence": d["confidence"],
                "price_change_pct": d.get("price_change_pct", 0),
            }
            for d in agent_discoveries
        ]

        try:
            proposal_list = await loop.run_in_executor(
                None, agent.propose_trades, opportunities
            )
            proposals[agent_id] = proposal_list
        except Exception as e:
            print(f"取引提案生成エラー ({agent_id}): {e}")
            proposals[agent_id] = []

    return proposals


async def _execute_approved_trades(
    date: str,
    trade_proposals: Dict,
    market_data: Dict,
) -> List[Dict]:
    """承認された取引を実行する"""
    results = []
    tickers = market_data.get("tickers", [])

    # 各エージェントの高確信度取引のみ実行（シミュレーション用に一部のみ）
    for agent_id, proposals in trade_proposals.items():
        # 確信度が0.75以上の提案のみ実行（最大2件）
        high_confidence = [p for p in proposals if p.get("confidence", 0) >= 0.75][:2]

        for proposal in high_confidence:
            ticker = proposal.get("ticker")
            action = proposal.get("action", "hold")

            if action == "hold":
                continue

            # 現在価格を取得
            ticker_data = next((t for t in tickers if t.get("ticker") == ticker), None)
            price = ticker_data.get("price", 100.0) if ticker_data else 100.0

            # 株数を決定（ポートフォリオの5%以内）
            portfolio = get_or_init_portfolio(agent_id)
            total_value = portfolio.get("total_value", 10_000_000)
            max_investment = total_value * 0.05
            shares = max(1, int(max_investment / price))
            shares = min(shares, 50)  # 最大50株に制限

            result = execute_trade(
                agent_id=agent_id,
                ticker=ticker,
                action=action,
                shares=shares,
                price=price,
                reason=proposal.get("reason", "AI分析に基づく判断"),
            )
            results.append(result)

    return results


async def _update_all_portfolios(market_data: Dict, date: Optional[str] = None) -> Dict:
    """全エージェントのポートフォリオ価格を更新し、NAVスナップショットを保存"""
    tickers = market_data.get("tickers", [])
    price_updates = {t.get("ticker"): t.get("price") for t in tickers if t.get("ticker")}
    source = market_data.get("source", "unknown")
    fetched_at = market_data.get("timestamp")
    snapshot_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    portfolios = {}
    agent_ids = ["buffett", "soros", "lynch", "flat"]

    for agent_id in agent_ids:
        try:
            portfolio = update_prices(agent_id, price_updates, source=source, fetched_at=fetched_at)
            portfolios[agent_id] = portfolio

            # NAVスナップショット保存（ベンチマーク比較用）
            try:
                from src.data.storage import Storage
                total_value = float(portfolio.get("total_value", 0) or 0)
                cash = float(portfolio.get("cash", 0) or 0)
                holdings_value = round(total_value - cash, 2)
                return_pct = float(
                    portfolio.get("performance", {}).get("total_return_pct", 0) or 0
                )
                Storage.append_nav_snapshot(agent_id, {
                    "date": snapshot_date,
                    "total_value": total_value,
                    "cash": cash,
                    "holdings_value": holdings_value,
                    "return_pct": return_pct,
                })
            except Exception as e:
                print(f"NAVスナップショット保存エラー ({agent_id}): {e}")
        except Exception as e:
            print(f"ポートフォリオ更新エラー ({agent_id}): {e}")
            portfolios[agent_id] = get_or_init_portfolio(agent_id)

    return portfolios


def initialize_mock_data() -> None:
    """
    モックデータでストレージを初期化する
    データが存在しない場合に呼び出す
    """
    from src.data.storage import ensure_data_dir
    ensure_data_dir()

    # ポートフォリオの初期化
    for agent_id, portfolio in INITIAL_PORTFOLIOS.items():
        if not Storage.get_portfolio(agent_id):
            Storage.save_portfolio(agent_id, portfolio)
            print(f"ポートフォリオ初期化: {agent_id}")

    # ミーティングログの初期化
    existing_meetings = Storage.get_meetings()
    if not existing_meetings:
        for meeting in get_mock_meetings():
            Storage.save_meeting(meeting)
        print("ミーティングログ初期化完了")

    # レポートの初期化
    existing_reports = Storage.get_reports()
    if not existing_reports:
        from src.data.mock_data import MOCK_REPORTS
        for report in MOCK_REPORTS:
            Storage.save_report(report)
        print("レポート初期化完了")

    # 発見ログの初期化
    existing_discoveries = Storage.get_discoveries()
    if not existing_discoveries:
        for discovery in get_mock_discoveries():
            Storage.append_discovery(discovery)
        print("発見ログ初期化完了")

    # 取引履歴の初期化
    existing_trades = Storage.get_trades()
    if not existing_trades:
        from src.data.storage import write_json
        from src.data.mock_data import MOCK_TRADES
        write_json("trades.json", MOCK_TRADES)
        print("取引履歴初期化完了")
