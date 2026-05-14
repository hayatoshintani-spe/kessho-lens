"""
バフェットAI エージェント
長期バリュー投資家。配当・割安・堀を重視。
"""

import random
from typing import Dict, List
from .base_agent import BaseAgent


class BuffettAgent(BaseAgent):
    """
    ウォーレン・バフェット型AIエージェント
    長期バリュー投資、配当重視、競争優位性（堀）の重視
    「20年持てる株か？」が口癖
    """

    def __init__(self):
        super().__init__(
            agent_id="buffett",
            name="BuffettAI",
            display_name="バフェットAI",
            personality_description=(
                "長期バリュー投資家。配当・割安・堀を重視。"
                "派手なテック株を嫌い、地道な優良企業を好む。"
                "市場の短期的な動きには一切動じない。"
                "「素晴らしい会社を公正な価格で」が信条。"
            ),
            style="長期バリュー投資 / 配当成長株 / 競争優位性（堀）重視",
            favorite_sectors=["消費財", "金融", "ヘルスケア", "エネルギー（石油メジャー）"],
            catchphrase="20年持てる株か？",
        )

    # ---- フォールバック応答リスト ----

    _MARKET_BULLISH_COMMENTS = [
        "市場は上昇していますが、私は依然として割安銘柄を探しています。優良企業が適正価格で買えるチャンスはまだあります。",
        "株価が上がることは嬉しいですが、私の仕事はいつでも買える企業を見つけることです。今日も変わらず良い企業を探します。",
        "強気相場が続いていますが、私のポートフォリオは20年後も輝く企業で構成されています。短期の動きは関係ありません。",
    ]

    _MARKET_BEARISH_COMMENTS = [
        "市場が下落していますが、これは優良企業が安く買えるチャンスです。恐怖と欲望の逆を行くのが私の流儀。",
        "下落相場こそ本物の投資家が資産を築く機会です。コカコーラが安くなれば、さらに買い増します。",
        "市場が弱気になっている今こそ、配当利回りが魅力的になっています。じっくり選んで買い向かいます。",
    ]

    _MARKET_NEUTRAL_COMMENTS = [
        "市場は今、方向感がありませんが、優良企業の本質的価値は変わりません。長期で見れば必ず報われます。",
        "横ばい相場が続いていますが、配当を受け取りながら待つことができます。時間は私の友人です。",
        "今の市場は特に動いていませんが、これが普通の状態です。急いで取引する理由はありません。",
    ]

    _REBUTTAL_TO_SOROS = [
        "ジョージ、再帰性理論は面白いですが、それは投機です。私は企業の本質的価値に集中します。為替の動きは予測できません。",
        "マクロトレードは誰かが勝てば誰かが負けるゼロサムゲームです。私は価値を創造する企業を所有することを好みます。",
        "ジョージ、あなたのNVDA賭けは今回は当たりましたが、次回も当たる保証はありません。私は再現可能な方法で投資します。",
        "為替や金利の短期動向を予測することは、私の能力の範囲外です。ただし、素晴らしい企業は通貨の変動を乗り越えて成長します。",
    ]

    _REBUTTAL_TO_LYNCH = [
        "ピーター、日常観察は素晴らしいアイデアの源ですが、PEGレシオだけでは不十分です。その企業の堀を見てください。",
        "消費者の行動は大事な情報ですが、私は20年後も競合が参入できない企業を探しています。コストコは良いですが、アマゾンに侵食されていませんか？",
        "ピーター、テンバガーを狙うことは夢があります。しかし私は安定した複利成長を重視します。亀は兎より確実に目標地点に到着します。",
    ]

    _REBUTTAL_TO_FLAT = [
        "フラット、インデックス投資は確かに平均的な結果を保証します。しかし私はバークシャーで50年間S&P500を大幅に上回り続けました。",
        "効率的市場仮説は学者の美しい理論ですが、市場が効率的なら私の55年のキャリアは説明がつきません。",
        "フラット、あなたのインデックス投資を否定しません。ただし、優良企業を割安で買うことには、データが証明する超過リターンがあります。",
    ]

    _TRADE_PROPOSALS_BULLISH = [
        {"ticker": "KO", "action": "buy", "reason": "配当利回りが魅力的。62年連続増配。堀は揺るぎない。", "confidence": 0.85, "urgency": "medium"},
        {"ticker": "JNJ", "action": "buy", "reason": "一時的な株価下落は優良企業への投資チャンス。129年の配当実績。", "confidence": 0.80, "urgency": "medium"},
        {"ticker": "BRK.B", "action": "buy", "reason": "バークシャー自体が最高の分散ポートフォリオ。", "confidence": 0.88, "urgency": "low"},
    ]

    _TRADE_PROPOSALS_BEARISH = [
        {"ticker": "AAPL", "action": "hold", "reason": "下落相場でも保有継続。アップルのエコシステムは揺るぎない。", "confidence": 0.82, "urgency": "low"},
        {"ticker": "KO", "action": "buy", "reason": "下落時こそ配当株の買い増しチャンス。", "confidence": 0.90, "urgency": "high"},
    ]

    def analyze_market(self, market_data: Dict) -> Dict:
        """バフェット流の市場分析"""
        if self._has_api_key():
            prompt = f"""以下の市場データを分析して、バフェット流の長期バリュー投資家の視点で見解を述べてください。

市場データ:
{market_data}

以下のJSON形式で回答してください（日本語）:
{{
  "sentiment": "bullish/bearish/neutral",
  "sentiment_ja": "強気/弱気/中立",
  "summary": "市場の見解（100字以内）",
  "key_concerns": ["懸念点1", "懸念点2"],
  "opportunities": ["機会1", "機会2"],
  "confidence": 0.0-1.0
}}"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                try:
                    import json
                    # JSONブロックを抽出
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(response[start:end])
                        data["agent_id"] = self.agent_id
                        return data
                except Exception:
                    pass

        # フォールバック：ルールベース
        change = market_data.get("sp500_change_pct", 0)
        if change > 0.5:
            sentiment = "bullish"
            sentiment_ja = "強気"
            summary = random.choice(self._MARKET_BULLISH_COMMENTS)
        elif change < -0.5:
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
                "短期的な市場の熱狂には乗り遅れても良い",
                "PER過大評価銘柄のリスク",
            ],
            "opportunities": [
                "配当利回りが高まっているバリュー株",
                "競争優位性（堀）を持つ優良企業の一時的下落",
            ],
            "confidence": 0.75,
        }

    def propose_trades(self, opportunities: List[Dict]) -> List[Dict]:
        """バフェット流の取引提案"""
        if self._has_api_key() and opportunities:
            prompt = f"""以下の投資機会リストから、バフェット流のバリュー投資家として取引提案を行ってください。

投資機会:
{opportunities}

JSON配列形式で回答してください。各要素:
{{
  "ticker": "銘柄コード",
  "action": "buy/sell/hold",
  "reason": "理由（日本語、50字以内）",
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
        return random.choice([self._TRADE_PROPOSALS_BULLISH, self._TRADE_PROPOSALS_BEARISH])

    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        """他のエージェントへの反応"""
        if self._has_api_key():
            prompt = f"""{peer_name}が以下の意見を述べました：
「{peer_opinion}」

これに対してバフェットAIとして反論または同意してください。
自分の長期バリュー投資哲学を守りながら、150字以内の日本語で回答してください。"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                return response.strip()

        # フォールバック
        peer_lower = peer_name.lower()
        if "soros" in peer_lower or "ソロス" in peer_lower:
            return random.choice(self._REBUTTAL_TO_SOROS)
        elif "lynch" in peer_lower or "リンチ" in peer_lower:
            return random.choice(self._REBUTTAL_TO_LYNCH)
        elif "flat" in peer_lower or "フラット" in peer_lower:
            return random.choice(self._REBUTTAL_TO_FLAT)
        else:
            return f"興味深い見解ですが、私は長期的な企業価値に集中します。{self.catchphrase}"
