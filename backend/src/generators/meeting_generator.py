"""
ミーティングログ生成モジュール
AIエージェント間の議論を生成する
"""

import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.agents import get_all_agents, get_agent


# ミーティングのシナリオテンプレート
_MEETING_SCENARIOS = [
    {
        "theme": "AI半導体バブルの継続性",
        "trigger": "NVDA急騰",
        "key_question": "AI関連株はバブルか、それとも実需か？",
    },
    {
        "theme": "FRBの政策転換と株式市場",
        "trigger": "FRB利下げ観測",
        "key_question": "利下げはグロース株の追い風になるか？",
    },
    {
        "theme": "日本株の復活",
        "trigger": "日銀政策変更",
        "key_question": "日本株に今投資すべきか？",
    },
    {
        "theme": "インフレ再燃リスク",
        "trigger": "CPI上昇",
        "key_question": "インフレ下でどのセクターが有利か？",
    },
    {
        "theme": "消費者支出の動向",
        "trigger": "小売売上高発表",
        "key_question": "消費者の財布は開いているか、閉じているか？",
    },
]

# 各エージェントの会話スタイル
_OPENING_MESSAGES = {
    "buffett": [
        "本日の市場を見てください。{theme}について議論が必要です。私の見解は長期的な企業価値に基づいています。",
        "おはようございます。{theme}に関して、私はいつも通り長期的な視点で考えています。",
        "今日のテーマは{theme}ですね。私のアプローチは変わりません。20年後も輝く企業を探すことです。",
    ],
    "soros": [
        "重要な動きがあります。{theme}は再帰性理論から見ると非常に興味深い展開です。",
        "市場は間違っています。{theme}について、私のマクロモデルが明確なシグナルを出しています。",
        "皆さん、{theme}について話しましょう。マクロの転換点が近づいています。",
    ],
    "lynch": [
        "今日のテーマは{theme}ですね。先週、街を歩いていて気づいたことがあります...",
        "{theme}について、日常の観察から面白い発見がありました。",
        "皆さん、{theme}に関して、私の現地調査の結果を報告します。",
    ],
    "flat": [
        "皆さんが{theme}について議論している間に、データを確認しました。",
        "{theme}についての皆さんの議論は理解できます。しかし統計は別のことを示しています。",
        "本日のテーマ{theme}について。皆さんの直感より、数字を見てください。",
    ],
}

_DEBATE_MESSAGES = {
    "buffett": [
        "興味深い見方ですが、私は企業の本質的価値に集中します。{context}",
        "短期的な動きは関係ありません。20年後の姿を見てください。{context}",
        "私がKOを持ち続けるのはなぜか。{context}それが答えです。",
        "競争優位性（堀）はどこにありますか？{context}",
    ],
    "soros": [
        "再帰性の観点から言えば、{context}市場の認識が現実を変えています。",
        "{context}これはマクロの転換点のシグナルです。",
        "市場は常に間違っています。今回の間違いは{context}",
        "私のポジションは{context}に基づいています。マクロを見てください。",
    ],
    "lynch": [
        "先週、{context}について実際に確認してきました。現地調査は嘘をつきません。",
        "PEGレシオで計算すると、{context}まだ割安かもしれません。",
        "普通の人が使い始めた製品・サービスは強い。{context}",
        "テンバガーの匂いがします。{context}",
    ],
    "flat": [
        "データを見てください。{context}これは統計的に有意ではありません。",
        "過去20年のデータによれば、{context}アクティブ運用は市場に負けます。",
        "{context}これはアンカリングバイアスです。",
        "感情ではなく数字で話しましょう。{context}",
    ],
}

_DECISION_MESSAGES = {
    "buffett": [
        "私の判断：{holdings}を保有継続します。急ぐ必要はありません。",
        "今日の決定：{action}。良い企業は20年持てます。",
        "私はポートフォリオを変えません。{reason}",
    ],
    "soros": [
        "本日の決定：{action}。マクロの流れに従います。",
        "{ticker}を{action}します。{reason}",
        "ポジションを調整します。{action}。状況が変わればまた変えます。",
    ],
    "lynch": [
        "今日は{action}します。{reason}現地調査の結論です。",
        "{ticker}の目標価格を{target}に設定します。{reason}",
        "様子見を継続します。{reason}もう少し観察が必要です。",
    ],
    "flat": [
        "リバランスを実施します。{action}。理論通りです。",
        "本日の取引：{action}。コスト管理が最優先です。",
        "皆さんのアクティブ運用の結果を来月確認しましょう。私はSPY保有継続。",
    ],
}


def generate_meeting_log(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    trade_proposals: Dict,
) -> Dict:
    """
    ミーティングログを生成する

    Args:
        date: 日付 (YYYY-MM-DD)
        market_data: 市場データ
        agent_analyses: 各エージェントの市場分析
        trade_proposals: 各エージェントの取引提案

    Returns:
        ミーティングログ辞書
    """
    # AIを使う場合とフォールバックを分岐
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _generate_with_ai(date, market_data, agent_analyses, trade_proposals)
        except Exception as e:
            print(f"AI生成エラー: {e}, フォールバックを使用")

    return _generate_fallback(date, market_data, agent_analyses, trade_proposals)


def _generate_with_ai(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    trade_proposals: Dict,
) -> Dict:
    """Claude APIを使ってミーティングログを生成"""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    market_theme = market_data.get("market_theme", "市場全般")
    sp500_change = market_data.get("sp500_change_pct", 0)

    prompt = f"""以下の状況でAI投資会議のチャットログを生成してください。

日付: {date}
市場テーマ: {market_theme}
S&P500変動: {sp500_change:+.2f}%

各AIエージェントの分析:
{agent_analyses}

取引提案:
{trade_proposals}

4人のAI投資家（BuffettAI、SorosAI、LynchAI、FlatAI）が激論を交わすチャットログを生成してください。
- BuffettAI: 長期バリュー、配当重視、「20年持てる株か？」
- SorosAI: マクロ・再帰性理論、「市場は常に間違っている」
- LynchAI: 日常観察・PEGレシオ、「自分が理解できる株を買え」
- FlatAI: インデックス派、「アクティブ運用は全員負ける」

以下のJSON形式で返してください:
{{
  "summary": "会議の要約（日本語、100字以内）",
  "key_decisions": ["決定1", "決定2", "決定3"],
  "messages": [
    {{
      "agent": "BuffettAI",
      "time": "09:00",
      "content": "発言内容（日本語）",
      "type": "opening"
    }},
    ...（最低10メッセージ）
  ]
}}

各メッセージのtypeは: opening, debate, proposal, rebuttal, decision のいずれか。
全て日本語で、個性を際立てた激論にしてください。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text
    import json
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    ai_data = json.loads(response_text[start:end])

    return {
        "date": date,
        "participants": ["BuffettAI", "SorosAI", "LynchAI", "FlatAI"],
        "summary": ai_data.get("summary", "AI投資会議が行われました"),
        "market_theme": market_theme,
        "key_decisions": ai_data.get("key_decisions", []),
        "messages": ai_data.get("messages", []),
    }


def _generate_fallback(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    trade_proposals: Dict,
) -> Dict:
    """ルールベースのフォールバックでミーティングログを生成"""
    market_theme = market_data.get("market_theme", "本日の市場動向")
    sp500_change = market_data.get("sp500_change_pct", 0)
    scenario = random.choice(_MEETING_SCENARIOS)

    agents_order = ["soros", "buffett", "lynch", "flat"]
    messages = []
    time_minutes = 0

    def format_time(minutes: int) -> str:
        hour = 9 + minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"

    # オープニング（ソロスから始まることが多い）
    for agent_id in agents_order[:2]:
        agent = get_agent(agent_id)
        template = random.choice(_OPENING_MESSAGES.get(agent_id, ["{theme}について話しましょう。"]))
        content = template.format(theme=market_theme)
        messages.append({
            "agent": agent.name,
            "time": format_time(time_minutes),
            "content": content,
            "type": "opening",
        })
        time_minutes += random.randint(3, 5)

    # 残りのエージェントの反応
    for agent_id in agents_order[2:]:
        agent = get_agent(agent_id)
        analysis = agent_analyses.get(agent_id, {})
        summary = analysis.get("summary", "市場を分析中")
        messages.append({
            "agent": agent.name,
            "time": format_time(time_minutes),
            "content": summary,
            "type": "debate",
        })
        time_minutes += random.randint(3, 5)

    # 取引提案と反論
    proposals_made = []
    for proposer_id in ["soros", "lynch"]:
        proposals = trade_proposals.get(proposer_id, [])
        if proposals:
            top_proposal = proposals[0]
            ticker = top_proposal.get("ticker", "SPY")
            action = top_proposal.get("action", "buy")
            reason = top_proposal.get("reason", "分析に基づく判断")
            action_ja = "買い" if action == "buy" else "売り" if action == "sell" else "保有継続"

            proposer = get_agent(proposer_id)
            messages.append({
                "agent": proposer.name,
                "time": format_time(time_minutes),
                "content": f"{ticker}を{action_ja}することを提案します。理由：{reason}",
                "type": "proposal",
            })
            proposals_made.append((proposer_id, ticker, action_ja))
            time_minutes += random.randint(3, 6)

            # バフェットかフラットが反論
            rebuttal_id = "buffett" if proposer_id == "soros" else "flat"
            rebuttal_agent = get_agent(rebuttal_id)
            rebuttal = rebuttal_agent.respond_to_peer(proposer.name, f"{ticker}の{action_ja}を推奨")
            messages.append({
                "agent": rebuttal_agent.name,
                "time": format_time(time_minutes),
                "content": rebuttal,
                "type": "rebuttal",
            })
            time_minutes += random.randint(2, 4)

    # バフェットの反論
    buffett = get_agent("buffett")
    buffett_analysis = agent_analyses.get("buffett", {})
    buffett_summary = buffett_analysis.get("summary", "長期的な視点で考えます。")
    messages.append({
        "agent": buffett.name,
        "time": format_time(time_minutes),
        "content": buffett_summary,
        "type": "debate",
    })
    time_minutes += random.randint(3, 5)

    # フラットのデータ攻撃
    flat = get_agent("flat")
    flat_analysis = agent_analyses.get("flat", {})
    flat_summary = flat_analysis.get("summary", "データを見てください。統計的には全員負けます。")
    messages.append({
        "agent": flat.name,
        "time": format_time(time_minutes),
        "content": flat_summary,
        "type": "rebuttal",
    })
    time_minutes += random.randint(3, 5)

    # 決定フェーズ
    for agent_id in agents_order:
        agent = get_agent(agent_id)
        proposals = trade_proposals.get(agent_id, [])
        if proposals:
            top = proposals[0]
            ticker = top.get("ticker", "SPY")
            action = top.get("action", "hold")
            action_ja = "買い" if action == "buy" else "売り" if action == "sell" else "保有継続"
            reason = top.get("reason", "")
            content = f"本日の決定：{ticker}を{action_ja}します。{reason}"
        else:
            content = f"本日は現状維持とします。{agent.catchphrase}"

        messages.append({
            "agent": agent.name,
            "time": format_time(time_minutes),
            "content": content,
            "type": "decision",
        })
        time_minutes += random.randint(2, 3)

    # サマリーと主要決定事項を生成
    key_decisions = []
    for agent_id, ticker, action_ja in proposals_made:
        agent = get_agent(agent_id)
        key_decisions.append(f"{ticker}: {agent.display_name}が{action_ja}")

    if sp500_change > 0.5:
        sentiment = "強気相場の継続"
    elif sp500_change < -0.5:
        sentiment = "弱気相場への警戒"
    else:
        sentiment = "横ばい相場での戦略議論"

    summary = f"{market_theme}を巡る議論。{sentiment}。各エージェントが独自の哲学で主張を展開。"

    return {
        "date": date,
        "participants": ["BuffettAI", "SorosAI", "LynchAI", "FlatAI"],
        "summary": summary,
        "market_theme": market_theme,
        "key_decisions": key_decisions or [
            "各エージェントが現状維持を判断",
            "次回のデータ発表まで様子見",
        ],
        "messages": messages,
    }
