"""
エージェントエンドポイント
AIエージェントの情報とポートフォリオを返す
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict

from src.agents import ALL_AGENTS, get_agent
from src.data.storage import Storage
from src.data.mock_data import INITIAL_PORTFOLIOS

router = APIRouter()

# エージェントの詳細メタ情報
_AGENT_DETAILS = {
    "buffett": {
        "display_name": "BuffettAI（バフェット）",
        "full_name": "Warren Buffett AI",
        "avatar": "🏦",
        "color": "#1d6a96",
        "style_tags": ["バリュー投資", "長期保有", "配当重視", "堀（モート）"],
        "bio_ja": (
            "オマハの賢人を模したAIエージェント。長期的な企業価値に基づいた投資を行う。"
            "配当成長株、競争優位性（堀）のある企業を好み、派手なテクノロジー株は嫌う。"
            "「20年持てない株は20分も持つな」というフィロソフィーで、"
            "短期的な市場の騒音には一切動じない。"
            "コカコーラ、JNJ、バークシャーを中核保有。"
        ),
        "famous_quotes": [
            "20年持てる株か？",
            "素晴らしい会社を公正な価格で買う",
            "市場は短期的には投票機、長期的には体重計だ",
            "リスクとは、自分が何をしているか分からないことから来る",
        ],
        "investment_approach": {
            "time_horizon": "10〜20年以上",
            "risk_tolerance": "低（安全余裕率重視）",
            "valuation_method": "ディスカウントキャッシュフロー / PBR / 配当利回り",
            "preferred_metrics": ["P/E（割安）", "配当利回り", "ROE", "フリーキャッシュフロー"],
        },
        "weaknesses": [
            "テクノロジー株の初期段階を見逃すことがある",
            "マクロ変動に対して受動的",
            "成長よりも安定を優先するため、急成長株を避ける",
        ],
    },
    "soros": {
        "display_name": "SorosAI（ソロス）",
        "full_name": "George Soros AI",
        "avatar": "🌍",
        "color": "#8b5e3c",
        "style_tags": ["グローバルマクロ", "再帰性理論", "為替", "コモディティ"],
        "bio_ja": (
            "伝説的なマクロ投資家を模したAIエージェント。再帰性理論を軸に、"
            "政策・為替・市場の相互作用から投資機会を発見する。"
            "「市場は常に間違っている」という信念のもと、"
            "市場の誤りを先取りした大胆なポジションを取る。"
            "利益が乗れば素早く利確、状況が変わればすぐにポジションを転換する柔軟さも持つ。"
        ),
        "famous_quotes": [
            "市場は常に間違っている",
            "認識が現実を変える、それが再帰性だ",
            "自分の仮説が間違っていると証明されれば、すぐに変える",
            "私が正しいか間違っているかより、間違えた時にどれだけ失うかが重要だ",
        ],
        "investment_approach": {
            "time_horizon": "数週間〜数ヶ月（マクロトレンドに依存）",
            "risk_tolerance": "高（大胆なポジション、リスク管理も厳格）",
            "valuation_method": "再帰性モデル / マクロファンダメンタルズ",
            "preferred_metrics": ["通貨フロー", "政策金利", "資本移動", "市場センチメント"],
        },
        "weaknesses": [
            "短期的なボラティリティが高い",
            "個別企業の質より市場全体の方向性を重視",
            "ポジション転換が頻繁でコストがかかる",
        ],
    },
    "lynch": {
        "display_name": "LynchAI（リンチ）",
        "full_name": "Peter Lynch AI",
        "avatar": "🔍",
        "color": "#2d8a4e",
        "style_tags": ["成長株", "テンバガー", "PEGレシオ", "日常観察"],
        "bio_ja": (
            "マゼランファンドの伝説的マネージャーを模したAIエージェント。"
            "日常生活での観察から投資アイデアを発掘する。"
            "PEGレシオ（株価収益率÷成長率）を重視し、成長と価格のバランスが取れた銘柄を探す。"
            "「スーパーマーケットで株を発見する」スタイルで、"
            "一般消費者が使い始めた製品・サービスに着目。テンバガー（10倍株）を狙う。"
        ),
        "famous_quotes": [
            "自分が理解できる株を買え",
            "テンバガーの匂いがする",
            "スーパーマーケットで株を発見する",
            "企業のストーリーが分かれば、数字は後からついてくる",
        ],
        "investment_approach": {
            "time_horizon": "3〜5年（成長ストーリーが続く限り）",
            "risk_tolerance": "中〜高（分散投資でリスク管理）",
            "valuation_method": "PEGレシオ / 成長率 / ストーリー投資",
            "preferred_metrics": ["PEG（1以下が理想）", "売上成長率", "利益率改善", "顧客満足度"],
        },
        "weaknesses": [
            "確証バイアスに陥りやすい（好きな企業を擁護）",
            "マクロリスクを過小評価することがある",
            "日常観察が常に正確とは限らない（アンカリングバイアス）",
        ],
    },
    "flat": {
        "display_name": "FlatAI（フラット）",
        "full_name": "Index Investor AI",
        "avatar": "📊",
        "color": "#6b6b6b",
        "style_tags": ["インデックス投資", "効率的市場仮説", "低コスト", "パッシブ"],
        "bio_ja": (
            "効率的市場仮説（EMH）の忠実な信奉者。ジョン・ボーグルのパッシブ投資哲学を体現するAIエージェント。"
            "「アクティブ運用は長期的に全員負ける」という統計的事実を武器に、"
            "他の3人の銘柄選択を容赦なく批判する。"
            "感情を完全に排除した合理的な意思決定を行い、"
            "コスト最小化と定期リバランスだけを実践する。"
        ),
        "famous_quotes": [
            "アクティブ運用は全員負ける",
            "データを見てください",
            "これはアンカリングバイアスです",
            "過去20年でS&P500に勝ったアクティブファンドは15%未満",
        ],
        "investment_approach": {
            "time_horizon": "長期（市場全体の成長に乗る）",
            "risk_tolerance": "低〜中（分散によりリスク最小化）",
            "valuation_method": "インデックスパフォーマンス / コスト比較",
            "preferred_metrics": ["経費率（低いほど良い）", "トラッキングエラー", "流動性"],
        },
        "weaknesses": [
            "市場全体が下落する際には防御ができない",
            "超過リターンを求める投資家には退屈",
            "個別の優良企業への集中投資機会を逃す",
        ],
    },
}


@router.get("/agents")
async def list_agents():
    """全エージェントの一覧と概要を返す"""
    agents_list = []

    for agent_id, details in _AGENT_DETAILS.items():
        agent = get_agent(agent_id)
        portfolio = Storage.get_portfolio(agent_id) or INITIAL_PORTFOLIOS.get(agent_id, {})
        perf = portfolio.get("performance", {})

        agents_list.append({
            "id": agent_id,
            "display_name": details["display_name"],
            "full_name": details["full_name"],
            "avatar": details["avatar"],
            "color": details["color"],
            "style_tags": details["style_tags"],
            "bio_short": details["bio_ja"][:100] + "...",
            "catchphrase": agent.catchphrase if agent else details["style_tags"][0] if details["style_tags"] else "",
            "style": agent.style if agent else details["style_tags"][0] if details["style_tags"] else "",
            "favorite_sectors": agent.favorite_sectors if agent else [],
            "performance": {
                "total_return_pct": perf.get("total_return_pct", 0),
                "daily_pnl": perf.get("daily_pnl", 0),
            },
        })

    return {
        "agents": agents_list,
        "count": len(agents_list),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/agents/{agent_id}")
async def get_agent_detail(agent_id: str):
    """特定エージェントの詳細情報を返す"""
    agent_id = agent_id.lower()

    if agent_id not in _AGENT_DETAILS:
        raise HTTPException(
            status_code=404,
            detail=f"エージェント '{agent_id}' が見つかりません。有効なID: buffett, soros, lynch, flat",
        )

    agent = get_agent(agent_id)
    details = _AGENT_DETAILS[agent_id]

    # ポートフォリオ取得
    portfolio = Storage.get_portfolio(agent_id) or INITIAL_PORTFOLIOS.get(agent_id, {})

    # 直近の取引履歴
    recent_trades = Storage.get_trades(agent_id=agent_id, limit=10)

    # 直近のミーティングでの発言
    recent_meetings = Storage.get_meetings(limit=5)
    agent_messages = []
    agent_name = agent.name if agent else details["display_name"]
    for meeting in recent_meetings:
        for msg in meeting.get("messages", []):
            if msg.get("agent") == agent_name:
                agent_messages.append({
                    "date": meeting.get("date"),
                    "time": msg.get("time"),
                    "content": msg.get("content"),
                    "type": msg.get("type"),
                })
        if len(agent_messages) >= 6:
            break

    return {
        "id": agent_id,
        "display_name": details["display_name"],
        "full_name": details["full_name"],
        "avatar": details["avatar"],
        "color": details["color"],
        "style_tags": details["style_tags"],
        "bio_ja": details["bio_ja"],
        "catchphrase": agent.catchphrase if agent else details["style_tags"][0] if details["style_tags"] else "",
        "style": agent.style if agent else details["style_tags"][0] if details["style_tags"] else "",
        "favorite_sectors": agent.favorite_sectors if agent else [],
        "famous_quotes": details["famous_quotes"],
        "investment_approach": details["investment_approach"],
        "weaknesses": details["weaknesses"],
        "portfolio": {
            "total_value": portfolio.get("total_value", 0),
            "cash": portfolio.get("cash", 0),
            "holdings": portfolio.get("holdings", []),
            "performance": portfolio.get("performance", {}),
        },
        "recent_trades": recent_trades,
        "recent_messages": agent_messages,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
