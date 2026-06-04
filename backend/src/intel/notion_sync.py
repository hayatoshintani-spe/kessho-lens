"""
Notion 連携モジュール
IntelCard を Notion DB に同期する（idempotent upsert）

設計:
- NOTION_API_KEY と NOTION_CARDS_DB_ID 環境変数で動作
- card.id を Notion ページの "Card ID" プロパティに保存し、再同期時は upsert
- カードの完全な JSON は "Card JSON" プロパティに格納（round-trip 用）。
  これにより Notion から元のカード構造を完全復元できる（fetch_all_cards）。
- カードのメタはプロパティ、本文はページ children として書き込む（人間可読用）
- 未設定時は is_enabled() が False を返し、API 呼び出し側で安全にスキップ
"""

import os
import json
from typing import Dict, List, Optional, Tuple

import httpx

from .categories import CATEGORY_META
from .experts import IMPORTANCE_LABELS, EXPERT_META

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Notion rich_text の1要素あたり最大2000文字。複数要素配列にすれば総計は数万文字まで可。
_CARD_JSON_CHUNK = 1900


def is_enabled() -> bool:
    return bool(os.getenv("NOTION_API_KEY") and os.getenv("NOTION_CARDS_DB_ID"))


def is_briefs_enabled() -> bool:
    """Brief 永続化用 DB が設定されていれば True"""
    return bool(os.getenv("NOTION_API_KEY") and os.getenv("NOTION_BRIEFS_DB_ID"))


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _truncate(s: str, max_chars: int = 1900) -> str:
    """Notion rich_text は1セクション2000文字制限。余裕を持って1900で切る"""
    if not s:
        return ""
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def _rich_text(text: str, max_chars: int = 1900) -> List[Dict]:
    """Notion rich_text 配列を作る"""
    t = _truncate(text or "", max_chars)
    if not t:
        return []
    return [{"type": "text", "text": {"content": t}}]


def _paragraph(text: str) -> Dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": _rich_text(text)},
    }


def _heading(text: str, level: int = 2) -> Dict:
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": _rich_text(text)},
    }


def _bullet(text: str) -> Dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": _rich_text(text)},
    }


def _divider() -> Dict:
    return {"object": "block", "type": "divider", "divider": {}}


# ─── Card → Notion 変換 ────────────────────────────────────────────────


def _card_to_json_rich_text(card: Dict) -> List[Dict]:
    """カード全体を JSON 化し、Notion rich_text のチャンク配列に分割する。
    各 text item は 2000 文字制限のため _CARD_JSON_CHUNK=1900 で安全に分割。
    """
    blob = json.dumps(card, ensure_ascii=False, separators=(",", ":"))
    chunks: List[Dict] = []
    for i in range(0, len(blob), _CARD_JSON_CHUNK):
        part = blob[i : i + _CARD_JSON_CHUNK]
        chunks.append({"type": "text", "text": {"content": part}})
    return chunks


def _read_card_json_property(page: Dict) -> Optional[Dict]:
    """Notion ページの Card JSON プロパティを連結してカード dict にデコードする"""
    props = page.get("properties", {})
    field = props.get("Card JSON") or {}
    items = field.get("rich_text") or []
    if not items:
        return None
    blob = "".join((it.get("plain_text") or it.get("text", {}).get("content", "")) for it in items)
    if not blob:
        return None
    try:
        return json.loads(blob)
    except (ValueError, TypeError):
        return None


def _card_to_properties(card: Dict) -> Dict:
    """IntelCard を Notion DB プロパティへ変換"""
    cat_meta = CATEGORY_META.get(card.get("category"), {})
    imp_meta = IMPORTANCE_LABELS.get(card.get("importance"), {})

    sources_text = " / ".join(
        f"{s.get('publisher') or s.get('title')}({s.get('access_status', '?')})"
        for s in card.get("sources", [])[:3]
    )
    first_url = next(
        (s.get("url") for s in card.get("sources", []) if s.get("url")),
        None,
    )

    props: Dict = {
        "Title": {"title": _rich_text(card.get("title", "(無題)"))},
        "Card ID": {"rich_text": _rich_text(card.get("id", ""))},
        "Card JSON": {"rich_text": _card_to_json_rich_text(card)},
        "Date": {"date": {"start": card.get("date")}} if card.get("date") else {"date": None},
        "Importance": {
            "select": {"name": f"{card.get('importance', 'D')} - {imp_meta.get('label', '')}"}
            if card.get("importance") else None
        },
        "Category": {
            "select": {"name": cat_meta.get("label", card.get("category", "未分類"))}
            if card.get("category") else None
        },
        "Confidence": {
            "select": {"name": card.get("confidence", "medium")}
        },
        "One Liner": {"rich_text": _rich_text(card.get("one_liner", ""))},
        "What it means": {
            "rich_text": _rich_text(card.get("insight", {}).get("what_it_means", ""))
        },
        "Tags": {
            "multi_select": [{"name": _truncate(t, 100)} for t in card.get("tags", [])[:10]]
        },
        "Related Experts": {
            "multi_select": [
                {"name": EXPERT_META.get(e, {}).get("name", e)}
                for e in card.get("related_agents", [])
            ]
        },
        "Sources": {"rich_text": _rich_text(sources_text)},
        "Source URL": {"url": first_url} if first_url else {"url": None},
        "Status": {"select": {"name": "新規"}},  # 初回作成時のみ。更新時は touch しない
    }
    return props


def _card_to_blocks(card: Dict) -> List[Dict]:
    """IntelCard をページ本文ブロックへ変換"""
    blocks: List[Dict] = []

    one_liner = card.get("one_liner", "")
    if one_liner:
        blocks.append(_paragraph(f"💡 {one_liner}"))
        blocks.append(_divider())

    fact = card.get("fact", "")
    if fact:
        blocks.append(_heading("📋 事実"))
        blocks.append(_paragraph(fact))

    interpretation = card.get("interpretation", "")
    if interpretation:
        blocks.append(_heading("🔍 解釈"))
        blocks.append(_paragraph(interpretation))

    insight = card.get("insight", {})
    wim = insight.get("what_it_means", "")
    if wim:
        blocks.append(_heading("💼 円谷への示唆"))
        blocks.append(_paragraph(wim))

    opps = insight.get("business_opportunity", [])
    if opps:
        blocks.append(_heading("🌱 事業機会", level=3))
        for o in opps:
            blocks.append(_bullet(o))

    risks = insight.get("risk", [])
    if risks:
        blocks.append(_heading("⚠️ リスク", level=3))
        for r in risks:
            blocks.append(_bullet(r))

    actions = card.get("actions", [])
    if actions:
        blocks.append(_heading("✅ 次アクション"))
        pri_label = {
            "urgent": "🔴 緊急",
            "this_week": "🟡 今週",
            "this_month": "🟢 今月",
            "watch": "⚪ 継続監視",
        }
        for a in actions:
            line = f"{pri_label.get(a.get('priority'), '')} | {a.get('who', '')}: {a.get('what', '')}"
            blocks.append(_bullet(line))

    spec = card.get("speculation_notes")
    if spec:
        blocks.append(_divider())
        blocks.append(_heading("📝 推測の注記", level=3))
        blocks.append(_paragraph(spec))

    sources = card.get("sources", [])
    if sources:
        blocks.append(_divider())
        blocks.append(_heading("📰 出典", level=3))
        for s in sources:
            parts = [s.get("title", ""), s.get("publisher", ""), s.get("published_at", "")]
            line = " — ".join([p for p in parts if p])
            if s.get("url"):
                line = f"{line} ({s['url']})"
            line = f"[{s.get('access_status', 'full')}] {line}"
            blocks.append(_bullet(line))

    return blocks


# ─── Notion API 呼び出し ────────────────────────────────────────────────


def _find_existing_page(client: httpx.Client, db_id: str, card_id: str) -> Optional[str]:
    """Card ID プロパティで既存ページを検索。あれば page_id を返す"""
    resp = client.post(
        f"{NOTION_API_BASE}/databases/{db_id}/query",
        json={
            "filter": {
                "property": "Card ID",
                "rich_text": {"equals": card_id},
            },
            "page_size": 1,
        },
    )
    if resp.status_code != 200:
        return None
    results = resp.json().get("results", [])
    return results[0]["id"] if results else None


def _replace_page_children(client: httpx.Client, page_id: str, blocks: List[Dict]) -> None:
    """ページの既存 children を全削除してから新規追加"""
    # 既存ブロック取得 → 削除
    list_resp = client.get(
        f"{NOTION_API_BASE}/blocks/{page_id}/children",
        params={"page_size": 100},
    )
    if list_resp.status_code == 200:
        for child in list_resp.json().get("results", []):
            try:
                client.delete(f"{NOTION_API_BASE}/blocks/{child['id']}")
            except Exception:
                pass
    # 新規追加（100ブロックずつ）
    for i in range(0, len(blocks), 100):
        client.patch(
            f"{NOTION_API_BASE}/blocks/{page_id}/children",
            json={"children": blocks[i : i + 100]},
        )


def sync_card(card: Dict, db_id: Optional[str] = None) -> Dict:
    """
    カードをNotionにupsertする

    Returns:
        {"action": "created"|"updated"|"skipped"|"error",
         "page_id": str|None,
         "url": str|None,
         "error": str|None}
    """
    if not is_enabled():
        return {"action": "skipped", "page_id": None, "url": None, "error": "notion_not_configured"}

    db_id = db_id or os.getenv("NOTION_CARDS_DB_ID")
    card_id = card.get("id")
    if not card_id or not db_id:
        return {"action": "error", "page_id": None, "url": None, "error": "missing_card_id_or_db_id"}

    properties = _card_to_properties(card)
    blocks = _card_to_blocks(card)

    try:
        with httpx.Client(headers=_headers(), timeout=30.0) as client:
            existing_page_id = _find_existing_page(client, db_id, card_id)

            if existing_page_id:
                # Status は手動更新を尊重するため、更新時は touch しない
                update_props = {k: v for k, v in properties.items() if k != "Status"}
                resp = client.patch(
                    f"{NOTION_API_BASE}/pages/{existing_page_id}",
                    json={"properties": update_props},
                )
                if resp.status_code != 200:
                    return {
                        "action": "error",
                        "page_id": existing_page_id,
                        "url": None,
                        "error": f"page_update_failed: {resp.status_code} {resp.text[:200]}",
                    }
                _replace_page_children(client, existing_page_id, blocks)
                page = resp.json()
                return {
                    "action": "updated",
                    "page_id": existing_page_id,
                    "url": page.get("url"),
                    "error": None,
                }
            else:
                resp = client.post(
                    f"{NOTION_API_BASE}/pages",
                    json={
                        "parent": {"database_id": db_id},
                        "properties": properties,
                        "children": blocks[:100],  # 初回は100まで
                    },
                )
                if resp.status_code != 200:
                    return {
                        "action": "error",
                        "page_id": None,
                        "url": None,
                        "error": f"page_create_failed: {resp.status_code} {resp.text[:200]}",
                    }
                page = resp.json()
                page_id = page.get("id")
                # 残りブロックを追加
                if len(blocks) > 100 and page_id:
                    for i in range(100, len(blocks), 100):
                        client.patch(
                            f"{NOTION_API_BASE}/blocks/{page_id}/children",
                            json={"children": blocks[i : i + 100]},
                        )
                return {
                    "action": "created",
                    "page_id": page_id,
                    "url": page.get("url"),
                    "error": None,
                }
    except httpx.HTTPError as e:
        return {"action": "error", "page_id": None, "url": None, "error": str(e)}


def sync_all_cards(cards: List[Dict]) -> Dict:
    """全カードをまとめて同期する"""
    result = {"created": 0, "updated": 0, "skipped": 0, "errors": []}
    if not is_enabled():
        return {**result, "skipped": len(cards), "errors": ["notion_not_configured"]}
    for card in cards:
        r = sync_card(card)
        action = r.get("action")
        if action == "created":
            result["created"] += 1
        elif action == "updated":
            result["updated"] += 1
        elif action == "skipped":
            result["skipped"] += 1
        else:
            result["errors"].append({"card_id": card.get("id"), "error": r.get("error")})
    return result


# ─── Setup: DB 作成ヘルパー ────────────────────────────────────────────


def create_cards_database(parent_page_id: str) -> Dict:
    """
    親ページに IntelCards 用のDBを作成する。
    Notion Integration が親ページに招待されている必要がある。
    """
    if not os.getenv("NOTION_API_KEY"):
        return {"error": "NOTION_API_KEY not set"}

    schema = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Tsuburaya Intel Cards"}}],
        "properties": {
            "Title": {"title": {}},
            "Card ID": {"rich_text": {}},
            "Card JSON": {"rich_text": {}},
            "Date": {"date": {}},
            "Importance": {
                "select": {
                    "options": [
                        {"name": "A - 経営アジェンダ化", "color": "red"},
                        {"name": "B - 事業部で検討", "color": "orange"},
                        {"name": "C - 情報共有", "color": "blue"},
                        {"name": "D - 参考情報", "color": "gray"},
                    ]
                }
            },
            "Category": {
                "select": {
                    "options": [
                        {"name": m["label"], "color": "default"}
                        for m in CATEGORY_META.values()
                    ]
                }
            },
            "Confidence": {
                "select": {
                    "options": [
                        {"name": "high", "color": "green"},
                        {"name": "medium", "color": "yellow"},
                        {"name": "low", "color": "red"},
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "新規", "color": "blue"},
                        {"name": "確認中", "color": "yellow"},
                        {"name": "対応中", "color": "orange"},
                        {"name": "完了", "color": "green"},
                        {"name": "保留", "color": "gray"},
                    ]
                }
            },
            "One Liner": {"rich_text": {}},
            "What it means": {"rich_text": {}},
            "Tags": {"multi_select": {}},
            "Related Experts": {"multi_select": {}},
            "Sources": {"rich_text": {}},
            "Source URL": {"url": {}},
        },
    }

    try:
        with httpx.Client(headers=_headers(), timeout=30.0) as client:
            resp = client.post(f"{NOTION_API_BASE}/databases", json=schema)
            if resp.status_code != 200:
                return {
                    "error": f"create_failed: {resp.status_code} {resp.text[:500]}"
                }
            data = resp.json()
            return {
                "database_id": data.get("id"),
                "url": data.get("url"),
                "message": (
                    f"Database created. Set NOTION_CARDS_DB_ID={data.get('id')} in your env."
                ),
            }
    except httpx.HTTPError as e:
        return {"error": str(e)}


def get_status() -> Dict:
    """接続状況とDB情報を返す"""
    enabled = is_enabled()
    db_id = os.getenv("NOTION_CARDS_DB_ID")
    has_key = bool(os.getenv("NOTION_API_KEY"))

    db_info: Dict = {}
    if enabled:
        try:
            with httpx.Client(headers=_headers(), timeout=15.0) as client:
                resp = client.get(f"{NOTION_API_BASE}/databases/{db_id}")
                if resp.status_code == 200:
                    data = resp.json()
                    title_arr = data.get("title", [])
                    title = title_arr[0]["plain_text"] if title_arr else "(no title)"
                    db_info = {
                        "title": title,
                        "url": data.get("url"),
                        "properties": list(data.get("properties", {}).keys()),
                    }
                else:
                    db_info = {
                        "error": f"{resp.status_code}: {resp.text[:200]}",
                    }
        except httpx.HTTPError as e:
            db_info = {"error": str(e)}

    return {
        "enabled": enabled,
        "has_api_key": has_key,
        "has_db_id": bool(db_id),
        "db_id": db_id,
        "db": db_info,
    }


# ─── Restore: Notion → ローカル ──────────────────────────────────────────


def fetch_all_cards(db_id: Optional[str] = None) -> List[Dict]:
    """Notion DB から全カードを取得して dict のリストとして返す。
    Card JSON プロパティを優先、欠落しているページはスキップする。
    """
    if not is_enabled():
        return []
    db_id = db_id or os.getenv("NOTION_CARDS_DB_ID")
    if not db_id:
        return []

    cards: List[Dict] = []
    next_cursor: Optional[str] = None
    try:
        with httpx.Client(headers=_headers(), timeout=30.0) as client:
            while True:
                payload: Dict = {"page_size": 100}
                if next_cursor:
                    payload["start_cursor"] = next_cursor
                resp = client.post(
                    f"{NOTION_API_BASE}/databases/{db_id}/query",
                    json=payload,
                )
                if resp.status_code != 200:
                    print(
                        f"[notion] fetch_all_cards: query failed "
                        f"{resp.status_code} {resp.text[:200]}"
                    )
                    break
                data = resp.json()
                for page in data.get("results", []):
                    card = _read_card_json_property(page)
                    if card and card.get("id"):
                        cards.append(card)
                if not data.get("has_more"):
                    break
                next_cursor = data.get("next_cursor")
    except httpx.HTTPError as e:
        print(f"[notion] fetch_all_cards error: {e}")
        return cards
    return cards


def restore_local_from_notion() -> Dict:
    """Notion のカードをローカル JSON ストアへ反映する（起動時の復元用）。
    Notion 未設定なら何もしない。Returns: {restored, skipped, error}
    """
    if not is_enabled():
        return {"restored": 0, "skipped": 0, "error": "notion_not_configured"}

    # 循環インポート回避のためここで遅延 import
    from ..data.storage import Storage

    try:
        cards = fetch_all_cards()
    except Exception as e:
        return {"restored": 0, "skipped": 0, "error": f"fetch_failed: {e}"}

    if not cards:
        return {"restored": 0, "skipped": 0, "error": None}

    # Notion を source of truth とし、ローカルを上書き
    Storage.save_intel_cards(cards)
    return {"restored": len(cards), "skipped": 0, "error": None}


# ─── Briefs DB: 永続化 / 復元 ───────────────────────────────────────────


def _brief_to_json_rich_text(brief: Dict) -> List[Dict]:
    """Brief 全体を JSON 化し、2000 文字制限を踏まえてチャンク分割する。"""
    blob = json.dumps(brief, ensure_ascii=False, separators=(",", ":"))
    chunks: List[Dict] = []
    for i in range(0, len(blob), _CARD_JSON_CHUNK):
        part = blob[i : i + _CARD_JSON_CHUNK]
        chunks.append({"type": "text", "text": {"content": part}})
    return chunks


def _read_brief_json_property(page: Dict) -> Optional[Dict]:
    """Notion ページの Brief JSON プロパティを連結して dict にデコード"""
    props = page.get("properties", {})
    field = props.get("Brief JSON") or {}
    items = field.get("rich_text") or []
    if not items:
        return None
    blob = "".join(
        (it.get("plain_text") or it.get("text", {}).get("content", ""))
        for it in items
    )
    if not blob:
        return None
    try:
        return json.loads(blob)
    except (ValueError, TypeError):
        return None


def _brief_to_properties(brief: Dict) -> Dict:
    date = brief.get("date") or ""
    btype = brief.get("brief_type", "daily")
    key = f"{date}__{btype}"
    return {
        "Title": {"title": _rich_text(brief.get("title") or f"{date} {btype} brief")},
        "Brief Key": {"rich_text": _rich_text(key)},
        "Brief JSON": {"rich_text": _brief_to_json_rich_text(brief)},
        "Date": {"date": {"start": date}} if date else {"date": None},
        "Brief Type": {"select": {"name": btype}} if btype else None,
        "Executive Summary": {
            "rich_text": _rich_text(brief.get("executive_summary", ""))
        },
        "Card Count": {"number": len(brief.get("top_topics", []))},
    }


def _brief_to_blocks(brief: Dict) -> List[Dict]:
    """Brief を人間可読なページ本文へ"""
    blocks: List[Dict] = []
    summary = brief.get("executive_summary", "")
    if summary:
        blocks.append(_heading("📋 エグゼクティブサマリ"))
        blocks.append(_paragraph(summary))
        blocks.append(_divider())

    for section in brief.get("sections", []):
        blocks.append(_heading(section.get("heading", "(無題)")))
        body = section.get("body", "")
        # 2000 文字制限のため段落単位で分割
        for chunk_start in range(0, len(body), 1800):
            blocks.append(_paragraph(body[chunk_start : chunk_start + 1800]))

    actions = brief.get("next_actions", [])
    if actions:
        blocks.append(_divider())
        blocks.append(_heading("✅ 次アクション"))
        for a in actions:
            line = f"[{a.get('priority', '')}] {a.get('who', '')}: {a.get('what', '')}"
            blocks.append(_bullet(line))
    return blocks


def _find_existing_brief_page(
    client: httpx.Client, db_id: str, brief_key: str,
) -> Optional[str]:
    resp = client.post(
        f"{NOTION_API_BASE}/databases/{db_id}/query",
        json={
            "filter": {
                "property": "Brief Key",
                "rich_text": {"equals": brief_key},
            },
            "page_size": 1,
        },
    )
    if resp.status_code != 200:
        return None
    results = resp.json().get("results", [])
    return results[0]["id"] if results else None


def sync_brief(brief: Dict, db_id: Optional[str] = None) -> Dict:
    """Brief を Briefs DB に upsert"""
    if not is_briefs_enabled():
        return {"action": "skipped", "page_id": None, "url": None,
                "error": "notion_briefs_not_configured"}
    db_id = db_id or os.getenv("NOTION_BRIEFS_DB_ID")
    date = brief.get("date")
    btype = brief.get("brief_type", "daily")
    if not date or not db_id:
        return {"action": "error", "page_id": None, "url": None,
                "error": "missing_date_or_db_id"}
    key = f"{date}__{btype}"
    props = {k: v for k, v in _brief_to_properties(brief).items() if v is not None}
    blocks = _brief_to_blocks(brief)
    try:
        with httpx.Client(headers=_headers(), timeout=30.0) as client:
            existing_id = _find_existing_brief_page(client, db_id, key)
            if existing_id:
                resp = client.patch(
                    f"{NOTION_API_BASE}/pages/{existing_id}",
                    json={"properties": props},
                )
                if resp.status_code != 200:
                    return {"action": "error", "page_id": existing_id, "url": None,
                            "error": f"page_update_failed: {resp.status_code} {resp.text[:200]}"}
                _replace_page_children(client, existing_id, blocks)
                return {"action": "updated", "page_id": existing_id,
                        "url": resp.json().get("url"), "error": None}
            resp = client.post(
                f"{NOTION_API_BASE}/pages",
                json={
                    "parent": {"database_id": db_id},
                    "properties": props,
                    "children": blocks[:100],
                },
            )
            if resp.status_code != 200:
                return {"action": "error", "page_id": None, "url": None,
                        "error": f"page_create_failed: {resp.status_code} {resp.text[:200]}"}
            page = resp.json()
            page_id = page.get("id")
            if len(blocks) > 100 and page_id:
                for i in range(100, len(blocks), 100):
                    client.patch(
                        f"{NOTION_API_BASE}/blocks/{page_id}/children",
                        json={"children": blocks[i : i + 100]},
                    )
            return {"action": "created", "page_id": page_id,
                    "url": page.get("url"), "error": None}
    except httpx.HTTPError as e:
        return {"action": "error", "page_id": None, "url": None, "error": str(e)}


def fetch_all_briefs(db_id: Optional[str] = None) -> List[Dict]:
    """Briefs DB から全 Brief を取得して dict のリストとして返す"""
    if not is_briefs_enabled():
        return []
    db_id = db_id or os.getenv("NOTION_BRIEFS_DB_ID")
    if not db_id:
        return []
    briefs: List[Dict] = []
    next_cursor: Optional[str] = None
    try:
        with httpx.Client(headers=_headers(), timeout=30.0) as client:
            while True:
                payload: Dict = {"page_size": 100}
                if next_cursor:
                    payload["start_cursor"] = next_cursor
                resp = client.post(
                    f"{NOTION_API_BASE}/databases/{db_id}/query",
                    json=payload,
                )
                if resp.status_code != 200:
                    print(
                        f"[notion] fetch_all_briefs: query failed "
                        f"{resp.status_code} {resp.text[:200]}"
                    )
                    break
                data = resp.json()
                for page in data.get("results", []):
                    brief = _read_brief_json_property(page)
                    if brief and brief.get("date"):
                        briefs.append(brief)
                if not data.get("has_more"):
                    break
                next_cursor = data.get("next_cursor")
    except httpx.HTTPError as e:
        print(f"[notion] fetch_all_briefs error: {e}")
        return briefs
    return briefs


def restore_local_briefs_from_notion() -> Dict:
    """Notion の Brief をローカル JSON ストアへ反映する（起動時の復元用）"""
    if not is_briefs_enabled():
        return {"restored": 0, "skipped": 0, "error": "notion_briefs_not_configured"}
    from ..data.storage import Storage, write_json
    try:
        briefs = fetch_all_briefs()
    except Exception as e:
        return {"restored": 0, "skipped": 0, "error": f"fetch_failed: {e}"}
    if not briefs:
        return {"restored": 0, "skipped": 0, "error": None}
    write_json("intel_briefs.json", briefs)
    return {"restored": len(briefs), "skipped": 0, "error": None}


def create_briefs_database(parent_page_id: str) -> Dict:
    """親ページに Daily/Weekly Brief 永続化用のDBを作成する"""
    if not os.getenv("NOTION_API_KEY"):
        return {"error": "NOTION_API_KEY not set"}
    schema = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Tsuburaya Intel Briefs"}}],
        "properties": {
            "Title": {"title": {}},
            "Brief Key": {"rich_text": {}},
            "Brief JSON": {"rich_text": {}},
            "Date": {"date": {}},
            "Brief Type": {
                "select": {
                    "options": [
                        {"name": "daily", "color": "blue"},
                        {"name": "weekly", "color": "green"},
                        {"name": "monthly", "color": "orange"},
                    ]
                }
            },
            "Executive Summary": {"rich_text": {}},
            "Card Count": {"number": {}},
        },
    }
    try:
        with httpx.Client(headers=_headers(), timeout=30.0) as client:
            resp = client.post(f"{NOTION_API_BASE}/databases", json=schema)
            if resp.status_code != 200:
                return {"error": f"create_failed: {resp.status_code} {resp.text[:500]}"}
            data = resp.json()
            return {
                "database_id": data.get("id"),
                "url": data.get("url"),
                "message": (
                    f"Briefs database created. "
                    f"Set NOTION_BRIEFS_DB_ID={data.get('id')} in your env."
                ),
            }
    except httpx.HTTPError as e:
        return {"error": str(e)}
