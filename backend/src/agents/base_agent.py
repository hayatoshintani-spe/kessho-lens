"""
エージェント基底クラス
全AIエージェントが継承する抽象基底クラス
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class BaseAgent(ABC):
    """
    AIインベストメントエージェントの抽象基底クラス
    各エージェントはこのクラスを継承して個性を実装する
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        display_name: str,
        personality_description: str,
        style: str,
        favorite_sectors: List[str],
        catchphrase: str,
    ):
        self.agent_id = agent_id
        self.name = name
        self.display_name = display_name
        self.personality_description = personality_description
        self.style = style
        self.favorite_sectors = favorite_sectors
        self.catchphrase = catchphrase
        self._anthropic_client = None

    def _get_anthropic_client(self):
        """Anthropicクライアントを取得（遅延初期化）"""
        if self._anthropic_client is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    import anthropic
                    self._anthropic_client = anthropic.Anthropic(api_key=api_key)
                except ImportError:
                    pass
        return self._anthropic_client

    def _has_api_key(self) -> bool:
        """APIキーが設定されているか確認"""
        return bool(os.getenv("ANTHROPIC_API_KEY"))

    def _call_claude(self, system_prompt: str, user_message: str) -> Optional[str]:
        """
        Claude APIを呼び出す
        失敗した場合はNoneを返す
        """
        client = self._get_anthropic_client()
        if not client:
            return None

        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except Exception as e:
            print(f"Claude API呼び出しエラー ({self.agent_id}): {e}")
            return None

    def get_system_prompt(self) -> str:
        """
        エージェント固有のシステムプロンプトを生成
        サブクラスでオーバーライド可能
        """
        return f"""あなたは{self.display_name}というAI投資家です。

性格: {self.personality_description}
投資スタイル: {self.style}
得意セクター: {', '.join(self.favorite_sectors)}
口癖: 「{self.catchphrase}」

あなたは常に日本語で回答してください。
自分の投資哲学に基づいた意見を、強い個性を持って表現してください。
他のAI投資家（バフェットAI、ソロスAI、リンチAI、フラットAI）との議論では、
自分の哲学を曲げずに主張してください。
回答は200字以内で、簡潔かつ印象的にしてください。"""

    @abstractmethod
    def analyze_market(self, market_data: Dict) -> Dict:
        """
        市場データを分析してオピニオンを返す

        Args:
            market_data: 市場データ辞書

        Returns:
            {
                "agent_id": str,
                "sentiment": "bullish" | "bearish" | "neutral",
                "sentiment_ja": "強気" | "弱気" | "中立",
                "summary": str (Japanese),
                "key_concerns": List[str] (Japanese),
                "opportunities": List[str] (Japanese),
                "confidence": float (0-1),
            }
        """
        pass

    @abstractmethod
    def propose_trades(self, opportunities: List[Dict]) -> List[Dict]:
        """
        投資機会から取引提案を生成する

        Args:
            opportunities: 投資機会のリスト

        Returns:
            [
                {
                    "ticker": str,
                    "action": "buy" | "sell" | "hold",
                    "reason": str (Japanese),
                    "confidence": float,
                    "urgency": "high" | "medium" | "low",
                }
            ]
        """
        pass

    @abstractmethod
    def respond_to_peer(self, peer_name: str, peer_opinion: str, context: str = "") -> str:
        """
        他のエージェントの意見に対して反応する

        Args:
            peer_name: 相手エージェントの名前
            peer_opinion: 相手の意見（日本語）
            context: 追加コンテキスト

        Returns:
            str: 反応メッセージ（日本語）
        """
        pass

    def get_summary(self) -> Dict:
        """エージェントの概要情報を返す"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "display_name": self.display_name,
            "personality": self.personality_description,
            "style": self.style,
            "favorite_sectors": self.favorite_sectors,
            "catchphrase": self.catchphrase,
        }

    def _fallback_market_sentiment(self, market_data: Dict) -> str:
        """市場データからデフォルトのセンチメントを推定"""
        change = market_data.get("sp500_change_pct", 0)
        if change > 0.5:
            return "bullish"
        elif change < -0.5:
            return "bearish"
        return "neutral"
