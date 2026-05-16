// Tsuburaya Intelligence Brief — 共有 TypeScript 型

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
