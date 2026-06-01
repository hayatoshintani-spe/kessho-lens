"""
AIエージェント会議生成器（プロジェクト指示§9）
重要テーマに対し、6人のエキスパートが議論し、編集長が結論をまとめる
"""

import os
import json
import hashlib
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .experts import EXPERT_META, EXPERTS


def make_council_id(date: str, topic: str) -> str:
    h = hashlib.sha1(f"council|{date}|{topic}".encode("utf-8")).hexdigest()[:8]
    return f"council_{date}_{h}"


def _has_api_key() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def _build_council_prompt(topic: str, context_cards: List[Dict]) -> str:
    card_brief = "\n".join(
        f"- [{c.get('importance')}] {c.get('title')}: {c.get('one_liner', '')}"
        for c in context_cards[:6]
    )
    experts_list = "\n".join(
        f"- {meta['name']} ({meta['id']}): {meta['focus']}"
        for meta in EXPERT_META.values()
    )

    return f"""円谷プロダクション社内のインテリジェンスブリーフ会議を生成してください。

【議題】
{topic}

【参照カード】
{card_brief}

【参加エキスパート】
{experts_list}

【ルール】
- 各エキスパートは自分の役割視点でのみ発言
- お互い意見が衝突する場面を入れる（特にCFO vs IP戦略家、リスク管理 vs AI技術トレンド）
- 発言は1人150字以内
- 全体で12-16発言
- 最後に「編集長としての結論」を入れる：採用すべき論点 / 保留すべき論点 / 追加調査

以下のJSONで返してください（説明文なし、JSONのみ）:
{{
  "summary": "会議の要約（100字以内）",
  "messages": [
    {{
      "expert_id": "ip_strategist",
      "time": "09:00",
      "content": "発言内容",
      "stance": "support|challenge|neutral|concern|proposal"
    }}
  ],
  "editor_conclusion": {{
    "adopt": ["採用すべき論点1", "論点2"],
    "hold": ["保留すべき論点1"],
    "research": ["追加調査が必要な点1", "点2"]
  }}
}}
"""


def _generate_council_with_ai(topic: str, context_cards: List[Dict]) -> Optional[Dict]:
    if not _has_api_key():
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            messages=[{"role": "user", "content": _build_council_prompt(topic, context_cards)}],
        )
        text = message.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        print(f"[intel] AI council 生成エラー: {e}")
        return None


def _fallback_council(topic: str, context_cards: List[Dict]) -> Dict:
    """ルールベースの会議フォールバック"""
    messages = []
    time_min = 0

    def t():
        nonlocal time_min
        hour = 9 + time_min // 60
        minute = time_min % 60
        time_min += random.randint(2, 4)
        return f"{hour:02d}:{minute:02d}"

    primary_card = context_cards[0] if context_cards else {"title": topic, "one_liner": ""}
    card_title = primary_card.get("title", topic)

    # オープニング: IP戦略家
    messages.append({
        "expert_id": "ip_strategist",
        "time": t(),
        "content": (
            f"本日の議題は『{topic}』。{card_title}を起点に、"
            f"ウルトラマンIPの長期価値拡張の観点で論点を整理したい。"
            f"短期収益より、ファン世代の広がりとブランド資産を最優先で見るべき。"
        ),
        "stance": "proposal",
    })

    # CFOの冷徹な問い
    messages.append({
        "expert_id": "cfo",
        "time": t(),
        "content": (
            "気持ちは分かるが、まず投資額・回収期間・限界利益を出してほしい。"
            "『IPの広がり』だけでは予算は付かない。3年で黒字化、5年でROI 20%が最低ライン。"
        ),
        "stance": "challenge",
    })

    # グローバル展開担当
    messages.append({
        "expert_id": "global_expansion",
        "time": t(),
        "content": (
            "地域別の温度差を見るべき。中国・東南アジアは既存ファン基盤が強く、"
            "本件はそこに刺さる可能性が高い。北米はまだファン層が薄いので"
            "投資効率が落ちる。優先順位は明確化したい。"
        ),
        "stance": "support",
    })

    # MD/ライセンス担当
    messages.append({
        "expert_id": "md_licensing",
        "time": t(),
        "content": (
            "MD側からは大人向け・コレクター市場への拡張余地が見える。"
            "Pop Mart型のサプライズ性とコレクター性を組み合わせた限定品は、"
            "単価1万円超でも回転する可能性。ライセンシーと組む形を提案。"
        ),
        "stance": "proposal",
    })

    # AI技術トレンド担当
    messages.append({
        "expert_id": "ai_trend",
        "time": t(),
        "content": (
            "技術面から補強。AI翻訳・吹替・ファンチャットの組み合わせで、"
            "海外展開のローカライズコストを大幅に下げられる。"
            "ただしブランド毀損を防ぐためのガードレール設計が必須。"
        ),
        "stance": "support",
    })

    # リスク管理担当
    messages.append({
        "expert_id": "risk_manager",
        "time": t(),
        "content": (
            "待った。AIキャラクター展開は各国の著作権・パブリシティ権の取り扱いが"
            "まだ流動的。EU・中国・米国で規制スタンスが異なる。"
            "全社展開の前に法務レビューと炎上シミュレーションを必須としたい。"
        ),
        "stance": "concern",
    })

    # CFO再質問
    messages.append({
        "expert_id": "cfo",
        "time": t(),
        "content": (
            "リスク管理の指摘は正論。法務コストとブランド毀損リスクを織り込むと、"
            "ROIは下振れする。まずは限定地域・限定IP範囲でのPoCに投資を絞るべき。"
        ),
        "stance": "challenge",
    })

    # IP戦略家まとめ
    messages.append({
        "expert_id": "ip_strategist",
        "time": t(),
        "content": (
            "全員の論点を取り込むと、(1) 中国・東南アジア優先、(2) MD/ライセンス先行、"
            "(3) AI活用は限定PoC、(4) 法務レビューを並行、という構図。"
            "ブランド整合性を最優先しつつ、段階的に検証していくべき。"
        ),
        "stance": "proposal",
    })

    # グローバル展開で締める提案
    messages.append({
        "expert_id": "global_expansion",
        "time": t(),
        "content": (
            "賛成。具体的には中国・タイ・インドネシアでのMD展開を6ヶ月で検証、"
            "並行して現地パートナー候補をリスト化したい。経営会議への上申準備に入る。"
        ),
        "stance": "support",
    })

    return {
        "summary": f"『{topic}』を巡る議論。中国・東南アジア優先のMD/ライセンス展開を起点に、AI活用は限定PoC、法務レビュー並行という方向性で収束。",
        "messages": messages,
        "editor_conclusion": {
            "adopt": [
                "中国・東南アジア優先のMD/ライセンス展開を段階検証",
                "Pop Mart型のコレクター向け限定MDを試作",
            ],
            "hold": [
                "全社規模でのAIキャラクター展開（法務リスク確定まで）",
                "北米市場への大規模投資（ファン基盤が薄いため）",
            ],
            "research": [
                "EU・中国・米国のAIパブリシティ権規制の最新動向",
                "Pop Mart・Funko の利益構造とコレクター市場の伸びシロ",
                "現地パートナー候補のリストアップ（東南アジア3カ国）",
            ],
        },
    }


def generate_council_session(
    topic: str,
    context_cards: List[Dict],
    date: Optional[str] = None,
) -> Dict:
    """AIエージェント会議を生成"""
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sid = make_council_id(date, topic)

    ai_result = _generate_council_with_ai(topic, context_cards)
    body = ai_result if ai_result else _fallback_council(topic, context_cards)

    # メッセージにエキスパート名を補完
    messages = []
    for m in body.get("messages", []):
        eid = m.get("expert_id", "ip_strategist")
        meta = EXPERT_META.get(eid, EXPERT_META["ip_strategist"])
        messages.append({
            "expert_id": eid,
            "expert_name": meta["name"],
            "time": m.get("time", "09:00"),
            "content": m.get("content", ""),
            "stance": m.get("stance", "neutral"),
        })

    return {
        "id": sid,
        "date": date,
        "topic": topic,
        "trigger_card_ids": [c.get("id") for c in context_cards if c.get("id")],
        "summary": body.get("summary", f"『{topic}』に関するエキスパート会議"),
        "messages": messages,
        "editor_conclusion": body.get("editor_conclusion", {
            "adopt": [], "hold": [], "research": [],
        }),
    }
