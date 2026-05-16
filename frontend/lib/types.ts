// ─── Agent ────────────────────────────────────────────────────────────────────

// ファンドメンバー（ポートフォリオ・取引に参加する4エージェント）
export type FundAgentId = 'buffett' | 'soros' | 'lynch' | 'flat';

// 会議参加者（専門分析AI3名を含む7エージェント）
export type AgentId = FundAgentId | 'macro' | 'quant' | 'risk';

export interface Portfolio {
  totalValue: number;
  cash: number;
  holdings: Holding[];
}

export interface Holding {
  ticker: string;
  name: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPct: number;
  weight: number; // portfolio weight %
}

export interface Agent {
  id: AgentId;
  name: string;        // e.g. "BuffettAI"
  nameJa: string;      // e.g. "バフェットAI"
  personality: string; // Japanese description
  style: string;       // investment style label
  color: string;       // hex color
  portfolio: Portfolio;
  totalReturn: number;     // percentage
  totalReturnAbs: number;  // absolute JPY/USD
  rank: number;
  beliefs: string[];       // key investment principles
  recentDecision?: string;
}

// ─── Meeting / Discussion ──────────────────────────────────────────────────────

export type MessageType =
  | 'opening'
  | 'debate'
  | 'proposal'
  | 'rebuttal'
  | 'decision'
  | 'analysis'
  | 'closing'
  | 'risk_check'   // RiskAI の反証・撤退条件
  | 'scenario';    // シナリオ分析

export interface MeetingMessage {
  agent: string; // AgentId または未知のエージェント名
  time: string;  // "HH:MM:SS"
  content: string;
  type: MessageType;
}

export interface MeetingScenario {
  name: 'ベース' | 'ブル' | 'ベア' | string;
  probability: number; // 0-100
  description: string;
  portfolio_action: string;
}

export interface MeetingLog {
  date: string; // "YYYY-MM-DD"
  participants: AgentId[];
  summary: string;
  keyDecisions: string[];
  marketTheme: string;
  messages: MeetingMessage[];
  scenarios?: MeetingScenario[];
  duration?: string; // "45分"
}

// ─── Report ───────────────────────────────────────────────────────────────────

export interface AgentSummary {
  agentId: AgentId;
  summary: string;
  decisions: string[];
  pnlChange: number;
}

export interface DailyReport {
  date: string; // "YYYY-MM-DD"
  title: string;
  content: string; // full markdown report
  agentSummaries: Partial<Record<AgentId, AgentSummary>>;
  totalFundReturn: number;
  marketTheme: string;
}

// ─── Discovery ────────────────────────────────────────────────────────────────

export type DiscoveryStatus = 'scanning' | 'found' | 'rejected' | 'watchlist';

export interface DiscoveryEntry {
  id: string;
  date: string;
  ticker: string;
  name: string;
  nameJa?: string;
  agentId: AgentId;
  reason: string;
  score: number; // 0-100
  status: DiscoveryStatus;
  sector?: string;
  priceAtDiscovery?: number;
}

// ─── Performance / Chart ──────────────────────────────────────────────────────

export interface PerformanceDataPoint {
  date: string; // "YYYY-MM-DD"
  buffett: number;
  soros: number;
  lynch: number;
  flat: number;
  benchmark?: number; // e.g. Nikkei
}

export interface FundStats {
  totalAum: number;
  inception: string; // "YYYY-MM-DD"
  totalReturn: number;
  bestAgent: AgentId;
  worstAgent: AgentId;
  lastUpdated: string; // ISO timestamp
}

// ─── API response wrappers ────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// ─── Settings ─────────────────────────────────────────────────────────────────

export type MarketTarget = 'japan' | 'us' | 'both';

export interface AppSettings {
  apiBaseUrl: string;
  anthropicApiKey: string;
  marketTarget: MarketTarget;
  autoRunEnabled: boolean;
  autoRunTime: string; // "HH:MM"
}
