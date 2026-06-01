"""
ニュース自動取得 → IntelCard 自動生成パイプライン

Google News RSS 検索（無料・APIキー不要）から円谷の関心領域のニュースを取得し、
既存の card_generator で円谷向けインテリジェンスカードへ翻訳・保存する。

設計方針:
- 外部APIキー不要（Google News RSS のみ）
- 1回の実行で生成するカード数を上限管理（Claude 呼び出しコスト抑制）
- URL/タイトルで重複除外（再実行・複数クエリの重複に対応）
- RSS は本文を含まないため access_status="title_only" として扱い、
  card_generator 側で「タイトル/提供情報からの推定」と明記させる
"""

import os
import re
import html
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import httpx

from .card_generator import build_intel_card, make_card_id
from ..data.storage import Storage


# 円谷の関心領域に対応したデフォルト検索クエリ
# INTEL_NEWS_QUERIES 環境変数（カンマ区切り）で上書き可能
DEFAULT_QUERIES = [
    "ウルトラマン IP",
    "特撮 キャラクター ビジネス",
    "キャラクター ライセンス 海外",
    "アニメ 海外展開 ライセンス",
    "玩具 キャラクター 市場",
    "AI 音声 キャラクター",
    "コンテンツ 規制 子ども",
    "IP ビジネス 出資 提携",
]

GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
)


def _get_queries() -> List[str]:
    raw = os.getenv("INTEL_NEWS_QUERIES", "").strip()
    if raw:
        return [q.strip() for q in raw.split(",") if q.strip()]
    return DEFAULT_QUERIES


def _max_items() -> int:
    try:
        return max(1, int(os.getenv("INTEL_NEWS_MAX_ITEMS", "8")))
    except ValueError:
        return 8


def _per_query() -> int:
    try:
        return max(1, int(os.getenv("INTEL_NEWS_PER_QUERY", "3")))
    except ValueError:
        return 3


def _strip_html(text: str) -> str:
    """RSS description の HTML タグを除去して素のテキストにする"""
    if not text:
        return ""
    no_tags = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(no_tags).strip()


def _split_title_publisher(raw_title: str) -> tuple[str, Optional[str]]:
    """Google News のタイトル "見出し - 媒体名" を分解する"""
    if " - " in raw_title:
        head, _, pub = raw_title.rpartition(" - ")
        if head.strip():
            return head.strip(), pub.strip() or None
    return raw_title.strip(), None


def fetch_news_items(
    queries: Optional[List[str]] = None,
    per_query: Optional[int] = None,
    timeout: float = 20.0,
) -> List[Dict]:
    """Google News RSS から複数クエリでニュース項目を取得する。

    Returns: news dict のリスト（card_generator が受け取れる形）
    """
    queries = queries or _get_queries()
    per_query = per_query or _per_query()
    items: List[Dict] = []

    headers = {"User-Agent": "Mozilla/5.0 (compatible; TsuburayaIntel/1.0)"}
    with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
        for query in queries:
            url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
            try:
                resp = client.get(url)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
            except (httpx.HTTPError, ET.ParseError) as e:
                print(f"[intel] ニュース取得失敗 query='{query}': {e}")
                continue

            count = 0
            for item in root.iter("item"):
                if count >= per_query:
                    break
                raw_title = (item.findtext("title") or "").strip()
                if not raw_title:
                    continue
                title, publisher = _split_title_publisher(raw_title)
                link = (item.findtext("link") or "").strip()
                desc = _strip_html(item.findtext("description") or "")
                pub_date = (item.findtext("pubDate") or "").strip()
                source_el = item.find("source")
                if source_el is not None and source_el.text:
                    publisher = source_el.text.strip()

                items.append({
                    "title": title,
                    "url": link,
                    "publisher": publisher,
                    "summary": desc,
                    "published_at": pub_date,
                    "access_status": "title_only",
                    "user_note": f"自動取得 (検索: {query})",
                })
                count += 1

    return items


def _existing_keys() -> tuple[set, set]:
    """既存カードの URL 集合とタイトル集合を返す（重複除外用）"""
    urls: set = set()
    titles: set = set()
    for card in Storage.get_intel_cards(limit=1000):
        titles.add((card.get("title") or "").strip())
        for src in card.get("sources", []) or []:
            u = src.get("url")
            if u:
                urls.add(u)
    return urls, titles


def ingest_cards_for_date(
    date: Optional[str] = None,
    max_items: Optional[int] = None,
) -> Dict:
    """ニュースを取得し、新規分を IntelCard 化して保存する。

    Returns:
        {
          "date": str,
          "fetched": int,       # RSS から取得した総件数
          "created": int,       # 新規生成したカード数
          "skipped_dup": int,   # 重複でスキップした件数
          "card_ids": [...],
        }
    """
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    max_items = max_items or _max_items()

    fetched = fetch_news_items()
    seen_urls, seen_titles = _existing_keys()

    created_ids: List[str] = []
    skipped = 0
    seen_in_run: set = set()

    for news in fetched:
        if len(created_ids) >= max_items:
            break
        url = news.get("url") or ""
        title = (news.get("title") or "").strip()
        dedup_key = url or title
        # 既存カード・同一実行内の重複を除外
        if (
            (url and url in seen_urls)
            or (title and title in seen_titles)
            or dedup_key in seen_in_run
        ):
            skipped += 1
            continue
        seen_in_run.add(dedup_key)

        card = build_intel_card(news, date=date)
        Storage.save_intel_card(card)
        created_ids.append(card["id"])

    return {
        "date": date,
        "fetched": len(fetched),
        "created": len(created_ids),
        "skipped_dup": skipped,
        "card_ids": created_ids,
    }
