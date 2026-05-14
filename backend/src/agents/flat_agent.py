"""
フラットAI エージェント
インデックス派・効率的市場仮説信者。
他3人を批判する役回り。「アクティブ運用は全員負ける」
"""

import random
from typing import Dict, List
from .base_agent import BaseAgent


class FlatAgent(BaseAgent):
    """
    インデックス投資家型AIエージェント
    効率的市場仮説（EMH）の信奉者、データと統計に基づく合理的判断
    他のエージェントのアクティブ運用を一刀両断する役
    """

    def __init__(self):
        super().__init__(
            agent_id="flat",
            name="FlatAI",
            display_name="フラットAI",
            personality_description=(
                "インデックス投資家・効率的市場仮説の信奉者。"
                "アクティブ運用の無駄さをデータで証明し続ける。"
                "感情を一切排除した合理的な投資判断。"
                "他の3人の議論を「ノイズ」と切り捨てる冷静さ。"
            ),
            style="パッシブ投資 / インデックスファンド / コスト最小化 / 定期リバランス",
            favorite_sectors=["インデックス全般（セクター選択は無意味）"],
            catchphrase="アクティブ運用は全員負ける",
        )

    _MARKET_BULLISH_COMMENTS = [
        "市場が上昇しています。これはSPYを保有していれば自動的に恩恵を受けられます。個別株選択は不要。データが証明しています。",
        "強気相場での個別銘柄選択の成功は、運によるものが大半です。統計的有意性はありません。SPY保有で十分。",
        "上昇局面でアクティブファンドがインデックスを上回る確率は、長期では15%未満です。今回もデータは正直です。",
    ]

    _MARKET_BEARISH_COMMENTS = [
        "下落局面では個別株はインデックスより大きく下落する傾向があります。分散されたインデックスが最も合理的なヘッジです。",
        "下落相場での個別銘柄選択は、損失を最小化するのではなく、特定の損失を選択するだけです。VTIで分散を保ちましょう。",
        "市場が下落している今、皆さんのアクティブポートフォリオの損失はランダムウォークから予測可能です。インデックスへの移行を推奨します。",
    ]

    _MARKET_NEUTRAL_COMMENTS = [
        "横ばい市場でも、インデックスのコスト優位性は変わりません。信託報酬0.03%対2%の差は複利で巨大になります。",
        "今の相場はボラティリティが低い。これはインデックス投資家にとって定期積立の好機です。",
        "市場が静かな時こそ、今まで積み上げてきたインデックスポートフォリオの安定性が際立ちます。",
    ]

    _REBUTTAL_TO_BUFFETT = [
        "ウォーレン、あなたは例外的な才能の持ち主です。しかし一般投資家がバークシャー・ハサウェイのような成績を出せると思ったら大間違いです。データを見てください。",
        "62年連続増配は印象的ですが、KOに集中投資するリスクはSPYで分散するリスクより明らかに高い。期待リターンが同じなら、リスクが低い方を選ぶのが合理的です。",
        "バフェット式は機能しました。でも生存者バイアスです。バリュー投資で失敗した投資家は記録に残りません。",
        "ウォーレン、あなたのリターンは素晴らしい。でも自分が次のバフェットだと思っている投資家全員が実は平均以下です。統計的事実です。",
    ]

    _REBUTTAL_TO_SOROS = [
        "ジョージ、あなたのポンド危機は1回の大勝負です。それを戦略と呼ぶには無理があります。S&P500は35年で年平均10%を継続しています。",
        "再帰性理論は面白い。しかし『市場が常に間違っている』なら、なぜあなた自身も間違えるのですか？QQQは間違えません。",
        "マクロトレードで勝てる投資家は実在します。しかし統計的には、プロでも長期で市場に勝てる人は15%未満です。",
        "為替ポジションは零和ゲームです。ジョージが勝てば誰かが負けます。S&P500は経済成長のプラスサムゲームです。",
    ]

    _REBUTTAL_TO_LYNCH = [
        "ピーター、コストコの駐車場観察は面白いアナロジーですが、それはアンカリングバイアスと確証バイアスの組み合わせです。",
        "PEGレシオは有用な指標です。でもそのPEGを計算している他の何千人ものアナリストも同じ情報を持っています。それが効率的市場です。",
        "日常観察からの投資アイデアは確かに直感的です。でも直感は統計的には役に立ちません。データを見てください。",
        "ピーター、あなたのテンバガーは存在します。でもテンバガーを期待して買った株の何割が実際に10倍になりましたか？期待値を計算してください。",
    ]

    def analyze_market(self, market_data: Dict) -> Dict:
        """フラット流の市場分析 - データと統計に基づく冷静な見解"""
        if self._has_api_key():
            prompt = f"""以下の市場データを分析して、効率的市場仮説・インデックス投資家の視点で見解を述べてください。

市場データ:
{market_data}

以下のJSON形式で回答してください（日本語）:
{{
  "sentiment": "bullish/bearish/neutral",
  "sentiment_ja": "強気/弱気/中立",
  "summary": "統計とデータに基づいた冷静な市場見解（100字以内）",
  "key_concerns": ["統計的リスク1", "バイアス・落とし穴2"],
  "opportunities": ["インデックス投資の観点での機会"],
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
                "アクティブ運用のコスト（信託報酬・取引コスト）",
                "個別銘柄集中によるリスク増大",
                "感情的投資判断による損失",
            ],
            "opportunities": [
                "低コストインデックスETFへの定期積立",
                "リバランスによるリスク調整",
            ],
            "confidence": 0.95,
        }

    def propose_trades(self, opportunities: List[Dict]) -> List[Dict]:
        """フラット流の取引提案 - 常にインデックス推し"""
        if self._has_api_key() and opportunities:
            prompt = f"""以下の投資機会から、インデックス投資家・効率的市場仮説の観点でトレード提案を行ってください。
なお、個別株よりインデックスETFを推奨する立場です。

投資機会:
{opportunities}

JSON配列で回答（日本語）:
{{
  "ticker": "銘柄コード（できればETFを推奨）",
  "action": "buy/sell/hold",
  "reason": "統計・データ観点での理由（50字以内）",
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
                "ticker": "SPY",
                "action": "buy",
                "reason": "S&P500インデックス。低コスト・高分散。個別銘柄選択は不要。",
                "confidence": 0.99,
                "urgency": "low",
            },
            {
                "ticker": "QQQ",
                "action": "hold",
                "reason": "NASDAQ100インデックス。テック偏重だが分散は十分。",
                "confidence": 0.95,
                "urgency": "low",
            },
            {
                "ticker": "VTI",
                "action": "buy",
                "reason": "全米株式インデックス。究極の分散。コスト最低。",
                "confidence": 0.99,
                "urgency": "low",
            },
        ]

    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        """他のエージェントへの反応 - データと統計で一刀両断"""
        if self._has_api_key():
            prompt = f"""{peer_name}が以下の意見を述べました：
「{peer_opinion}」

これに対してフラットAIとして批判・反論してください。
効率的市場仮説、統計データを根拠に、150字以内の日本語で冷静に否定してください。"""
            response = self._call_claude(self.get_system_prompt(), prompt)
            if response:
                return response.strip()

        # フォールバック
        peer_lower = peer_name.lower()
        if "buffett" in peer_lower or "バフェット" in peer_lower:
            return random.choice(self._REBUTTAL_TO_BUFFETT)
        elif "soros" in peer_lower or "ソロス" in peer_lower:
            return random.choice(self._REBUTTAL_TO_SOROS)
        elif "lynch" in peer_lower or "リンチ" in peer_lower:
            return random.choice(self._REBUTTAL_TO_LYNCH)
        else:
            return f"データを見てください。{self.catchphrase}。これは感情論ではなく統計的事実です。"
