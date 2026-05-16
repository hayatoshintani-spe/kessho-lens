"""
IntelCard 生成器
ニュースインプット → 円谷向けインテリジェンスカードへ変換
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .categories import CATEGORY_META
from .experts import EXPERT_META, IMPORTANCE_LABELS


def make_card_id(date: str, title: str) -> str:
    """日付+タイトルから安定IDを生成"""
    h = hashlib.sha1(f"{date}|{title}".encode("utf-8")).hexdigest()[:10]
    return f"intel_{date}_{h}"


def _has_api_key() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def _build_card_prompt(news: Dict) -> str:
    """Claude API用のプロンプトを構築"""
    title = news.get("title", "")
    url = news.get("url", "")
    summary = news.get("summary", "")
    access = news.get("access_status", "full")
    user_note = news.get("user_note", "")

    category_list = "\n".join(
        f"- {cid}: {meta['label']}" for cid, meta in CATEGORY_META.items()
    )

    importance_list = "\n".join(
        f"- {k}: {v['label']} — {v['description']}"
        for k, v in IMPORTANCE_LABELS.items()
    )

    return f"""あなたは円谷プロダクションのインテリジェンスブリーフ主任アナリストです。
以下のニュースを円谷の事業機会・リスク・経営論点に翻訳してください。

【ニュース】
タイトル: {title}
URL: {url}
要約: {summary or "(本文なし)"}
アクセス状況: {access}
ユーザーメモ: {user_note or "(なし)"}

【ルール】
- 事実・解釈・提案を明確に分ける
- 推測は推測と明記する（speculation_notes フィールド使用）
- 出典が不明な事実を断定しない
- access_status が full でない場合、「タイトル/ユーザー提供情報からの推定である」と明記
- 円谷の事業（ウルトラマンIP、海外展開、MD、ライセンス、ファンコミュニティ）に翻訳する
- 「誰が動くべきか」「次に何を確認すべきか」まで落とし込む

【カテゴリ選択肢】
{category_list}

【重要度選択肢】
{importance_list}

以下のJSONで返してください（説明文なし、JSONのみ）:
{{
  "title": "日本語タイトル（45字以内）",
  "one_liner": "30字以内の超要約",
  "category": "<カテゴリID>",
  "importance": "<A|B|C|D>",
  "fact": "出典に基づく事実（簡潔に）",
  "interpretation": "編集長としての解釈（推測は明記）",
  "insight": {{
    "what_it_means": "円谷にとって何を意味するのか（2-3文）",
    "business_opportunity": ["機会1", "機会2"],
    "risk": ["リスク1", "リスク2"]
  }},
  "actions": [
    {{
      "who": "動くべき部署または会議体",
      "what": "具体的アクション",
      "priority": "urgent|this_week|this_month|watch"
    }}
  ],
  "tags": ["タグ1", "タグ2", "タグ3"],
  "confidence": "high|medium|low",
  "speculation_notes": "推測の根拠と限界（必要なら）",
  "related_agents": ["関連エキスパートIDの配列"]
}}

エキスパートIDの選択肢: ip_strategist, global_expansion, md_licensing, ai_trend, cfo, risk_manager
"""


def generate_card_with_ai(news: Dict) -> Optional[Dict]:
    """Claude APIを使ってIntelCardを生成"""
    if not _has_api_key():
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": _build_card_prompt(news)}],
        )
        text = message.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        print(f"[intel] AIカード生成エラー: {e}")
        return None


def _fallback_card(news: Dict) -> Dict:
    """AIが使えない時のルールベースフォールバック"""
    title = news.get("title", "(無題)")
    summary = news.get("summary", "")
    user_note = news.get("user_note", "")
    category = news.get("category", "ip_content")
    importance = news.get("importance", "C")
    access = news.get("access_status", "title_only")

    cat_meta = CATEGORY_META.get(category, CATEGORY_META["ip_content"])
    related_agents = cat_meta.get("responsible_experts", ["ip_strategist"])[:3]

    spec_note = None
    confidence = "medium"
    if access != "full":
        spec_note = (
            "本記事は本文を確認できていないため、"
            "タイトルおよびユーザー提供情報からの推定である。"
        )
        confidence = "low"

    return {
        "title": title[:45],
        "one_liner": (summary or title)[:30],
        "category": category,
        "importance": importance,
        "fact": summary or f"記事タイトル: {title}",
        "interpretation": (
            f"{cat_meta['label']}カテゴリの動きとして注視。"
            f"{user_note or '詳細は要確認。'}"
        ),
        "insight": {
            "what_it_means": (
                f"円谷の{cat_meta['label_short']}領域に関連する変化の兆し。"
                "本格判断のためには続報と一次情報の確認が必要。"
            ),
            "business_opportunity": [
                f"{cat_meta['label_short']}領域での仮説検証機会"
            ],
            "risk": ["情報不足のまま判断するリスク"],
        },
        "actions": [
            {
                "who": "経営企画 + 関連事業部",
                "what": "本記事の一次情報を取得し、続報をウォッチ",
                "priority": "this_week",
            }
        ],
        "tags": cat_meta.get("targets", [])[:3],
        "confidence": confidence,
        "speculation_notes": spec_note,
        "related_agents": related_agents,
    }


def build_intel_card(news: Dict, date: Optional[str] = None) -> Dict:
    """
    ニュース入力からIntelCardを構築する

    news スキーマ:
        {
            "title": str (必須),
            "url": str,
            "publisher": str,
            "summary": str,
            "user_note": str,  # ユーザーが追加した文脈
            "access_status": "full|title_only|paywalled|estimated",
            "category": str,  # 明示指定（任意）
            "importance": str,  # 明示指定（任意）
        }
    """
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = news.get("title", "(無題)")
    card_id = make_card_id(date, title)

    ai_result = generate_card_with_ai(news)
    body = ai_result if ai_result else _fallback_card(news)

    sources = [{
        "title": news.get("title", ""),
        "url": news.get("url"),
        "publisher": news.get("publisher"),
        "published_at": news.get("published_at"),
        "access_status": news.get("access_status", "full"),
    }]

    return {
        "id": card_id,
        "date": date,
        "title": body.get("title", title),
        "one_liner": body.get("one_liner", title[:30]),
        "category": body.get("category", "ip_content"),
        "importance": body.get("importance", "C"),
        "fact": body.get("fact", ""),
        "interpretation": body.get("interpretation", ""),
        "insight": body.get("insight", {
            "what_it_means": "",
            "business_opportunity": [],
            "risk": [],
        }),
        "actions": body.get("actions", []),
        "tags": body.get("tags", []),
        "sources": sources,
        "confidence": body.get("confidence", "medium"),
        "speculation_notes": body.get("speculation_notes"),
        "related_card_ids": [],
        "related_agents": body.get("related_agents", []),
    }
