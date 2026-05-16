"""QuantAI - 定量分析専門エージェント"""
import random
from typing import Dict, List

from .base_agent import BaseAgent


class QuantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="quant",
            name="QuantAI",
            display_name="クオンツAI",
            personality_description=(
                "定量分析専門家。PER/PBR/EV-EBITDA/配当利回り/モメンタム/RSIで銘柄をスコアリングする。"
                "感情・物語・直感を排除し、数字のみで投資判断する。"
                "特に「織り込み度」の定量評価が得意。株価が既にニュースを織り込んでいるかを"
                "バリュエーションの歴史的水準と比較して判断する。口癖：「数字だけが真実だ」"
            ),
            style="定量分析 / バリュエーション / モメンタム / リスク定量化",
            favorite_sectors=["インデックス全般", "割安セクター", "高配当"],
            catchphrase="数字だけが真実だ",
        )

    def analyze_market(self, market_data: Dict) -> Dict:
        sp500_change = market_data.get("sp500_change_pct", 0)
        tickers = market_data.get("tickers", [])

        gainers = sorted([t for t in tickers if t.get("change_pct", 0) > 0],
                         key=lambda x: x.get("change_pct", 0), reverse=True)[:3]
        losers = sorted([t for t in tickers if t.get("change_pct", 0) < 0],
                        key=lambda x: x.get("change_pct", 0))[:3]

        gainer_str = "、".join([f"{t['ticker']}({t['change_pct']:+.1f}%)" for t in gainers])
        loser_str = "、".join([f"{t['ticker']}({t['change_pct']:+.1f}%)" for t in losers])

        summary = (
            f"定量スクリーニング結果。本日の上昇銘柄：{gainer_str}。"
            f"下落銘柄：{loser_str}。"
            f"S&P500の変動率{sp500_change:+.2f}%を基準に各銘柄のベータを考慮すると、"
            "市場コンセンサスから外れた動きをしている銘柄に注目すべきだ。"
            "バリュエーション面では、PERが過去5年平均を20%以上上回る銘柄は"
            "現時点でのニュースを既に相当程度織り込んでいる可能性が高い。"
        )

        return {
            "agent_id": self.agent_id,
            "summary": summary,
            "sentiment": "neutral",
            "confidence": 0.75,
        }

    def propose_trades(self, opportunities: List) -> List[Dict]:
        return []  # QuantAIは直接取引しない。定量分析の提供のみ。

    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        responses = [
            f"{peer_name}の定性分析を数値で検証する。"
            "現在の対象銘柄のPERは過去5年平均比で1.3倍水準。"
            "モメンタムは強いが、RSIが70を超えており短期的には過熱感がある。"
            "数字は現状維持を示している。",

            "感情的な議論は置いておいて、定量的に見てみよう。"
            "この銘柄の株価は過去3ヶ月で30%上昇している。"
            "好材料はかなりの程度織り込まれており、"
            "追加的なアップサイドには業績の大幅な上振れが必要だ。",

            "スコアリングでは、バリュエーション：中立、モメンタム：強い、"
            "需給：やや過熱。総合スコアは買いとも売りとも言いにくい水準。"
            "新規参入よりも既存保有のウェイトを維持する判断が数字的に妥当だ。",
        ]
        return random.choice(responses)
