"""Shared Pydantic schemas for FastAPI backend."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel


AgentId = Literal["buffett", "soros", "lynch", "flat"]
ActionType = Literal["BUY", "SELL", "HOLD"]
ConvictionLevel = Literal["HIGH", "MEDIUM", "LOW"]
MessageType = Literal["opening", "debate", "proposal", "rebuttal", "decision"]


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
