"""
Daily/Weekly/Monthly ブリーフ合成器
カード群と会議ログから経営向けブリーフを組み立てる
"""

from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from .categories import CATEGORY_META
from .experts import IMPORTANCE_LABELS


def _importance_rank(card: Dict) -> int:
    """A=0, B=1, C=2, D=3 でソートできる数値"""
    return {"A": 0, "B": 1, "C": 2, "D": 3}.get(card.get("importance", "D"), 9)


def _format_importance_chip(imp: str) -> str:
    meta = IMPORTANCE_LABELS.get(imp, IMPORTANCE_LABELS["D"])
    return f"**[{imp}] {meta['label']}**"


def select_top_cards(cards: List[Dict], n: int = 5) -> List[Dict]:
    """重要度順でトップN件を選ぶ"""
    sorted_cards = sorted(cards, key=lambda c: (_importance_rank(c), c.get("date", "")))
    return sorted_cards[:n]


def build_daily_brief(
    date: str,
    cards: List[Dict],
    council_session_id: Optional[str] = None,
) -> Dict:
    """
    Daily Intelligence Briefを組み立てる

    cards: その日のIntelCard群
    """
    if not cards:
        return _empty_daily_brief(date)

    top_cards = select_top_cards(cards, 5)

    # カテゴリ別の集計
    cat_counter = Counter(c.get("category") for c in cards)
    a_cards = [c for c in cards if c.get("importance") == "A"]
    b_cards = [c for c in cards if c.get("importance") == "B"]

    # 機会・リスクの集約
    all_opportunities = []
    all_risks = []
    all_actions = []
    for c in top_cards:
        insight = c.get("insight", {})
        for opp in insight.get("business_opportunity", []):
            all_opportunities.append(f"{opp}（{c.get('title')}）")
        for risk in insight.get("risk", []):
            all_risks.append(f"{risk}（{c.get('title')}）")
        for act in c.get("actions", []):
            all_actions.append(act)

    # 経営層向け要約
    exec_summary = _compose_exec_summary(top_cards, a_cards, cat_counter)

    # セクション構築
    sections = []

    # 上位トピックスセクション
    sections.append({
        "heading": "🔝 今日の重要トピックス上位5件",
        "body": _format_top_topics_md(top_cards),
    })

    if a_cards:
        sections.append({
            "heading": "🚨 経営アジェンダ化候補（重要度A）",
            "body": _format_cards_section(a_cards),
        })

    sections.append({
        "heading": "🎯 経営論点",
        "body": _compose_management_issues(top_cards),
    })

    sections.append({
        "heading": "🌱 事業機会",
        "body": "\n".join(f"- {o}" for o in all_opportunities[:8]) or "_該当なし_",
    })

    sections.append({
        "heading": "⚠️ リスク・脅威",
        "body": "\n".join(f"- {r}" for r in all_risks[:8]) or "_該当なし_",
    })

    sections.append({
        "heading": "✅ 次アクション",
        "body": _format_actions_md(all_actions[:10]),
    })

    sections.append({
        "heading": "📇 Notion / DB登録用記事カード",
        "body": _format_card_index(top_cards),
    })

    return {
        "date": date,
        "brief_type": "daily",
        "title": f"Tsuburaya Intelligence Brief — {date}",
        "top_topics": [c.get("id") for c in top_cards],
        "executive_summary": exec_summary,
        "business_opportunities": all_opportunities[:8],
        "risks": all_risks[:8],
        "next_actions": all_actions[:10],
        "sections": sections,
        "council_session_id": council_session_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _compose_exec_summary(
    top_cards: List[Dict],
    a_cards: List[Dict],
    cat_counter: Counter,
) -> str:
    """経営層向けの2-3文サマリー"""
    if not top_cards:
        return "本日特筆すべき動きなし。"

    leading = top_cards[0]
    leading_title = leading.get("title", "")

    parts = []
    parts.append(f"本日の最重要トピックは『{leading_title}』。")

    if a_cards:
        a_count = len(a_cards)
        parts.append(
            f"重要度A（経営アジェンダ化）が{a_count}件あり、役員会議題への上申準備を推奨する。"
        )

    # ドミナントなカテゴリ
    if cat_counter:
        top_cat_id, top_cat_count = cat_counter.most_common(1)[0]
        cat_label = CATEGORY_META.get(top_cat_id, {}).get("label_short", top_cat_id)
        if top_cat_count >= 2:
            parts.append(f"本日は『{cat_label}』カテゴリの動きが集中（{top_cat_count}件）。")

    return " ".join(parts)


def _compose_management_issues(top_cards: List[Dict]) -> str:
    """経営論点セクション"""
    lines = []
    for i, c in enumerate(top_cards, 1):
        what_means = c.get("insight", {}).get("what_it_means", "")
        if what_means:
            lines.append(f"{i}. **{c.get('title')}** — {what_means}")
    return "\n".join(lines) or "_該当なし_"


def _format_top_topics_md(top_cards: List[Dict]) -> str:
    lines = []
    for i, c in enumerate(top_cards, 1):
        chip = _format_importance_chip(c.get("importance", "D"))
        cat = CATEGORY_META.get(c.get("category", ""), {})
        cat_label = cat.get("label_short", "")
        one_liner = c.get("one_liner", "")
        lines.append(f"{i}. {chip} `{cat_label}` **{c.get('title')}** — {one_liner}")
    return "\n".join(lines)


def _format_cards_section(cards: List[Dict]) -> str:
    """カードをまとめたセクション本文"""
    parts = []
    for c in cards:
        parts.append(f"### {c.get('title')}")
        parts.append(f"**事実:** {c.get('fact', '')}")
        parts.append(f"**解釈:** {c.get('interpretation', '')}")
        what_means = c.get("insight", {}).get("what_it_means", "")
        if what_means:
            parts.append(f"**円谷への示唆:** {what_means}")
        actions = c.get("actions", [])
        if actions:
            parts.append("**次アクション:**")
            for a in actions:
                parts.append(f"- ({a.get('priority','')}) {a.get('who')}: {a.get('what')}")
        parts.append("")
    return "\n".join(parts)


def _format_actions_md(actions: List[Dict]) -> str:
    if not actions:
        return "_該当なし_"
    pri_order = {"urgent": 0, "this_week": 1, "this_month": 2, "watch": 3}
    sorted_actions = sorted(actions, key=lambda a: pri_order.get(a.get("priority"), 9))
    lines = []
    pri_label = {
        "urgent": "🔴 緊急",
        "this_week": "🟡 今週",
        "this_month": "🟢 今月",
        "watch": "⚪ 継続監視",
    }
    for a in sorted_actions:
        p = a.get("priority", "watch")
        lines.append(f"- {pri_label.get(p, p)} | **{a.get('who')}**: {a.get('what')}")
    return "\n".join(lines)


def _format_card_index(cards: List[Dict]) -> str:
    """Notion DB登録用の一覧"""
    lines = ["| 重要度 | カテゴリ | タイトル | 担当エキスパート |", "|---|---|---|---|"]
    for c in cards:
        imp = c.get("importance", "D")
        cat = CATEGORY_META.get(c.get("category", ""), {}).get("label_short", "")
        agents = ", ".join(c.get("related_agents", [])[:2])
        lines.append(f"| {imp} | {cat} | {c.get('title')} | {agents} |")
    return "\n".join(lines)


def _empty_daily_brief(date: str) -> Dict:
    return {
        "date": date,
        "brief_type": "daily",
        "title": f"Tsuburaya Intelligence Brief — {date}",
        "top_topics": [],
        "executive_summary": "本日カード未登録。",
        "business_opportunities": [],
        "risks": [],
        "next_actions": [],
        "sections": [{
            "heading": "本日の状況",
            "body": "本日のインテリジェンスカードが登録されていません。"
                    "カードを生成してから再度ブリーフを組み立ててください。",
        }],
        "council_session_id": None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_weekly_brief(
    week_start: str,
    cards: List[Dict],
    daily_briefs: List[Dict],
) -> Dict:
    """週次エグゼクティブブリーフを組み立て"""
    top_cards = select_top_cards(cards, 7)
    a_cards = [c for c in cards if c.get("importance") == "A"]
    b_cards = [c for c in cards if c.get("importance") == "B"]

    # 部署別アクション集約（who に部署名が含まれる前提）
    dept_actions: Dict[str, List[str]] = {}
    for c in top_cards:
        for a in c.get("actions", []):
            who = a.get("who", "未指定")
            dept_actions.setdefault(who, []).append(a.get("what", ""))

    # 来週のウォッチテーマ
    watch_themes = []
    for c in cards:
        for act in c.get("actions", []):
            if act.get("priority") == "watch":
                watch_themes.append(act.get("what", ""))

    return {
        "date": week_start,
        "brief_type": "weekly",
        "title": f"Weekly Executive Brief — week of {week_start}",
        "week_of": week_start,
        "key_changes": [c.get("title") for c in a_cards[:5]],
        "opportunities": _flatten_opportunities(top_cards)[:8],
        "risks": _flatten_risks(top_cards)[:8],
        "decisions_pending": [c.get("title") for c in a_cards],
        "actions_by_department": {k: v[:4] for k, v in dept_actions.items()},
        "watch_themes_next_week": watch_themes[:8],
        "card_count": len(cards),
        "a_count": len(a_cards),
        "b_count": len(b_cards),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _flatten_opportunities(cards: List[Dict]) -> List[str]:
    out = []
    for c in cards:
        for o in c.get("insight", {}).get("business_opportunity", []):
            out.append(f"{o}（{c.get('title')}）")
    return out


def _flatten_risks(cards: List[Dict]) -> List[str]:
    out = []
    for c in cards:
        for r in c.get("insight", {}).get("risk", []):
            out.append(f"{r}（{c.get('title')}）")
    return out
