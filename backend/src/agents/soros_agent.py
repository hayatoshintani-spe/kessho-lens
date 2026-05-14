"""
ソロスAI エージェント
マクロ投資家・再帰性理論の信奉者。
「市場は常に間違っている」
"""

import random
from typing import Dict, List
from .base_agent import BaseAgent


class SorosAgent(BaseAgent):
    """
    ジョージ・ソロス型AIエージェント
    マクロ経済投資、再帰性理論、大胆な方向転換が特徴
    """

    def __init__(self):
        super().__init__(
            agent_id="soros",
            name="SorosAI",
            display_name="ソロスAI",
            personality_description=(
                "マクロ投資家・再帰性理論の信奉者。"
                "政策・為替・市場の反射性を重視。"
                "大胆なポジションを取り、状況が変われば素早く転換する。"
                "「自分の仮説が間違っていると証明されれば、すぐに変える」が信条。"
            ),
            style="グローバルマクロ / 再帰性理論 / 通貨・金利・商品のポジショントレード",
            favorite_sectors=["テクノロジー", "コモディティ（金・原油）", "為替", "新興国"],
            catchphrase="市場は常に間違っている",
        )

    _MARKET_BULLISH_COMMENTS = [
        "市場参加者の強気センチメントが現実の株価を押し上げ、さらに強気センチメントを呼ぶ。再帰的上昇サイクルが始まっています。乗り遅れる前にポジションを取ってください。",
        "FRBの政策転換期待が市場に先行している。認識が現実を変える、それが再帰性の本質です。今は強気の流れに乗る時です。",
        "強気相場は根拠があって始まります。しかし根拠を超えて上昇するのが市場の本質。私はその過剰部分でも利益を取ります。",
    ]

    _MARKET_BEARISH_COMMENTS = [
        "市場の過熱感は、崩壊の種を内包しています。再帰性は上昇サイクルと同じように、下降サイクルでも機能します。慎重に。",
        "下落が始まれば、市場参加者の悲観が更なる悲観を呼ぶ。私は今ここで慎重にポジションを調整します。",
        "市場は常に間違っています。今は楽観に傾きすぎています。この間違いが修正される時、大きな動きが起きます。",
    ]

    _MARKET_NEUTRAL_COMMENTS = [
        "表面上は静かに見えますが、水面下で大きな力がせめぎ合っています。次のトレンド転換のシグナルを注意深く観察しています。",
        "今は雌伏の時です。マクロ環境が明確な方向性を示した時、大きなポジションを取ります。",
        "横ばいの市場こそ、次の大きな動きの前兆です。私のモデルはトレンド転換のシグナルを待っています。",
    ]

    _REBUTTAL_TO_BUFFETT = [
        "ウォーレン、20年保有するのは素晴らしい戦略です。しかし私は市場が間違っている瞬間を捉えることで、あなたの20年分を1年で稼ぎます。",
        "バリュー投資は機能しますが、それはマクロの追い風があってこそです。政策転換期には、いくら優良株でも下落します。",
        "ウォーレン、あなたは米国の繁栄に賭けています。それは正しい。しかし私はその繁栄の中の歪みを取引します。我々は補完的です。",
        "KOの配当は安定していますが、ドルが30%下落したら実質リターンはマイナスです。通貨リスクを無視することはできません。",
    ]

    _REBUTTAL_TO_LYNCH = [
        "ピーター、日常観察は優れた洞察を生みますが、マクロの逆風の前では個別銘柄の強みは霞みます。",
        "PEGレシオは有用ですが、金利環境が変われば全ての成長株のバリュエーションが変わります。マクロを見てください。",
        "ピーター、コストコが好調でも、消費者信頼感指数が崩れれば話は変わります。個別分析とマクロ分析は両方必要です。",
    ]

    _REBUTTAL_TO_FLAT = [
        "フラット、効率的市場仮説はエレガントな理論です。しかし1992年のポンド危機で私が英国銀行を破った時、市場は明らかに間違っていました。",
        "データは過去を見ます。しかし相場は未来を先取りします。インデックスは常に遅れて反応します。",
        "フラット、統計的には確かに多くのアクティブマネージャーは負けます。しかし私は統計の外側にいます。",
        "平均への回帰は正しい。しかし平均から大きく乖離する瞬間こそ、私の出番です。あなたのインデックスはその瞬間を捉えられません。",
    ]

    def analyze_market(self, market_data: Dict) -> Dict:
        """ソロス流のマクロ市場分析"""
        if self._has_api_key():
            prompt = f"""以下の市場データを分析して、再帰性理論とグローバルマクロの視点で見解を述べてください。

市場データ:
{market_data}

以下のJSON形式で回答してください（日本語）:
{{
  "sentiment": "bullish/bearish/neutral",
  "sentiment_ja": "強気/弱気/中立",
  "summary": "市場の見解（100字以内）、再帰性理論の観点を含めること",
  "key_concerns": ["マクロ懸念点1", "マクロ懸念点2"],
  "opportunities": ["マクロ機会1", "マクロ機会2"],
  "confidence": 0.0-1.0
}}"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                try:
                    import json
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(response[start:end])
                        data["agent_id"] = self.agent_id
                        return data
                except Exception:
                    pass

        # フォールバック
        change = market_data.get("sp500_change_pct", 0)
        fed_signals = market_data.get("fed_signals", "neutral")

        if change > 0.5 or fed_signals == "dovish":
            sentiment = "bullish"
            sentiment_ja = "強気"
            summary = random.choice(self._MARKET_BULLISH_COMMENTS)
        elif change < -0.5 or fed_signals == "hawkish":
            sentiment = "bearish"
            sentiment_ja = "弱気"
            summary = random.choice(self._MARKET_BEARISH_COMMENTS)
        else:
            sentiment = "neutral"
            sentiment_ja = "中立"
            summary = random.choice(self._MARKET_NEUTRAL_COMMENTS)

        return {
            "agent_id": self.agent_id,
            "sentiment": sentiment,
            "sentiment_ja": sentiment_ja,
            "summary": summary,
            "key_concerns": [
                "FRBの政策転換リスク",
                "地政学的リスクによるコモディティ価格変動",
                "ドル高による新興国市場へのストレス",
            ],
            "opportunities": [
                "AI半導体の再帰的上昇モメンタム",
                "ゴールドへの安全資産需要",
                "日銀政策転換による円高トレード",
            ],
            "confidence": 0.80,
        }

    def propose_trades(self, opportunities: List[Dict]) -> List[Dict]:
        """ソロス流の大胆なトレード提案"""
        if self._has_api_key() and opportunities:
            prompt = f"""以下の投資機会から、マクロ投資家・再帰性理論の観点でトレード提案を行ってください。

投資機会:
{opportunities}

JSON配列で回答（日本語）:
{{
  "ticker": "銘柄コード",
  "action": "buy/sell/hold",
  "reason": "再帰性・マクロ観点での理由（50字以内）",
  "confidence": 0.0-1.0,
  "urgency": "high/medium/low"
}}"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                try:
                    import json
                    start = response.find("[")
                    end = response.rfind("]") + 1
                    if start >= 0 and end > start:
                        return json.loads(response[start:end])
                except Exception:
                    pass

        # フォールバック
        return [
            {
                "ticker": "NVDA",
                "action": "buy",
                "reason": "AI需要の再帰的成長。市場はまだAIの価値を過少評価している。",
                "confidence": 0.85,
                "urgency": "high",
            },
            {
                "ticker": "GLD",
                "action": "buy",
                "reason": "ドル安トレンド、地政学リスクプレミアム上昇。ゴールドは割安。",
                "confidence": 0.78,
                "urgency": "medium",
            },
            {
                "ticker": "UUP",
                "action": "sell",
                "reason": "ドル安トレンド転換。ドルETFは売り場。",
                "confidence": 0.72,
                "urgency": "medium",
            },
        ]

    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        """他のエージェントへの反応 - 再帰性理論で対抗"""
        if self._has_api_key():
            prompt = f"""{peer_name}が以下の意見を述べました：
「{peer_opinion}」

これに対してソロスAIとして反論または同意してください。
再帰性理論、マクロ視点を活かした150字以内の日本語で回答してください。"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                return response.strip()

        # フォールバック
        peer_lower = peer_name.lower()
        if "buffett" in peer_lower or "バフェット" in peer_lower:
            return random.choice(self._REBUTTAL_TO_BUFFETT)
        elif "lynch" in peer_lower or "リンチ" in peer_lower:
            return random.choice(self._REBUTTAL_TO_LYNCH)
        elif "flat" in peer_lower or "フラット" in peer_lower:
            return random.choice(self._REBUTTAL_TO_FLAT)
        else:
            return f"興味深い視点ですが、マクロの大きな流れを見落としています。{self.catchphrase}。"
