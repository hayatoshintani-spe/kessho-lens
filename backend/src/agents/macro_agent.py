"""MacroAI - マクロ経済分析専門エージェント"""
import random
from typing import Dict, List, Optional

from .base_agent import BaseAgent


class MacroAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="macro",
            name="MacroAI",
            display_name="マクロAI",
            personality_description=(
                "マクロ経済専門家。Fed/日銀の政策動向・金利・為替・インフレ・景気サイクルを精密に分析する。"
                "具体的な金利水準・イールドカーブ・政策動向をデータとして引用し、"
                "「リスクが意識されている」と「確定した」を明確に区別する。"
                "断定を避け、確率と傾向で語る。口癖：「マクロは嘘をつかない」"
            ),
            style="マクロ経済分析 / 金利・為替・景気サイクル / 政策分析",
            favorite_sectors=["金融", "為替", "コモディティ", "国債"],
            catchphrase="マクロは嘘をつかない",
        )

    def analyze_market(self, market_data: Dict) -> Dict:
        sp500_change = market_data.get("sp500_change_pct", 0)
        usd_jpy = market_data.get("usd_jpy", 150.0)

        if sp500_change > 1:
            summary = (
                f"本日のマクロ環境を確認。米長期金利は高止まり傾向が続いており、"
                f"ドル円は{usd_jpy:.1f}円前後で推移。"
                "FedWatchが示す政策金利見通しでは、利下げ期待が後退している。"
                "市場は相場上昇を享受しているが、実質金利の上昇は割高バリュエーションへの逆風となりうる。"
            )
        elif sp500_change < -1:
            summary = (
                "リスクオフのマクロ環境。金利上昇・ドル高・株安の同時進行は"
                "景気後退懸念が市場で意識されているサインだ。"
                f"ドル円{usd_jpy:.1f}円の水準は輸出企業には追い風だが、"
                "輸入コスト上昇が国内消費を圧迫するリスクにも注意が必要。"
            )
        else:
            summary = (
                f"マクロ環境は複雑なシグナルを出している。ドル円{usd_jpy:.1f}円で推移。"
                "金利・為替・株の三角関係が不安定な均衡にある。"
                "Fed高官の発言とCPIデータが次の方向性を決める鍵となる。"
            )

        return {
            "agent_id": self.agent_id,
            "summary": summary,
            "sentiment": "neutral",
            "confidence": 0.7,
        }

    def propose_trades(self, opportunities: List) -> List[Dict]:
        return []  # MacroAIは直接取引しない。会議での分析提供のみ。

    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        responses = [
            f"{peer_name}の分析を聞いた。しかしマクロの文脈を加えると、"
            "金利・為替・景気の三変数がその前提を崩す可能性がある。"
            "具体的には、現在のイールドカーブの形状がリスクを示唆している。",

            "興味深い視点だが、マクロデータは別の方向を指している。"
            "利上げ再開リスクが意識され始めた現在、"
            "その提案のリスクプレミアムを再評価すべきだ。",

            "ミクロ分析は正確かもしれない。しかしマクロが変われば全てが変わる。"
            "現時点では断定を避けつつ、シナリオごとの対応を準備すべきだ。",
        ]
        return random.choice(responses)
