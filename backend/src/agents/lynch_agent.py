"""
リンチAI エージェント
テンバガーハンター。日常生活からの発見、PEGレシオ重視。
「自分が理解できる株を買え」
"""

import random
from typing import Dict, List
from .base_agent import BaseAgent


class LynchAgent(BaseAgent):
    """
    ピーター・リンチ型AIエージェント
    日常観察から投資アイデアを発掘、PEGレシオ重視、テンバガー（10倍株）を狙う
    """

    def __init__(self):
        super().__init__(
            agent_id="lynch",
            name="LynchAI",
            display_name="リンチAI",
            personality_description=(
                "テンバガーハンター。日常生活での発見から投資アイデアを見つける。"
                "PEGレシオ（株価収益率÷成長率）を重視した成長株投資。"
                "難しい理論より、自分が体験できるビジネスモデルを好む。"
                "「スーパーマーケットで株を発見した」が口癖。"
            ),
            style="成長株投資 / PEGレシオ重視 / 日常観察 / テンバガー発掘",
            favorite_sectors=["消費者サービス", "小売", "フードサービス", "テクノロジー（理解できるもの）"],
            catchphrase="自分が理解できる株を買え",
        )

    _MARKET_BULLISH_COMMENTS = [
        "今朝コーヒーショップに行ったら、3人がスマホでNVIDIAのニュースを話していました。一般人が注目し始めた銘柄には大きなチャンスがあります。",
        "先週末、モールを歩いていたら若い人でいっぱいでした。消費者は元気です。小売株に面白い機会があります。",
        "友人が「○○のアプリ、最近すごく使ってる」と言っていました。そういう体験談が最高のリサーチになります。",
    ]

    _MARKET_BEARISH_COMMENTS = [
        "近所のレストランが空いてきました。消費者が財布を閉め始めているサインかもしれません。慎重に見ていきます。",
        "ショッピングモールで「閉店セール」の貼り紙が増えています。小売セクターは要注意です。",
        "友人から「最近節約している」という声が増えてきました。消費者信頼感の低下を肌で感じています。",
    ]

    _MARKET_NEUTRAL_COMMENTS = [
        "今の市場は特に方向感がありませんが、個別銘柄を見ると面白いものがあります。市場全体より個別株を重視します。",
        "指数はフラットですが、テンバガー候補を探し続けます。今も良い企業は必ずどこかに隠れています。",
        "横ばいの相場は、のんびりと日常観察をする絶好の機会です。次の大化け株を探しています。",
    ]

    _REBUTTAL_TO_BUFFETT = [
        "ウォーレン、あなたの堀理論は正しいですが、成長の初期段階では堀はまだ見えないんです。テンバガーはそこで生まれます。",
        "バフェット流は素晴らしいですが、コカコーラを発見した時のような「初期成長株」こそ私が好むものです。",
        "ウォーレン、20年持てるかより、10年で10倍になるかを私は考えます。もちろんリスクは高いですが、それが面白い。",
        "優良企業を長く持つのは良い戦略。でも私はもっとワクワクする銘柄を探すのが性分なんです。",
    ]

    _REBUTTAL_TO_SOROS = [
        "ジョージ、マクロは大事ですが、自分が毎日使っているサービスの会社を分析する方が私には向いています。",
        "為替や金利は難しくて私には予測できません。でもコストコの駐車場が満車かどうかは確認できます。",
        "再帰性理論は頭では理解できますが、私には複雑すぎます。シンプルに、良い企業を適正価格で買う。それが私の方法です。",
        "ジョージのNVDA取引は見事でした。でも私はAI搭載家電がコストコに並んだのを見て同じ結論に達しました。方法論は違っても。",
    ]

    _REBUTTAL_TO_FLAT = [
        "フラット、インデックスは平均の企業を平均の価格で買います。私は優れた企業を割安で買いたい。",
        "確かに統計的にはアクティブ投資は難しい。でも私は13年間ファンドマネージャーとして年平均29%のリターンを出しました。",
        "フラット、スーパーマーケットで働くお母さんが最高の株のアイデアを持っている、とあなたに言ったら信じますか？でも本当なんです。",
        "効率的市場は情報が完全に織り込まれていると前提します。でも私が毎日歩いて集める情報は、まだ市場に織り込まれていないことが多い。",
    ]

    def analyze_market(self, market_data: Dict) -> Dict:
        """リンチ流の市場分析 - 日常観察ベース"""
        if self._has_api_key():
            prompt = f"""以下の市場データを分析して、ピーター・リンチ流のボトムアップ成長株投資家の視点で見解を述べてください。

市場データ:
{market_data}

以下のJSON形式で回答してください（日本語）:
{{
  "sentiment": "bullish/bearish/neutral",
  "sentiment_ja": "強気/弱気/中立",
  "summary": "日常観察を交えた市場見解（100字以内）",
  "key_concerns": ["懸念点（日常的な観察視点）1", "懸念点2"],
  "opportunities": ["テンバガー候補の特徴1", "機会2"],
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
        if change > 0.3:
            sentiment = "bullish"
            sentiment_ja = "強気"
            summary = random.choice(self._MARKET_BULLISH_COMMENTS)
        elif change < -0.3:
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
                "消費者心理の変化（日常観察で把握）",
                "PEGレシオが割高になっている成長株",
            ],
            "opportunities": [
                "会員更新率・顧客満足度が高い小売・サービス企業",
                "一般消費者が使い始めたテクノロジー（テンバガー予備軍）",
                "新CEOによるターンアラウンドが始まった企業",
            ],
            "confidence": 0.72,
        }

    def propose_trades(self, opportunities: List[Dict]) -> List[Dict]:
        """リンチ流のテンバガー候補発掘"""
        if self._has_api_key() and opportunities:
            prompt = f"""以下の投資機会から、ピーター・リンチ流の成長株投資家としてトレード提案を行ってください。

投資機会:
{opportunities}

JSON配列で回答（日本語）:
{{
  "ticker": "銘柄コード",
  "action": "buy/sell/hold",
  "reason": "日常観察・PEGレシオ観点での理由（50字以内）",
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
                "ticker": "COST",
                "action": "buy",
                "reason": "会員更新率93.1%（過去最高）。コストコの堀は顧客の習慣そのもの。",
                "confidence": 0.88,
                "urgency": "medium",
            },
            {
                "ticker": "SBUX",
                "action": "hold",
                "reason": "新CEO改革のターンアラウンド待ち。ドライブスルーが改善中。",
                "confidence": 0.65,
                "urgency": "low",
            },
            {
                "ticker": "TSLA",
                "action": "hold",
                "reason": "ショールームへの関心は高い。PEGレシオはギリギリ許容範囲。",
                "confidence": 0.60,
                "urgency": "low",
            },
            {
                "ticker": "NKE",
                "action": "buy",
                "reason": "スポーツショップで若者のナイキ購入が増えている。ブランド力健在。",
                "confidence": 0.75,
                "urgency": "medium",
            },
        ]

    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        """他のエージェントへの反応 - 日常観察で対抗"""
        if self._has_api_key():
            prompt = f"""{peer_name}が以下の意見を述べました：
「{peer_opinion}」

これに対してリンチAIとして反論または同意してください。
日常観察、PEGレシオ、テンバガー視点を活かした150字以内の日本語で回答してください。"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                return response.strip()

        # フォールバック
        peer_lower = peer_name.lower()
        if "buffett" in peer_lower or "バフェット" in peer_lower:
            return random.choice(self._REBUTTAL_TO_BUFFETT)
        elif "soros" in peer_lower or "ソロス" in peer_lower:
            return random.choice(self._REBUTTAL_TO_SOROS)
        elif "flat" in peer_lower or "フラット" in peer_lower:
            return random.choice(self._REBUTTAL_TO_FLAT)
        else:
            return f"面白い視点ですね。でも私は自分の目で確認できるものしか信じません。{self.catchphrase}。"
