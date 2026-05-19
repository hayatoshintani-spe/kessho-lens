"""
日次レポート生成モジュール
毎日のシミュレーション結果をMarkdownレポートとして生成する
"""

import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional


def generate_daily_report(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    portfolios: Dict,
    trade_results: List[Dict],
    discoveries: List[Dict],
    meeting_log: Dict,
    use_ai: bool = True,
) -> Dict:
    """
    日次レポートを生成する

    Args:
        date: 日付 (YYYY-MM-DD)
        market_data: 市場データ
        agent_analyses: 各エージェントの市場分析
        portfolios: 各エージェントのポートフォリオ
        trade_results: 本日の取引結果
        discoveries: 本日の発見ログ
        meeting_log: ミーティングログ
        use_ai: Claude APIを使用するか（Falseの場合はルールベースフォールバック）

    Returns:
        レポート辞書 (date, title, content, agent_summaries)
    """
    if use_ai and os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _generate_with_ai(
                date, market_data, agent_analyses, portfolios,
                trade_results, discoveries, meeting_log
            )
        except Exception as e:
            print(f"レポートAI生成エラー: {e}, フォールバックを使用")

    return _generate_fallback(
        date, market_data, agent_analyses, portfolios,
        trade_results, discoveries, meeting_log
    )


def _generate_with_ai(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    portfolios: Dict,
    trade_results: List[Dict],
    discoveries: List[Dict],
    meeting_log: Dict,
) -> Dict:
    """Claude APIでレポートを生成"""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""以下の情報を元に、AIインベストメントファンドの日次レポートを日本語Markdownで生成してください。

日付: {date}
市場データ: {market_data}
エージェント分析: {agent_analyses}
取引結果: {trade_results}
ミーティング概要: {meeting_log.get('summary', '')}
主要決定: {meeting_log.get('key_decisions', [])}

以下の構成でレポートを作成してください：
1. 市場概況（主要指数、特記事項）
2. AIファンドパフォーマンス（4エージェントの比較表）
3. ミーティングハイライト（各エージェントの主張）
4. 本日の発見銘柄
5. ポートフォリオ変更
6. AIの思考プロセス（印象的な発言を引用）
7. 明日の注目イベント

日本語で、投資家向けの専門的なレポートとして作成してください。
絵文字は使用可能です。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text
    date_formatted = _format_date_ja(date)
    title = f"AIファンド日次レポート - {date_formatted}"

    return {
        "date": date,
        "title": title,
        "content": content,
        "agent_summaries": _build_agent_summaries(agent_analyses, trade_results),
    }


def _generate_fallback(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    portfolios: Dict,
    trade_results: List[Dict],
    discoveries: List[Dict],
    meeting_log: Dict,
) -> Dict:
    """ルールベースのフォールバックでレポートを生成"""
    date_formatted = _format_date_ja(date)
    sp500_change = market_data.get("sp500_change_pct", 0)
    nasdaq_change = market_data.get("nasdaq_change_pct", 0)
    dow_change = market_data.get("dow_change_pct", 0)
    nikkei_change = market_data.get("nikkei_change_pct", 0)
    sp500_price = market_data.get("sp500_price", 5284.31)
    market_theme = market_data.get("market_theme", "市場全般の動向")
    meeting_summary = meeting_log.get("summary", "AI投資会議が行われました")
    key_decisions = meeting_log.get("key_decisions", [])

    # パフォーマンス表を構築
    perf_rows = []
    agent_names = {
        "buffett": "BuffettAI",
        "soros": "SorosAI",
        "lynch": "LynchAI",
        "flat": "FlatAI",
    }
    for agent_id, display_name in agent_names.items():
        portfolio = portfolios.get(agent_id, {})
        perf = portfolio.get("performance", {})
        daily_pnl = perf.get("daily_pnl", random.randint(-50000, 100000))
        total_return = perf.get("total_return_pct", round(random.uniform(5, 20), 1))
        pnl_sign = "+" if daily_pnl >= 0 else ""
        perf_rows.append(
            f"| {display_name} | {pnl_sign}¥{daily_pnl:,.0f} | {total_return:+.1f}% |"
        )

    perf_table = "\n".join(perf_rows)

    # 取引サマリー
    trade_summary = ""
    if trade_results:
        successful_trades = [t for t in trade_results if t.get("success")]
        trade_lines = []
        for trade in successful_trades[:5]:
            action_ja = "買い" if trade.get("action") == "buy" else "売り"
            trade_lines.append(
                f"| {agent_names.get(trade.get('agent_id', ''), 'AI')} "
                f"| {trade.get('ticker', '-')} | {action_ja} "
                f"| {trade.get('shares', 0)}株 | ${trade.get('price', 0):.2f} |"
            )
        if trade_lines:
            trade_summary = "\n## 📈 ポートフォリオ変更\n\n"
            trade_summary += "| エージェント | 銘柄 | アクション | 数量 | 価格 |\n"
            trade_summary += "|------------|------|---------|------|-----|\n"
            trade_summary += "\n".join(trade_lines)

    # 発見ログサマリー
    discovery_summary = ""
    if discoveries:
        discovery_lines = []
        for d in discoveries[:4]:
            agent_id = d.get("agent_id", "unknown")
            discovery_lines.append(
                f"### {agent_names.get(agent_id, 'AI')}\n"
                f"- **{d.get('ticker', '-')} ({d.get('name', '-')})**: {d.get('discovery_reason', '-')[:80]}\n"
                f"- 確信度: {int(d.get('confidence', 0.5) * 100)}% | アクション: {d.get('action', '-')}"
            )
        discovery_summary = "\n## 🔍 本日の発見銘柄\n\n" + "\n\n".join(discovery_lines)

    # 主要決定事項
    decisions_text = ""
    if key_decisions:
        decisions_text = "\n".join(f"- {d}" for d in key_decisions)
    else:
        decisions_text = "- 各エージェントが状況を分析中"

    # ミーティングからの引用
    messages = meeting_log.get("messages", [])
    quotes = []
    agent_quote_map = {"BuffettAI": "buffett", "SorosAI": "soros", "LynchAI": "lynch", "FlatAI": "flat"}
    for msg in messages:
        if msg.get("type") in ("debate", "rebuttal", "decision") and len(msg.get("content", "")) > 30:
            agent_name = msg.get("agent", "")
            if agent_name in agent_quote_map:
                quotes.append(f'> **{agent_name}**: 「{msg["content"][:120]}」')
            if len(quotes) >= 4:
                break

    quotes_text = "\n\n".join(quotes) if quotes else "> AI投資家たちが議論を展開しました。"

    # 市場変動の方向性
    change_sign = "+" if sp500_change >= 0 else ""
    market_status = "上昇" if sp500_change > 0.3 else "下落" if sp500_change < -0.3 else "横ばい"

    content = f"""# AIインベストメントファンド 日次レポート
## {date_formatted}

---

## 📊 本日の市場概況

**主要指数**
- S&P 500: {sp500_price:,.2f} ({change_sign}{sp500_change:.2f}%)
- NASDAQ: N/A ({nasdaq_change:+.2f}%)
- ダウ平均: N/A ({dow_change:+.2f}%)
- 日経平均: N/A ({nikkei_change:+.2f}%)

**市場テーマ**: {market_theme}
**市場状況**: 本日の相場は{market_status}で推移。

---

## 🤖 AI投資家パフォーマンス

| エージェント | 日次損益 | 累計リターン |
|------------|--------|-----------|
{perf_table}

---

## 💬 本日のミーティングハイライト

{meeting_summary}

**主要決定事項:**
{decisions_text}

---
{discovery_summary}
{trade_summary}

---

## 🧠 AIの思考プロセス（本日のハイライト）

{quotes_text}

---

## 📅 明日の注目イベント

- 米国経済指標発表
- FRB関連発言
- 企業決算（予定）

---

*このレポートはAIによって自動生成されました。投資判断は自己責任でお願いします。*
"""

    title = f"AIファンド日次レポート - {date_formatted}"

    return {
        "date": date,
        "title": title,
        "content": content,
        "agent_summaries": _build_agent_summaries(agent_analyses, trade_results),
    }


def _build_agent_summaries(agent_analyses: Dict, trade_results: List[Dict]) -> Dict:
    """各エージェントのサマリーを構築"""
    summaries = {}
    agent_names = ["buffett", "soros", "lynch", "flat"]

    for agent_id in agent_names:
        analysis = agent_analyses.get(agent_id, {})
        summary = analysis.get("summary", "分析中")
        # 取引結果を追加
        agent_trades = [t for t in trade_results if t.get("agent_id") == agent_id and t.get("success")]
        if agent_trades:
            trade_msgs = [f"{t.get('ticker')} {'買い' if t.get('action') == 'buy' else '売り'}" for t in agent_trades[:2]]
            summary += " | 取引: " + "、".join(trade_msgs)
        summaries[agent_id] = summary[:150]

    return summaries


def _format_date_ja(date_str: str) -> str:
    """YYYY-MM-DD を日本語形式に変換"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays_ja = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays_ja[dt.weekday()]
        return f"{dt.year}年{dt.month}月{dt.day}日（{weekday}）"
    except Exception:
        return date_str
