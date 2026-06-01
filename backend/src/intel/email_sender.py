"""
Tsuburaya Intelligence Brief — メール配信モジュール

Resend API を使って Daily Brief を HTML 形式で経営層に送信する。
依存追加なし — httpx を直接呼ぶ。

設定環境変数:
    RESEND_API_KEY          Resend の API キー (re_xxx)
    BRIEF_EMAIL_FROM        差出人 (例: "Tsuburaya Intel <intel@example.com>")
    BRIEF_EMAIL_RECIPIENTS  カンマ区切りの宛先
    FRONTEND_URL            ブリーフ全文へのリンクのベースURL
"""
import html
import os
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from src.intel.categories import CATEGORY_META

_RESEND_API_URL = "https://api.resend.com/emails"
_DEFAULT_TIMEZONE = "Asia/Tokyo"


def is_enabled() -> bool:
    """メール配信に必要な環境変数が揃っているか"""
    return bool(
        os.getenv("RESEND_API_KEY")
        and os.getenv("BRIEF_EMAIL_FROM")
        and os.getenv("BRIEF_EMAIL_RECIPIENTS")
    )


def get_status() -> Dict:
    """設定状況（UI 表示用）"""
    recipients_raw = os.getenv("BRIEF_EMAIL_RECIPIENTS", "")
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    return {
        "enabled": is_enabled(),
        "has_api_key": bool(os.getenv("RESEND_API_KEY")),
        "from": os.getenv("BRIEF_EMAIL_FROM"),
        "recipients": recipients,
        "recipient_count": len(recipients),
        "frontend_url": os.getenv("FRONTEND_URL", ""),
        "timezone": os.getenv("BRIEF_TIMEZONE", _DEFAULT_TIMEZONE),
    }


# ─── HTML / Text 組み立て ────────────────────────────────────────────────


def _format_date_jp(date_str: str) -> str:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        # %-m / %-d は POSIX のみ。Windows 互換のため手書きフォーマット
        return f"{d.year}年{d.month}月{d.day}日"
    except Exception:
        return date_str


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _importance_badge(imp: str) -> tuple[str, str]:
    """重要度 → (ラベル, 色)"""
    table = {
        "A": ("経営アジェンダ", "#D85A30"),
        "B": ("事業部検討", "#C8860A"),
        "C": ("情報共有", "#2196F3"),
        "D": ("参考情報", "#7B7F8C"),
    }
    return table.get(imp, ("―", "#7B7F8C"))


def _category_label(cat: str) -> str:
    meta = CATEGORY_META.get(cat, {})
    return meta.get("label_short") or meta.get("label") or cat


def build_subject(brief: Dict, top_cards: List[Dict]) -> str:
    date_jp = _format_date_jp(brief.get("date", ""))
    titles: List[str] = []
    for c in top_cards[:3]:
        line = c.get("one_liner") or c.get("title", "")
        if line:
            titles.append(_truncate(line, 24))
    headline = " ／ ".join(titles) if titles else brief.get("title", "Daily Brief")
    return f"[Tsuburaya Intel] {date_jp} — {headline}"


def build_html(brief: Dict, top_cards: List[Dict], frontend_url: str) -> str:
    date = brief.get("date", "")
    date_jp = _format_date_jp(date)
    summary = html.escape(brief.get("executive_summary", ""))
    brief_url = f"{frontend_url}/intel/brief/{date}" if frontend_url else ""

    # 重要トピックス
    cards_html_parts: List[str] = []
    for c in top_cards[:5]:
        imp_label, imp_color = _importance_badge(c.get("importance", "C"))
        cat_label = _category_label(c.get("category", ""))
        title = html.escape(c.get("title", ""))
        one_liner = html.escape(c.get("one_liner", ""))
        card_url = (
            f"{frontend_url}/intel/cards/{c.get('id', '')}" if frontend_url else ""
        )
        link_open = (
            f'<a href="{card_url}" style="color:#1E2128;text-decoration:none;">'
            if card_url
            else ""
        )
        link_close = "</a>" if card_url else ""
        cards_html_parts.append(
            f"""
        <div style="border-left:3px solid {imp_color};padding:10px 14px;margin:10px 0;background:#F5F2EC;">
          <div style="font-size:11px;color:#7B7F8C;letter-spacing:0.05em;">
            <span style="background:{imp_color};color:#fff;padding:1px 7px;border-radius:3px;font-weight:bold;font-size:10px;">{imp_label}</span>
            <span style="margin-left:8px;">{html.escape(cat_label)}</span>
          </div>
          <div style="font-weight:bold;font-size:15px;color:#1E2128;margin-top:6px;line-height:1.4;">{link_open}{title}{link_close}</div>
          <div style="font-size:13px;color:#484C57;margin-top:4px;line-height:1.5;">{one_liner}</div>
        </div>"""
        )
    cards_html = "".join(cards_html_parts) or (
        '<p style="color:#7B7F8C;font-size:13px;">該当カードがありません</p>'
    )

    # 次アクション（urgent / this_week のみ）
    actions = [
        a
        for a in brief.get("next_actions", [])
        if a.get("priority") in ("urgent", "this_week")
    ]
    actions_html = ""
    if actions:
        items: List[str] = []
        for a in actions[:8]:
            icon = "🔴" if a.get("priority") == "urgent" else "🟡"
            who = html.escape(a.get("who", ""))
            what = html.escape(a.get("what", ""))
            deadline = a.get("deadline", "")
            deadline_str = (
                f' <span style="color:#7B7F8C;">— {html.escape(str(deadline))}</span>'
                if deadline
                else ""
            )
            items.append(
                f'<li style="margin:5px 0;font-size:13px;color:#1E2128;line-height:1.5;">'
                f"{icon} <strong>{who}</strong>: {what}{deadline_str}</li>"
            )
        actions_html = (
            '<h2 style="font-size:14px;color:#1E2128;margin:24px 0 8px;'
            'border-bottom:1px solid #DCD5C8;padding-bottom:4px;">次アクション</h2>'
            '<ul style="padding-left:20px;margin:6px 0;">' + "".join(items) + "</ul>"
        )

    # 事業機会
    opps = brief.get("business_opportunities", [])
    opps_html = ""
    if opps:
        items = [
            f'<li style="margin:4px 0;font-size:13px;color:#1E2128;line-height:1.5;">{html.escape(o)}</li>'
            for o in opps[:5]
        ]
        opps_html = (
            '<h2 style="font-size:14px;color:#1E2128;margin:24px 0 8px;'
            'border-bottom:1px solid #DCD5C8;padding-bottom:4px;">事業機会</h2>'
            '<ul style="padding-left:20px;margin:6px 0;">' + "".join(items) + "</ul>"
        )

    # リスク
    risks = brief.get("risks", [])
    risks_html = ""
    if risks:
        items = [
            f'<li style="margin:4px 0;font-size:13px;color:#1E2128;line-height:1.5;">{html.escape(r)}</li>'
            for r in risks[:5]
        ]
        risks_html = (
            '<h2 style="font-size:14px;color:#1E2128;margin:24px 0 8px;'
            'border-bottom:1px solid #DCD5C8;padding-bottom:4px;">識別リスク</h2>'
            '<ul style="padding-left:20px;margin:6px 0;">' + "".join(items) + "</ul>"
        )

    full_link_html = (
        f'<p style="text-align:center;margin:30px 0 10px;">'
        f'<a href="{brief_url}" style="background:#C8860A;color:#fff;padding:10px 22px;'
        f"border-radius:4px;text-decoration:none;font-size:13px;font-weight:bold;"
        f'display:inline-block;">ブリーフ全文を読む →</a></p>'
        if brief_url
        else ""
    )

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>Tsuburaya Intelligence Brief — {date_jp}</title>
</head>
<body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif;background:#EBE6DD;color:#1E2128;">
<div style="max-width:640px;margin:0 auto;background:#FAF7F1;padding:30px 24px;">

  <div style="border-bottom:2px solid #C8860A;padding-bottom:14px;margin-bottom:18px;">
    <div style="font-size:11px;color:#C8860A;letter-spacing:0.15em;text-transform:uppercase;font-weight:bold;">Tsuburaya Intelligence Brief</div>
    <h1 style="font-size:22px;margin:6px 0 0;color:#1E2128;font-weight:bold;">{date_jp} Daily Brief</h1>
  </div>

  <div style="background:#fff;padding:14px 16px;border-radius:4px;font-size:14px;line-height:1.8;color:#1E2128;margin-bottom:18px;">
    {summary}
  </div>

  <h2 style="font-size:14px;color:#1E2128;margin:24px 0 8px;border-bottom:1px solid #DCD5C8;padding-bottom:4px;">本日の重要トピックス</h2>
  {cards_html}

  {actions_html}
  {opps_html}
  {risks_html}

  {full_link_html}

  <div style="margin-top:30px;padding-top:12px;border-top:1px solid #DCD5C8;font-size:11px;color:#7B7F8C;text-align:center;line-height:1.6;">
    Tsuburaya Intelligence Brief は社内向けインテリジェンス配信です。<br>
    本メールに記載の解釈・示唆は AI 生成のドラフトを含みます。最終判断は責任者にて。
  </div>
</div>
</body>
</html>"""


def build_text(brief: Dict, top_cards: List[Dict], frontend_url: str) -> str:
    date = brief.get("date", "")
    date_jp = _format_date_jp(date)
    brief_url = f"{frontend_url}/intel/brief/{date}" if frontend_url else ""

    lines: List[str] = [
        f"Tsuburaya Intelligence Brief — {date_jp}",
        "=" * 50,
        "",
        brief.get("executive_summary", ""),
        "",
        "■ 本日の重要トピックス",
    ]
    if not top_cards:
        lines.append("  （該当カードなし）")
    for c in top_cards[:5]:
        imp_label, _ = _importance_badge(c.get("importance", "C"))
        lines.append(f"  [{imp_label}] {c.get('title', '')}")
        if c.get("one_liner"):
            lines.append(f"    {c.get('one_liner')}")
        lines.append("")

    actions = [
        a
        for a in brief.get("next_actions", [])
        if a.get("priority") in ("urgent", "this_week")
    ]
    if actions:
        lines.append("■ 次アクション")
        for a in actions[:8]:
            icon = "[緊急]" if a.get("priority") == "urgent" else "[今週]"
            deadline = f" — {a.get('deadline')}" if a.get("deadline") else ""
            lines.append(
                f"  {icon} {a.get('who', '')}: {a.get('what', '')}{deadline}"
            )
        lines.append("")

    if brief.get("business_opportunities"):
        lines.append("■ 事業機会")
        for o in brief["business_opportunities"][:5]:
            lines.append(f"  - {o}")
        lines.append("")

    if brief.get("risks"):
        lines.append("■ 識別リスク")
        for r in brief["risks"][:5]:
            lines.append(f"  - {r}")
        lines.append("")

    if brief_url:
        lines.append(f"ブリーフ全文: {brief_url}")
    lines.extend(["", "---", "Tsuburaya Intelligence Brief"])

    return "\n".join(lines)


# ─── 送信 ────────────────────────────────────────────────────────────────


def send_brief_email(
    brief: Dict,
    top_cards: List[Dict],
    recipients: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict:
    """Daily Brief をメール配信する。

    Returns:
        {"status": "sent"|"skipped"|"error", ...}
    """
    api_key = os.getenv("RESEND_API_KEY")
    from_addr = os.getenv("BRIEF_EMAIL_FROM")

    if not api_key or not from_addr:
        return {
            "status": "skipped",
            "reason": "RESEND_API_KEY または BRIEF_EMAIL_FROM が未設定です",
        }

    if recipients is None:
        recipients_raw = os.getenv("BRIEF_EMAIL_RECIPIENTS", "")
        recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    if not recipients:
        return {"status": "skipped", "reason": "送信先 (BRIEF_EMAIL_RECIPIENTS) が未設定です"}

    frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
    subject = build_subject(brief, top_cards)
    html_body = build_html(brief, top_cards, frontend_url)
    text_body = build_text(brief, top_cards, frontend_url)

    if dry_run:
        return {
            "status": "dry_run",
            "subject": subject,
            "recipients": recipients,
            "html_preview": html_body[:500],
            "text_preview": text_body[:500],
        }

    try:
        resp = httpx.post(
            _RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_addr,
                "to": recipients,
                "subject": subject,
                "html": html_body,
                "text": text_body,
            },
            timeout=20.0,
        )
        if resp.status_code >= 400:
            return {
                "status": "error",
                "error": f"Resend API error {resp.status_code}: {resp.text[:300]}",
                "recipients": recipients,
                "subject": subject,
            }
        data = resp.json()
        return {
            "status": "sent",
            "message_id": data.get("id"),
            "recipients": recipients,
            "subject": subject,
        }
    except httpx.HTTPError as e:
        return {
            "status": "error",
            "error": f"送信エラー: {type(e).__name__}: {e}",
            "recipients": recipients,
        }
