// Shared TypeScript types for frontend and documentation

export type AgentId = "buffett" | "soros" | "lynch" | "flat";

export interface Holding {
  symbol: string;
  name: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  sector: string;
  unrealizedPnl?: number;
  unrealizedPnlPct?: number;
}

export interface Portfolio {
  agentId: AgentId;
  cash: number;
  totalValue: number;
  holdings: Holding[];
}

export interface Agent {
  id: AgentId;
  name: string;
  nameJa: string;
  personality: string;
  style: string;
  favoriteSectors: string[];
  color: string;
  avatar: string;
  portfolio?: Portfolio;
  totalReturn?: number;
  rank?: number;
  dailyReturn?: number;
}

export type MeetingMessageType = "opening" | "debate" | "proposal" | "rebuttal" | "decision";

export interface MeetingMessage {
  agent: string;
  time: string;
  content: string;
  type: MeetingMessageType;
}

export interface MeetingLog {
  date: string;
  participants: string[];
  summary: string;
  keyDecisions: string[];
  marketTheme: string;
  messages: MeetingMessage[];
}

export interface DailyReport {
  date: string;
  title: string;
  marketTheme: string;
  content: string;
  agentSummaries: Record<AgentId, string>;
}

export interface Trade {
  id: string;
  date: string;
  agentId: AgentId;
  action: "BUY" | "SELL" | "HOLD";
  symbol: string;
  name: string;
  shares: number;
  price: number;
  reason: string;
  meetingDecision: boolean;
}

export interface Discovery {
  symbol: string;
  name: string;
  reason: string;
  conviction: "HIGH" | "MEDIUM" | "LOW";
  action: string;
}

export interface DiscoveryLog {
  date: string;
  agentId: AgentId;
  discoveries: Discovery[];
}

export interface Memory {
  date: string;
  type: "lesson" | "conviction" | "discovery" | "validation";
  content: string;
  ticker: string | null;
}

export interface AgentMemories {
  agentId: AgentId;
  memories: Memory[];
}

export interface DashboardData {
  agents: AgentSummary[];
  chartData: ChartDataPoint[];
  latestMeeting: MeetingLog | null;
  latestReport: DailyReport | null;
  lastUpdated: string;
}

export interface AgentSummary {
  id: AgentId;
  name: string;
  nameJa: string;
  color: string;
  totalValue: number;
  totalReturn: number;
  dailyReturn: number;
  rank: number;
  latestDecision: string;
}

export interface ChartDataPoint {
  date: string;
  buffett: number;
  soros: number;
  lynch: number;
  flat: number;
}
