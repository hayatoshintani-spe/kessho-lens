"""
ミーティングログ生成モジュール
7名のAI投資家による高度な投資委員会会議を生成する
"""

import json
import os
import random
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.agents import get_agent, get_fund_agents


# ─── システムプロンプト ──────────────────────────────────────────────────────────

_MEETING_SYSTEM_PROMPT = """あなたは7名のAI投資家による高度な投資委員会会議のファシリテーターです。
以下の要件に従い、実際の市場分析に裏付けられた高精度な投資会議チャットログを生成してください。

━━ 参加者と役割 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SorosAI    : 議長。グローバルマクロ・再帰性理論。大胆なポジション転換。
             口癖「市場は常に間違っている」
BuffettAI  : バリュー長期投資。企業の堀と本質的価値。
             口癖「20年持てる株か？」
LynchAI    : グロース・日常観察。PEGレシオ。テンバガー発掘。
             口癖「自分が理解できる株を買え」
FlatAI     : インデックス・効率市場仮説。アクティブ運用批判。データ重視。
             口癖「アクティブ運用は全員負ける」
MacroAI    : マクロ経済専門家。Fed/日銀政策・金利・為替・インフレを精密に分析。
             具体的な金利水準・イールドカーブ・政策動向を引用する。
             断定を避け「〜のリスクが意識されている」「〜の確率が上昇」と表現する。
QuantAI    : 定量分析専門家。PER/PBR/EV-EBITDA/配当利回り/モメンタムで銘柄スコアリング。
             「織り込み度」の評価が得意。感情なく数字だけで判断する。
RiskAI     : リスク管理専門家・議論の悪魔の代弁者。
             すべての投資提案に必ず反証を3つ以上出す。投資仮説が崩れる具体的な条件を明文化する。
             口癖「何が間違えるか考えろ」
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ 会議アジェンダ（この順序で進めること）━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
フェーズ1  [MacroAI] 市場データ確認
  → 金利・為替・株式指数を確認。断定でなく傾向として述べる。
フェーズ2  [SorosAI] 前回判断の振り返り
  → 前回の決定が市場の動きと照らして正しかったかを評価する。
フェーズ3  [QuantAI] 今日の銘柄スクリーニング
  → 上昇・下落銘柄のバリュエーションを確認し、織り込み度を評価する。
フェーズ4  [各エージェント] 市場テーマ整理と投資提案
  → テーマを識別し、具体的な銘柄・ETF・配分を提案する。
フェーズ5  [RiskAI] 全提案への反証（必須・省略禁止）
  → 各提案について「なぜ間違える可能性があるか」を3つ以上指摘する。
フェーズ6  [QuantAI + MacroAI] 織り込み度の議論
  → 提案銘柄がすでに材料を織り込んでいないかを確認する。
フェーズ7  [SorosAI] 3シナリオ分析
  → ベース・ブル・ベアを確率（合計100%）とともに提示する。
フェーズ8  [全員] 執行ルールの合意
  → いつ・いくら・どのように・何分割で買うかを決める。一括買いは原則禁止。
フェーズ9  [RiskAI] 投資仮説と撤退条件の明文化
  → 仮説が崩れる数値条件・イベントを記録する。
フェーズ10 [SorosAI] 次回監視項目の確認
  → FOMC・日銀・決算・経済指標など次回までに監視すべき項目を列挙する。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━ 必須の表現ルール ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 「年内2回の利上げが示唆された」「FRBは利上げを決定した」（過度な断定）
✅ 「利上げ再開リスクが市場で意識され始めた」「FedWatchの利上げ確率が上昇傾向にある」

❌ 「輸出株は確実に上がる」
✅ 「現在の為替水準では輸出株に追い風だが、すでに相当程度折り込まれている可能性がある」

❌ 「円安が続く」（根拠なき断定）
✅ 「日米金利差が維持される限り、円安バイアスは継続する傾向にあるが、日銀の政策転換リスクには注意が必要」
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

全7エージェントが複数回発言すること。日本語で、各エージェントの個性を際立てること。"""


# ─── ルールベース フォールバック用テンプレート ──────────────────────────────────

_FALLBACK_SCENARIOS = [
    "米金利動向と日本株の行方",
    "AI・半導体相場の継続性と過熱感",
    "円安の恩恵と織り込み度の評価",
    "インフレ再燃リスクとディフェンシブ銘柄",
    "景気後退シグナルと防御的ポジショニング",
]


# ─── メイン生成関数 ──────────────────────────────────────────────────────────────

def generate_meeting_log(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    trade_proposals: Dict,
    previous_meeting: Optional[Dict] = None,
    use_ai: bool = True,
) -> Dict:
    """ミーティングログを生成する（Claude API優先・ルールベースフォールバック）"""
    if use_ai and os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _generate_with_ai(
                date, market_data, agent_analyses, trade_proposals, previous_meeting
            )
        except Exception as e:
            print(f"[meeting_generator] AI生成エラー: {e}, フォールバックを使用")

    return _generate_fallback(date, market_data, agent_analyses, trade_proposals)


# ─── Claude API 生成 ─────────────────────────────────────────────────────────────

def _generate_with_ai(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    trade_proposals: Dict,
    previous_meeting: Optional[Dict],
) -> Dict:
    """Claude API を使って高品質な会議ログを生成する"""
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    market_theme = market_data.get("market_theme", "市場全般")
    sp500_change = market_data.get("sp500_change_pct", 0)
    usd_jpy = market_data.get("usd_jpy", 150.0)
    vix = market_data.get("vix", 18.0)

    # 当日の市場データをフォーマット
    tickers = market_data.get("tickers", [])
    top_gainers = sorted(
        [t for t in tickers if t.get("change_pct", 0) > 0],
        key=lambda x: x.get("change_pct", 0), reverse=True
    )[:3]
    top_losers = sorted(
        [t for t in tickers if t.get("change_pct", 0) < 0],
        key=lambda x: x.get("change_pct", 0)
    )[:3]

    def fmt_tickers(ts):
        return "、".join(f"{t['ticker']}({t.get('change_pct', 0):+.1f}%)" for t in ts) or "なし"

    # 前回判断のサマリー
    prev_decisions_text = "（初回会議のため前回なし）"
    if previous_meeting:
        prev_date = previous_meeting.get("date", "不明")
        prev_decisions = previous_meeting.get("key_decisions", [])
        prev_decisions_text = f"【{prev_date}の決定】\n" + "\n".join(
            f"  - {d}" for d in prev_decisions[:5]
        )

    # 各エージェントの分析サマリー
    analyses_text = "\n".join(
        f"  [{aid.upper()}] {a.get('summary', '分析中')}"
        for aid, a in agent_analyses.items()
    )

    # 取引提案サマリー
    proposals_text = ""
    for agent_id, props in trade_proposals.items():
        for p in props[:2]:
            action_ja = {"buy": "買い", "sell": "売り", "hold": "保有継続"}.get(
                p.get("action", "hold"), p.get("action", "")
            )
            proposals_text += (
                f"  [{agent_id.upper()}] {p.get('ticker')} → {action_ja}"
                f" 確信度{p.get('confidence', 0):.0%} 理由：{p.get('reason', '')}\n"
            )

    user_message = f"""本日の投資委員会会議を生成してください。

━━ 本日の市場データ ━━━━━━━━━━━━━━━━━━━━━━━━
日付        : {date}
市場テーマ  : {market_theme}
S&P500変動  : {sp500_change:+.2f}%
USD/JPY     : {usd_jpy:.1f}円
VIX         : {vix:.1f}
上昇銘柄TOP3: {fmt_tickers(top_gainers)}
下落銘柄TOP3: {fmt_tickers(top_losers)}

━━ 前回の会議決定（振り返り対象） ━━━━━━━━━━━━━━
{prev_decisions_text}

━━ 本日の各エージェント分析 ━━━━━━━━━━━━━━━━━━━
{analyses_text}

━━ 本日の取引提案 ━━━━━━━━━━━━━━━━━━━━━━━━━━
{proposals_text or "  （提案なし）"}

━━ 出力フォーマット（JSONのみ・説明文なし）━━━━━━━━━
{{
  "summary": "会議要約（150字以内、市場前提と決定内容を含む）",
  "key_decisions": [
    "【採用】XXXXを3分割で打診。初弾はYYY円割れで。仮説：ZZZ。撤退：WWW",
    "【現状維持】XXXX。理由：YYY",
    "【要監視】XXXX。次のトリガー：YYY"
  ],
  "scenarios": [
    {{"name": "ベース", "probability": 50,
      "description": "シナリオの説明（金利・為替・株の方向性）",
      "portfolio_action": "このシナリオでの配分方針"}},
    {{"name": "ブル", "probability": 25,
      "description": "強気シナリオの説明",
      "portfolio_action": "このシナリオでの配分方針"}},
    {{"name": "ベア", "probability": 25,
      "description": "弱気シナリオの説明",
      "portfolio_action": "このシナリオでの配分方針（キャッシュ増・防御株等）"}}
  ],
  "messages": [
    {{"agent": "MacroAI", "time": "09:00", "content": "発言（日本語）", "type": "opening"}},
    {{"agent": "SorosAI", "time": "09:03", "content": "発言", "type": "analysis"}},
    ...（18〜25メッセージ。全7エージェントが複数回発言すること）
  ]
}}

typeの種類: opening, analysis, debate, proposal, rebuttal, decision, risk_check, scenario, closing
メッセージは18〜25件。10フェーズのアジェンダに沿って進めること。
RiskAIは主要提案に対して必ず反証を出すこと（省略禁止）。
QuantAIは具体的なPER・PBR等の数値を使うこと。
MacroAIは金利・為替の具体的な水準を引用すること。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4500,
        system=_MEETING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = message.content[0].text
    m = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not m:
        raise ValueError("JSONが見つからない")
    ai_data = json.loads(m.group())

    return {
        "date": date,
        "participants": ["soros", "buffett", "lynch", "flat", "macro", "quant", "risk"],
        "summary": ai_data.get("summary", "AI投資委員会が会議を行いました"),
        "market_theme": market_theme,
        "key_decisions": ai_data.get("key_decisions", []),
        "scenarios": ai_data.get("scenarios", []),
        "messages": ai_data.get("messages", []),
    }


# ─── ルールベース フォールバック ─────────────────────────────────────────────────

def _generate_fallback(
    date: str,
    market_data: Dict,
    agent_analyses: Dict,
    trade_proposals: Dict,
) -> Dict:
    """ルールベースでミーティングログを生成（APIキーなし・エラー時）"""
    market_theme = market_data.get("market_theme", "本日の市場動向")
    sp500_change = market_data.get("sp500_change_pct", 0)
    usd_jpy = market_data.get("usd_jpy", 150.0)

    messages = []
    minutes = 0

    def fmt_t(m: int) -> str:
        return f"{9 + m // 60:02d}:{m % 60:02d}"

    def add(agent_id: str, content: str, typ: str):
        nonlocal minutes
        agent = get_agent(agent_id)
        name = agent.name if agent else agent_id
        messages.append({"agent": name, "time": fmt_t(minutes), "content": content, "type": typ})
        minutes += random.randint(2, 5)

    # フェーズ1: MacroAI が市場データを確認
    add("macro",
        f"本日の市場データを確認します。S&P500は{sp500_change:+.2f}%、"
        f"ドル円は{usd_jpy:.1f}円水準で推移しています。"
        "米金利についてはFedWatchの動向を注視する必要があります。"
        "断定は避けますが、金利高止まりリスクが市場で意識されている状況です。",
        "opening")

    # フェーズ2: SorosAI が前回判断を振り返る
    add("soros",
        f"前回の決定を振り返ります。市場テーマ「{market_theme}」は引き続き有効です。"
        "再帰性理論から見ると、市場参加者のセンチメントが現実を変えつつある局面です。",
        "analysis")

    # フェーズ3: QuantAI が銘柄スクリーニング
    add("quant",
        "定量スクリーニングの結果を報告します。"
        "上昇銘柄の多くはPERが過去5年平均の1.2〜1.4倍水準に達しており、"
        "好材料がすでにかなり織り込まれている可能性があります。"
        "モメンタムは強いですが、RSI70超の銘柄は追加買いに慎重を要します。",
        "analysis")

    # フェーズ4: 各ファンドエージェントが投資提案
    for agent_id in ["buffett", "lynch", "soros", "flat"]:
        proposals = trade_proposals.get(agent_id, [])
        analysis = agent_analyses.get(agent_id, {})
        summary = analysis.get("summary", "")
        agent = get_agent(agent_id)

        if proposals:
            p = proposals[0]
            ticker = p.get("ticker", "SPY")
            action_ja = {"buy": "買い", "sell": "売り", "hold": "保有継続"}.get(
                p.get("action", "hold"), "保有継続"
            )
            reason = p.get("reason", "分析に基づく判断")
            add(agent_id,
                f"{ticker}の{action_ja}を提案します。理由：{reason}"
                f" {summary[:60] if summary else ''}",
                "proposal")
        elif summary:
            add(agent_id, summary[:150], "debate")

    # フェーズ5: RiskAI が反証
    add("risk",
        "全ての提案に反証します。"
        "① 為替リスク：円安が反転した場合、輸出株の評価益は消える。"
        "② 金利リスク：米長期金利が上昇すれば、グロース株のバリュエーションは圧迫される。"
        "③ 織り込みリスク：好材料はすでに株価に反映されており、"
        "追加的なアップサイドには業績の上振れが必要。"
        "各提案の撤退条件を明文化してから執行すること。",
        "risk_check")

    # フェーズ6: QuantAI が織り込み度の確認
    add("quant",
        "織り込み度の評価：提案銘柄群は過去3ヶ月で平均15〜25%上昇しており、"
        "好材料の多くは織り込み済みの可能性が高い。"
        "新規ポジションは一括ではなく、3分割・時間分散を推奨します。",
        "analysis")

    # フェーズ7: SorosAI が3シナリオを提示
    add("soros",
        f"3シナリオを提示します。"
        f"【ベース50%】{market_theme}が継続。金利高止まり・円安維持で輸出株に追い風。"
        "【ブル25%】インフレ沈静化・利下げ観測復活でグロース株急騰。"
        "【ベア25%】米景気後退・円高反転で全面調整。キャッシュ比率15%以上を推奨。",
        "scenario")

    # フェーズ8: 執行ルールの確認
    add("lynch",
        "執行ルールを確認します。今日の決定は一括買いではなく、"
        "3分割・状況確認しながら。第1弾は本日少量打診、"
        "第2弾・第3弾は決算確認後または押し目で。",
        "decision")

    # フェーズ9: RiskAI が撤退条件を明文化
    add("risk",
        "撤退条件を明文化します。"
        "① ドル円が5円以上円高方向に動いた場合。"
        "② 対象銘柄の決算が市場期待を10%以上下回った場合。"
        "③ 米10年金利が急上昇し、グロース株全体が-10%を超えた場合。"
        "これらが発生した際は感情なく仮説を再評価する。",
        "risk_check")

    # フェーズ10: SorosAI が次回監視項目を確認
    add("soros",
        "次回まで監視すべき項目：FOMC議事録・CPI・日銀会合・"
        "主要企業決算・ドル円の動向。以上をもって本日の会議を終了します。",
        "closing")

    # key_decisions を作成
    key_decisions = []
    for agent_id in ["soros", "lynch", "buffett"]:
        props = trade_proposals.get(agent_id, [])
        if props:
            p = props[0]
            ticker = p.get("ticker", "")
            action_ja = {"buy": "買い", "sell": "売り", "hold": "保有継続"}.get(
                p.get("action", "hold"), "保有継続"
            )
            key_decisions.append(
                f"【{action_ja}提案】{ticker} - {p.get('reason', '')[:50]}"
                " 執行：3分割。仮説崩壊時は速やかに撤退。"
            )
    if not key_decisions:
        key_decisions = [
            "【現状維持】全ポジション保有継続。追加買いは条件付き。",
            "【執行ルール】新規参入は3分割・時間分散を徹底する。",
            "【リスク管理】キャッシュ比率10%以上を維持する。",
        ]

    # ベーシックなシナリオ
    scenarios = [
        {
            "name": "ベース",
            "probability": 50,
            "description": f"{market_theme}継続。金利高止まり・現在の為替水準が維持される。",
            "portfolio_action": "輸出関連を限定的に増加。テクノロジーは現状維持。キャッシュ10%維持。",
        },
        {
            "name": "ブル",
            "probability": 25,
            "description": "インフレ沈静化・利下げ期待復活。リスクオン環境が到来。",
            "portfolio_action": "グロース・テクノロジー比率を引き上げ。債券ETFを一部売却。",
        },
        {
            "name": "ベア",
            "probability": 25,
            "description": "景気後退シグナル・円高反転・株式全面調整。",
            "portfolio_action": "キャッシュ比率を20%以上に引き上げ。ディフェンシブ株・金に移行。",
        },
    ]

    sentiment = (
        "強気環境への対応" if sp500_change > 0.5
        else "弱気環境への対応" if sp500_change < -0.5
        else "不確実な市場環境での判断"
    )
    summary = (
        f"{market_theme}をテーマに7名のAI投資委員会が会議。"
        f"{sentiment}について議論し、3シナリオ分析と撤退条件を含む決定を行った。"
    )

    return {
        "date": date,
        "participants": ["soros", "buffett", "lynch", "flat", "macro", "quant", "risk"],
        "summary": summary,
        "market_theme": market_theme,
        "key_decisions": key_decisions,
        "scenarios": scenarios,
        "messages": messages,
    }
