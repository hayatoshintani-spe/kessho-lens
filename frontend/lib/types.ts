// ─── Agent ────────────────────────────────────────────────────────────────────

// ファンドメンバー（ポートフォリオ・取引に参加する4エージェント）
export type FundAgentId = 'buffett' | 'soros' | 'lynch' | 'flat';

// 会議参加者（専門分析AI3名を含む7エージェント）
export type AgentId = FundAgentId | 'macro' | 'quant' | 'risk';

export interface Portfolio {
  totalValue: number;
  cash: number;
  cashRatio?: number;       // 現金比率 %
  equityRatio?: number;     // 株式比率 %
  holdingsValue?: number;   // 株式評価額合計
  holdings: Holding[];
  priceUpdatedAt?: string;  // 株価最終更新時刻 (ISO 8601)
  priceSource?: string;     // データソース (alpaca | finnhub | yfinance | alpha_vantage | mock)
  consistencyWarnings?: ConsistencyWarning[];
}

export interface Holding {
  ticker: string;
  name: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  unrealizedPnL: number;
  unrealizedPnLPct: number;
  weight: number;            // portfolio weight %
  priceUpdatedAt?: string;   // この銘柄の株価が取得された時刻
  priceSource?: string;      // どのAPIから取得したか
  prevPrice?: number;        // 直近の前日比チェック用
}

export type ConsistencyLevel = 'info' | 'warning' | 'error';

export interface ConsistencyWarning {
  level: ConsistencyLevel;
  code: string;
  message: string;
}

// ─── Benchmark comparison ─────────────────────────────────────────────────────

export type BenchmarkName = 'n225' | 'topix' | 'sp500';

export interface BenchmarkSummary {
  agentId: FundAgentId;
  fundReturnPct: number;
  vsN225Pct: number;
  vsTopixPct: number;
  vsSp500Pct: number;
}

export interface BenchmarkComparison {
  days: number;
  fetchedAt: string;
  dates: string[];
  agents: Partial<Record<FundAgentId, number[]>>;       // 累積リターン %
  benchmarks: Partial<Record<BenchmarkName, number[]>>; // 累積リターン %
  benchmarkMeta: Partial<Record<BenchmarkName, { displayName: string; currency: string }>>;
  summary: BenchmarkSummary[];
}

export interface AttributionContribution {
  ticker: string;
  name: string;
  weightPct: number;
  returnPct: number;
  vsBenchmarkPct: number;
  contributionPct: number;
}

export interface AttributionAnalysis {
  agentId: FundAgentId;
  benchmark: BenchmarkName;
  benchmarkDisplay: string;
  days: number;
  fundReturnPct: number;
  benchmarkReturnPct: number;
  excessReturnPct: number;
  cashDragPct: number;
  cashRatioPct: number;
  selectionEffectPct: number;
  residualPct: number;
  topContributors: AttributionContribution[];
  topDetractors: AttributionContribution[];
  narrative: string;
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
