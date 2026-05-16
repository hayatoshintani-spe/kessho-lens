"""Shared Pydantic schemas for FastAPI backend."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel


AgentId = Literal["buffett", "soros", "lynch", "flat"]
ActionType = Literal["BUY", "SELL", "HOLD"]
ConvictionLevel = Literal["HIGH", "MEDIUM", "LOW"]
MessageType = Literal["opening", "debate", "proposal", "rebuttal", "decision"]

# Tsuburaya Intelligence Brief
IntelCategory = Literal[
    "ip_content",
    "ai_agent",
    "device_telecom",
    "global_region",
    "retail_md_license",
    "regulation_ip_law",
    "competitor_capital",
]
Importance = Literal["A", "B", "C", "D"]
BriefType = Literal["daily", "weekly", "monthly"]
ExpertId = Literal[
    "ip_strategist",
    "global_expansion",
    "md_licensing",
    "ai_trend",
    "cfo",
    "risk_manager",
]


class Holding(BaseModel):
    symbol: str
    name: str
    shares: int
    avgCost: float
    currentPrice: float
    sector: str
    unrealizedPnl: Optional[float] = None
    unrealizedPnlPct: Optional[float] = None


class Portfolio(BaseModel):
    agentId: AgentId
    cash: float
    totalValue: float
    holdings: list[Holding]


class AgentSummary(BaseModel):
    id: AgentId
    name: str
    nameJa: str
    color: str
    totalValue: float
    totalReturn: float
    dailyReturn: float
    rank: int
    latestDecision: str


class AgentDetail(AgentSummary):
    personality: str
    style: str
    favoriteSectors: list[str]
    portfolio: Portfolio
    recentTrades: list["Trade"] = []
    memories: list["Memory"] = []


class MeetingMessage(BaseModel):
    agent: str
    time: str
    content: str
    type: MessageType


class MeetingLog(BaseModel):
    date: str
    participants: list[str]
    summary: str
    keyDecisions: list[str]
    marketTheme: str
    messages: list[MeetingMessage]


class DailyReport(BaseModel):
    date: str
    title: str
    marketTheme: str
    content: str
    agentSummaries: dict[AgentId, str]


class Trade(BaseModel):
    id: str
    date: str
    agentId: AgentId
    action: ActionType
    symbol: str
    name: str
    shares: int
    price: float
    reason: str
    meetingDecision: bool


class Discovery(BaseModel):
    symbol: str
    name: str
    reason: str
    conviction: ConvictionLevel
    action: str


class DiscoveryLog(BaseModel):
    date: str
    agentId: AgentId
    discoveries: list[Discovery]


class Memory(BaseModel):
    date: str
    type: Literal["lesson", "conviction", "discovery", "validation"]
    content: str
    ticker: Optional[str] = None


class ChartDataPoint(BaseModel):
    date: str
    buffett: float
    soros: float
    lynch: float
    flat: float


class DashboardData(BaseModel):
    agents: list[AgentSummary]
    chartData: list[ChartDataPoint]
    latestMeeting: Optional[MeetingLog] = None
    latestReport: Optional[DailyReport] = None
    lastUpdated: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str


class RunDailyResponse(BaseModel):
    success: bool
    date: str
    message: str
    meetingGenerated: bool
    reportGenerated: bool
    tradesExecuted: int


# ─── Tsuburaya Intelligence Brief ───────────────────────────────────────────

class IntelSource(BaseModel):
    """記事の出典情報"""
    title: str
    url: Optional[str] = None
    publisher: Optional[str] = None
    published_at: Optional[str] = None
    access_status: Literal["full", "title_only", "paywalled", "estimated"] = "full"


class IntelInsight(BaseModel):
    """円谷への示唆セクション"""
    what_it_means: str  # 円谷にとって何を意味するのか
    business_opportunity: list[str] = []
    risk: list[str] = []


class IntelAction(BaseModel):
    """次アクション"""
    who: str  # 誰が動くべきか（部署・会議体）
    what: str  # 具体的に何をするか
    deadline: Optional[str] = None
    priority: Literal["urgent", "this_week", "this_month", "watch"] = "this_week"


class IntelCard(BaseModel):
    """記事カード — Notion DB 登録単位"""
    id: str
    date: str  # YYYY-MM-DD
    title: str  # 日本語タイトル
    one_liner: str  # 30字程度の要約
    category: IntelCategory
    importance: Importance
    fact: str  # 事実（出典あり）
    interpretation: str  # 解釈（推測は推測と明記）
    insight: IntelInsight
    actions: list[IntelAction]
    tags: list[str] = []
    sources: list[IntelSource] = []
    confidence: Literal["high", "medium", "low"] = "medium"
    speculation_notes: Optional[str] = None  # 推測・憶測の注記
    related_card_ids: list[str] = []
    related_agents: list[ExpertId] = []  # 関連する社内エキスパート


class CouncilMessage(BaseModel):
    """AIエージェント会議の発言"""
    expert_id: ExpertId
    expert_name: str
    time: str  # HH:MM
    content: str
    stance: Literal["support", "challenge", "neutral", "concern", "proposal"] = "neutral"


class CouncilSession(BaseModel):
    """重要テーマに対するAIエージェント会議ログ"""
    id: str
    date: str
    topic: str  # 議題
    trigger_card_ids: list[str]  # 引き金となったカード
    summary: str
    messages: list[CouncilMessage]
    editor_conclusion: dict  # {"adopt": [...], "hold": [...], "research": [...]}


class BriefSection(BaseModel):
    """ブリーフの1セクション"""
    heading: str
    body: str  # Markdown


class DailyBrief(BaseModel):
    """Daily Intelligence Brief"""
    date: str
    title: str
    top_topics: list[str]  # 上位5件カードID
    executive_summary: str  # 経営層向け要約
    business_opportunities: list[str]
    risks: list[str]
    next_actions: list[IntelAction]
    sections: list[BriefSection] = []
    council_session_id: Optional[str] = None


class WeeklyBrief(BaseModel):
    """Weekly Executive Brief"""
    week_of: str  # 月曜日のYYYY-MM-DD
    title: str
    key_changes: list[str]
    opportunities: list[str]
    risks: list[str]
    decisions_pending: list[str]
    actions_by_department: dict[str, list[str]]  # 部署別アクション
    watch_themes_next_week: list[str]


class WatchlistItem(BaseModel):
    """カテゴリ別ウォッチリスト項目"""
    keyword: str
    category: IntelCategory
    rationale: str  # なぜ追うか
    priority: Literal["high", "medium", "low"] = "medium"


class CategoryWatchlist(BaseModel):
    category: IntelCategory
    label: str
    description: str
    targets: list[str]  # 対象企業・キーワード
    items: list[WatchlistItem]
