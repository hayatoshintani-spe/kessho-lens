// Shared TypeScript types for frontend and documentation

export type AgentId = "buffett" | "soros" | "lynch" | "flat";

// ─── Tsuburaya Intelligence Brief ───────────────────────────────────────────

export type IntelCategory =
  | "ip_content"
  | "ai_agent"
  | "device_telecom"
  | "global_region"
  | "retail_md_license"
  | "regulation_ip_law"
  | "competitor_capital";

export type Importance = "A" | "B" | "C" | "D";
export type BriefType = "daily" | "weekly" | "monthly";
export type ExpertId =
  | "ip_strategist"
  | "global_expansion"
  | "md_licensing"
  | "ai_trend"
  | "cfo"
  | "risk_manager";

export interface IntelSource {
  title: string;
  url?: string;
  publisher?: string;
  publishedAt?: string;
  accessStatus?: "full" | "title_only" | "paywalled" | "estimated";
}

export interface IntelInsight {
  whatItMeans: string;
  businessOpportunity: string[];
  risk: string[];
}

export interface IntelAction {
  who: string;
  what: string;
  deadline?: string;
  priority: "urgent" | "this_week" | "this_month" | "watch";
}

export interface IntelCard {
  id: string;
  date: string;
  title: string;
  oneLiner: string;
  category: IntelCategory;
  importance: Importance;
  fact: string;
  interpretation: string;
  insight: IntelInsight;
  actions: IntelAction[];
  tags: string[];
  sources: IntelSource[];
  confidence: "high" | "medium" | "low";
  speculationNotes?: string;
  relatedCardIds: string[];
  relatedAgents: ExpertId[];
}

export interface CouncilMessage {
  expertId: ExpertId;
  expertName: string;
  time: string;
  content: string;
  stance: "support" | "challenge" | "neutral" | "concern" | "proposal";
}

export interface CouncilSession {
  id: string;
  date: string;
  topic: string;
  triggerCardIds: string[];
  summary: string;
  messages: CouncilMessage[];
  editorConclusion: {
    adopt: string[];
    hold: string[];
    research: string[];
  };
}

export interface BriefSection {
  heading: string;
  body: string;
}

export interface DailyBrief {
  date: string;
  title: string;
  topTopics: string[];
  executiveSummary: string;
  businessOpportunities: string[];
  risks: string[];
  nextActions: IntelAction[];
  sections: BriefSection[];
  councilSessionId?: string;
}

export interface WatchlistItem {
  keyword: string;
  category: IntelCategory;
  rationale: string;
  priority: "high" | "medium" | "low";
}

export interface CategoryWatchlist {
  category: IntelCategory;
  label: string;
  description: string;
  targets: string[];
  items: WatchlistItem[];
}

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
