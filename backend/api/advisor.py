"""個人資産アドバイザーAPI — 4AIが実資産の運用方針を議論する"""
from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
import re

router = APIRouter()


class AdvisorRequest(BaseModel):
    amount: int   # 万円単位
    period: str   # "short" | "medium" | "long"
    risk: str     # "low" | "medium" | "high"


PERIOD_LABELS = {
    "short": "1〜3年（短期）",
    "medium": "5〜10年（中期）",
    "long": "10年以上（長期）",
}
RISK_LABELS = {
    "low": "低リスク（元本重視）",
    "medium": "中リスク（バランス型）",
    "high": "高リスク（積極運用）",
}


def _m(agent: str, time: str, content: str, typ: str) -> dict:
    return {"agent": agent, "time": time, "content": content, "type": typ}


# ─── ルールベース議論 ────────────────────────────────────────────────────────────

def _low_risk(a: str, period: str) -> dict:
    msgs = [
        _m("soros", "09:00:00",
           f"本日は{a}を{PERIOD_LABELS[period]}・{RISK_LABELS['low']}で運用する最適戦略を議論します。"
           "元本を守りながら実質的なリターンを得るには何が最善か、各エージェントの見解を聞かせてください。",
           "opening"),
        _m("buffett", "09:01:30",
           f"低リスク運用の王道は、本質的価値が安定した高配当企業への長期投資です。"
           "三菱商事・KDDI・NTTのような連続増配株に{a}の30%を振り向け、"
           "残りをeMAXIS Slim S&P500で補完する。配当を再投資し続けることで複利の力が働きます。".format(a=a),
           "analysis"),
        _m("soros", "09:03:15",
           f"バフェットAIの選択は安定しているが、円安リスクを見落としています。"
           f"{a}の30%は米国債ETFやドルMMFでドル建て資産を確保すべきです。"
           "円が構造的に弱い今、ドル資産保有が最も簡単な守りになります。",
           "proposal"),
        _m("lynch", "09:05:00",
           f"低リスクといっても、インフレ率（現在2〜3%）を上回る必要があります。"
           "国内のインバウンド関連・防衛関連の安定成長株を一部加えることで、"
           "インフレに負けないリターンが確保できます。大型株ならリスクは限定的です。",
           "debate"),
        _m("flat", "09:06:45",
           "皆さん個別株の選択リスクを軽視しています。低リスクこそインデックスが最適です。"
           "eMAXIS Slim全世界株式（オルカン）とSBI・V・米国債券インデックスファンドを"
           "組み合わせるだけで、個別株選択リスクをゼロにしながら市場平均リターンが得られます。",
           "rebuttal"),
        _m("lynch", "09:08:20",
           f"重要な点を忘れていました。{a}ならNISA枠（年間360万円）で全額非課税運用が可能です。"
           "まずNISA口座を最大活用することが税コスト削減の第一歩。"
           "インデックスか個別株かより、NISAか否かの方が長期リターンへの影響が大きい。",
           "analysis"),
        _m("buffett", "09:10:00",
           "フラットAIの意見は合理的です。ただしオルカン一本では優良高配当株が持つ"
           "「定期的な現金収入」が得られない。配当収入は下落局面でも保有を続けられる"
           "心理的な安定感を与えます。",
           "debate"),
        _m("soros", "09:11:45",
           f"議論を踏まえた最終配分：オルカン（eMAXIS Slim全世界株式）40%、"
           "ドル建て資産（米国債ETF・ドルMMF）30%、国内高配当株（三菱商事・KDDI等）20%、"
           "現金（生活防衛資金）10%。全額NISA口座で運用すること。",
           "decision"),
        _m("flat", "09:12:45",
           "インデックス比率が高く、合理的な配分です。"
           "唯一追加するなら：下落時こそ積立を続けること。パニック売りが最大の敵です。",
           "closing"),
    ]
    if period == "short":
        decisions = [
            f"NISA口座でオルカン（eMAXIS Slim全世界株式） {a}の40%",
            f"ドル建て資産（米国債ETF・ドルMMF） {a}の30%",
            f"国内高配当株（三菱商事・KDDI等） {a}の20%",
            f"現金（生活防衛資金） {a}の10%",
        ]
        summary = (f"{a}を短期・元本保全優先で運用。守りを固めながら、"
                   "インフレに負けない最低限のリターンを確保する方針で合意。")
    elif period == "medium":
        decisions = [
            f"NISA口座でオルカン（eMAXIS Slim全世界株式） {a}の50%",
            f"国内高配当株（三菱商事・NTT・KDDI等） {a}の30%",
            f"ドル建て資産（米国債ETF） {a}の20%",
            "全額NISA口座を活用し、配当は再投資",
        ]
        summary = (f"{a}を中期で着実に増やす保守的戦略。高配当株とインデックスの組み合わせで"
                   "年率3〜5%のリターンを目指す方針で合意。")
    else:
        decisions = [
            f"NISA口座でオルカン積立（毎月定額） {a}の50%",
            f"国内高配当株（配当再投資） {a}の30%",
            f"ドル建て資産（為替リスクヘッジ） {a}の20%",
            "10年以上の長期保有で複利効果を最大化",
        ]
        summary = (f"{a}を長期・安定運用。複利効果を最大化しつつリスクを抑えた配分で合意。"
                   "オルカン積立を中心とした長期戦略。")
    return {
        "participants": ["soros", "buffett", "lynch", "flat"],
        "summary": summary,
        "market_theme": f"{a}の安全な資産形成戦略",
        "key_decisions": decisions,
        "messages": msgs,
    }


def _medium_risk(a: str, period: str) -> dict:
    msgs = [
        _m("soros", "09:00:00",
           f"本日は{a}を{PERIOD_LABELS[period]}・{RISK_LABELS['medium']}で運用する最適戦略を議論します。"
           "守りと攻めのバランスを取りながら、市場平均を上回るリターンを目指しましょう。",
           "opening"),
        _m("buffett", "09:01:45",
           f"中リスク運用の核心は、本質的価値に対して割安な優良企業への長期投資です。"
           f"{a}の50〜60%をeMAXIS Slim S&P500またはオルカンに充て、"
           "残り30〜40%を国内の割安優良株（三菱UFJ・ENEOSなど）に。"
           "この組み合わせが最も安定した複利成長をもたらします。",
           "analysis"),
        _m("lynch", "09:03:20",
           f"成長の観点から見ると、{a}の20%を日本の高成長中小型株に充てることを提案します。"
           "SHIFT・サイボウズ・ラクス等のDX推進企業は、今後5〜10年で大きく成長する可能性があります。"
           "身近なサービスで成長しているビジネスを見つけるのが私の手法です。",
           "proposal"),
        _m("soros", "09:05:00",
           "マクロ視点では、現在のAI・半導体サイクルの恩恵を受けるため"
           "QQQ（ナスダック100 ETF）への投資が有効です。"
           f"{a}の20〜30%を米国テックセクターに集中させることで、"
           "インデックス以上のリターンが期待できます。",
           "debate"),
        _m("flat", "09:06:40",
           "過去20年間でS&P500インデックスをアウトパフォームしたアクティブファンドは15%未満です。"
           f"{a}の80〜90%はオルカン積立に充て、残り10〜20%だけ個別株に挑戦するのが"
           "最も合理的な配分です。",
           "rebuttal"),
        _m("buffett", "09:08:15",
           "フラットAIの統計は正しい。しかし全員が平均を目指せば全員が平均で終わる。"
           "私は5〜10社の理解できる優良企業に集中することで、"
           "長期的に市場平均を上回ることができると確信しています。",
           "debate"),
        _m("lynch", "09:09:50",
           "NISAの活用を忘れてはなりません。"
           "つみたて投資枠（年間120万円）でオルカン積立、成長投資枠（年間240万円）で個別株購入が"
           f"黄金パターンです。{a}があれば複数年かけてNISA枠を最大活用できます。",
           "analysis"),
        _m("soros", "09:11:30",
           "議論を踏まえた最終配分：eMAXIS Slim全世界株式（オルカン）60%、"
           "国内優良株・高配当株20%、米国成長株（QQQ含む）20%。"
           "NISA口座を最大活用し、定期的にリバランスを実施すること。",
           "decision"),
        _m("flat", "09:12:45",
           "インデックス比率を高く維持した点は評価します。"
           "積立投資の習慣化が、最終的な資産形成の最大の要因になります。"
           "感情に左右されず、機械的に継続することが重要です。",
           "closing"),
    ]
    if period == "short":
        decisions = [
            f"NISA口座でオルカン積立 {a}の50%",
            f"国内高配当株（三菱UFJ・KDDI等） {a}の25%",
            f"米国成長株・QQQ {a}の15%",
            f"現金（機動的運用） {a}の10%",
        ]
        summary = (f"{a}を短期・バランス運用。インデックスを軸に高配当株と成長株を組み合わせた"
                   "安定成長戦略で合意。")
    elif period == "medium":
        decisions = [
            f"NISA口座でオルカン（eMAXIS Slim全世界株式） {a}の60%",
            f"国内優良株・高配当株 {a}の20%",
            f"米国成長株（QQQ・個別株） {a}の20%",
            "半年ごとにリバランスを実施",
        ]
        summary = (f"{a}の最適バランス運用。オルカンを中心に国内優良株・米国成長株を組み合わせ、"
                   "NISAを活用した中期成長戦略で合意。")
    else:
        decisions = [
            f"NISA口座でオルカン（長期積立） {a}の60%",
            f"国内成長株・優良株 {a}の20%",
            f"米国成長株（QQQ） {a}の20%",
            "10年以上保有し、下落時も継続積立で複利を最大化",
        ]
        summary = (f"{a}を長期バランス運用。時間を味方につけたオルカン積立を主軸に、"
                   "成長株でアルファを狙う複合戦略で合意。")
    return {
        "participants": ["soros", "buffett", "lynch", "flat"],
        "summary": summary,
        "market_theme": f"{a}のバランス成長戦略",
        "key_decisions": decisions,
        "messages": msgs,
    }


def _high_risk(a: str, period: str) -> dict:
    msgs = [
        _m("soros", "09:00:00",
           f"積極運用ですね。{a}を{PERIOD_LABELS[period]}で最大化する。"
           "リスクを恐れず、反射性理論に基づいて市場のトレンドを掴む戦略を議論しましょう。",
           "opening"),
        _m("lynch", "09:01:30",
           f"高リスク許容度があるなら、まず日本の小型成長株に注目すべきです。"
           "SHIFT・マネーフォワード・カプコン等、成長ストーリーが明確な銘柄に"
           f"{a}の30〜40%を集中投資します。"
           "業績成長率が市場予想を大幅に上回る銘柄群です。",
           "analysis"),
        _m("soros", "09:03:00",
           "マクロ観点では、現在の相場環境で最大のアルファ源はAI・半導体セクターです。"
           "NVIDIA・TSMC・東京エレクトロンへの集中投資、"
           f"またはSOXL（半導体3倍レバレッジETF）で{a}の10〜15%を攻める戦略を提案します。"
           "ただしレバレッジは総資産の15%以内に限定すること。",
           "proposal"),
        _m("buffett", "09:04:45",
           f"高リスクと無謀は違います。{a}を賭けるなら、私は5社に絞って徹底的に調査します。"
           "理解できないビジネスには絶対に投資しない。"
           "AI・半導体のインフラを提供するTSMCやAppleのようなエコシステムを持つ企業が、"
           "長期的な勝者になる確率が高い。",
           "debate"),
        _m("flat", "09:06:20",
           "積極運用でも、インデックスが基本です。"
           f"S&P500を長期保有した場合のリターンが個別株アクティブ運用の85%を上回ります。"
           f"{a}の50〜60%はQQQのような成長インデックスに充て、残りで個別株に挑戦することを推奨。",
           "rebuttal"),
        _m("soros", "09:08:00",
           "フラットAIは今日珍しく正しいことを言っている。"
           "ただしQQQはS&P500より集中度が高く、高リスク許容者には最適な選択です。"
           "QQQ + 個別株 + 少量のレバレッジETFという組み合わせが私の推奨です。",
           "analysis"),
        _m("lynch", "09:09:30",
           "国内では見落とされている宝が多い。"
           "時価総額500億円以下の小型株で業績成長率30%超の企業が複数存在します。"
           "大手証券のアナリストカバレッジが薄い点も優位性になります。",
           "debate"),
        _m("buffett", "09:11:00",
           "最終的に重要なのは、何に投資するかより、パニック時に売らない精神力があるか否かです。"
           f"高リスク配分を選ぶなら、{a}が半分になっても保有を続けられる確信が必要です。"
           "その覚悟がある方だけが高リターンを手にできます。",
           "proposal"),
        _m("soros", "09:12:45",
           "最終配分：米国成長株・QQQ（ナスダック100ETF）50%、"
           "日本小型成長株（SHIFT・マネーフォワード等）30%、"
           "新興国・AI・半導体テーマETF 20%。"
           "半年ごとにポートフォリオを見直し、トレンド変化に素早く対応すること。",
           "decision"),
        _m("flat", "09:14:00",
           f"この配分は私の推奨より積極的ですが、{PERIOD_LABELS[period]}保有できるなら"
           "統計的には十分勝算があります。"
           "定期的なリバランスを怠らないこと。感情に任せた追加投資・売却が最大の敵です。",
           "closing"),
    ]
    if period == "short":
        decisions = [
            f"米国成長株・QQQ（ナスダック100ETF） {a}の40%",
            f"日本小型成長株（SHIFT・マネーフォワード等） {a}の30%",
            f"AI・半導体テーマETF {a}の20%",
            f"現金（機動的運用） {a}の10%",
        ]
        summary = (f"{a}を短期・積極運用。米国・日本の成長株を中心に高いリターンを狙うが、"
                   "短期のため機動的な現金ポジションも確保する方針で合意。")
    elif period == "medium":
        decisions = [
            f"米国成長株・QQQ（ナスダック100ETF） {a}の50%",
            f"日本小型成長株（SHIFT・マネーフォワード等） {a}の30%",
            f"新興国・AI・半導体テーマETF {a}の20%",
            "半年ごとにリバランス・銘柄見直しを実施",
        ]
        summary = (f"{a}を中期・積極成長運用。米国・日本の成長株に集中投資し、"
                   "インデックスを上回るリターンを目指す戦略で合意。")
    else:
        decisions = [
            f"米国成長株・QQQ（長期保有） {a}の50%",
            f"日本小型成長株（テンバガー候補） {a}の30%",
            f"新興国・AI・半導体テーマETF {a}の20%",
            "10年以上の長期保有で複利を最大化。下落時も売らない",
        ]
        summary = (f"{a}を長期・最大積極運用。時間を武器に高ボラティリティ資産に集中投資し、"
                   "長期的な資産最大化を目指す戦略で合意。")
    return {
        "participants": ["soros", "buffett", "lynch", "flat"],
        "summary": summary,
        "market_theme": f"{a}の積極的資産最大化戦略",
        "key_decisions": decisions,
        "messages": msgs,
    }


def generate_rule_based_debate(amount: int, period: str, risk: str) -> dict:
    a = f"{amount:,}万円"
    if risk == "low":
        return _low_risk(a, period)
    elif risk == "medium":
        return _medium_risk(a, period)
    else:
        return _high_risk(a, period)


# ─── Claude API議論生成 ──────────────────────────────────────────────────────────

async def generate_claude_debate(amount: int, period: str, risk: str) -> dict | None:
    try:
        import anthropic
        # 25秒タイムアウト: Renderの30秒制限内に確実にフォールバックできるようにする
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            timeout=25.0,
            max_retries=0,
        )
        amount_str = f"{amount:,}万円"

        system = (
            "あなたは4つの異なる投資スタイルを持つAIエージェントが議論するシミュレーターです。\n\n"
            "エージェントの特徴:\n"
            "- BuffettAI: バフェットの価値投資。長期・割安優良株・高配当・複利重視。\n"
            "- SorosAI: ソロスのマクロ投資・反射性理論。大胆なポジション。議論の司会役。\n"
            "- LynchAI: リンチのグロース投資。身近な成長企業発掘・テンバガー志向。銘柄名を具体的に挙げる。\n"
            "- FlatAI: EMH信奉者・インデックス投資。オルカン推奨。アクティブ運用を批判。\n\n"
            "必ず日本語で、各エージェントの個性を忠実に再現してください。"
            "具体的な銘柄名・ETF名（eMAXIS Slim・QQQ・オルカン等）を含めてください。"
        )

        user_msg = (
            f"ユーザーの資産状況:\n"
            f"- 運用資金: {amount_str}\n"
            f"- 投資期間: {PERIOD_LABELS.get(period, period)}\n"
            f"- リスク許容度: {RISK_LABELS.get(risk, risk)}\n\n"
            "この状況で4AIが最適な運用戦略を議論してください。\n"
            "以下のJSON形式のみで返してください（説明文なし）:\n\n"
            "{\n"
            '  "summary": "会議サマリー（2文程度）",\n'
            '  "market_theme": "議論のテーマ（短く）",\n'
            f'  "key_decisions": ["具体的な配分案1（例: オルカン60% = {amount_str}の60%）", "配分案2", "配分案3", "配分案4"],\n'
            '  "participants": ["soros", "buffett", "lynch", "flat"],\n'
            '  "messages": [\n'
            '    {"agent": "soros", "time": "09:00:00", "content": "開会の発言", "type": "opening"}\n'
            "  ]\n"
            "}\n\n"
            "typeはopening/analysis/debate/proposal/rebuttal/decision/closingのいずれか。\n"
            "メッセージ数は8〜12。最後はSorosAIがdecision、FlatAIがclosingで締める。\n"
            "必ずNISA活用を含め、具体的な銘柄名・ETF名を挙げること。"
        )

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )

        content = response.content[0].text.strip()
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            content = m.group()
        return json.loads(content)
    except Exception as e:
        print(f"[advisor] Claude API error: {e}")
        return None


# ─── エンドポイント ──────────────────────────────────────────────────────────────

@router.post("/advisor")
async def get_advisor_debate(req: AdvisorRequest):
    """個人資産の4AI議論を生成する"""
    period = req.period if req.period in PERIOD_LABELS else "medium"
    risk = req.risk if req.risk in RISK_LABELS else "medium"
    amount = max(1, req.amount)

    result = None
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            result = await generate_claude_debate(amount, period, risk)
        except Exception as e:
            print(f"[advisor] unexpected Claude error, falling back: {e}")
            result = None

    if result is None:
        try:
            result = generate_rule_based_debate(amount, period, risk)
        except Exception as e:
            print(f"[advisor] rule-based generation failed: {e}")
            result = {
                "participants": ["soros", "buffett", "lynch", "flat"],
                "summary": "議論の生成に失敗しました。再度お試しください。",
                "market_theme": "エラー",
                "key_decisions": [],
                "messages": [],
            }

    return {"date": "advisor", **result}
