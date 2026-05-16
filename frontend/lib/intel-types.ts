// Tsuburaya Intelligence Brief 型定義
// shared/types.ts と同期している

export type IntelCategory =
  | 'ip_content'
  | 'ai_agent'
  | 'device_telecom'
  | 'global_region'
  | 'retail_md_license'
  | 'regulation_ip_law'
  | 'competitor_capital';

export type Importance = 'A' | 'B' | 'C' | 'D';

export type ExpertId =
  | 'ip_strategist'
  | 'global_expansion'
  | 'md_licensing'
  | 'ai_trend'
  | 'cfo'
  | 'risk_manager';

export type ActionPriority = 'urgent' | 'this_week' | 'this_month' | 'watch';

export type CouncilStance = 'support' | 'challenge' | 'neutral' | 'concern' | 'proposal';

export interface IntelSource {
  title: string;
  url?: string;
  publisher?: string;
  published_at?: string;
  access_status?: 'full' | 'title_only' | 'paywalled' | 'estimated';
}

export interface IntelInsight {
  what_it_means: string;
  business_opportunity: string[];
  risk: string[];
}

export interface IntelAction {
  who: string;
  what: string;
  deadline?: string;
  priority: ActionPriority;
}

export interface IntelCard {
  id: string;
  date: string;
  title: string;
  one_liner: string;
  category: IntelCategory;
  importance: Importance;
  fact: string;
  interpretation: string;
  insight: IntelInsight;
  actions: IntelAction[];
  tags: string[];
  sources: IntelSource[];
  confidence: 'high' | 'medium' | 'low';
  speculation_notes?: string | null;
  related_card_ids: string[];
  related_agents: ExpertId[];
}

export interface CouncilMessage {
  expert_id: ExpertId;
  expert_name: string;
  time: string;
  content: string;
  stance: CouncilStance;
}

export interface CouncilSession {
  id: string;
  date: string;
  topic: string;
  trigger_card_ids: string[];
  summary: string;
  messages: CouncilMessage[];
  editor_conclusion: {
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
  brief_type: 'daily' | 'weekly' | 'monthly';
  title: string;
  top_topics: string[];
  executive_summary: string;
  business_opportunities: string[];
  risks: string[];
  next_actions: IntelAction[];
  sections: BriefSection[];
  council_session_id?: string | null;
  generated_at?: string;
}

export interface BriefSummary {
  date: string;
  brief_type: string;
  title: string;
  executive_summary: string;
  card_count: number;
}

export interface CategoryMeta {
  id: IntelCategory;
  label: string;
  label_short: string;
  icon: string;
  color: string;
  targets: string[];
  watch_angles: string[];
  responsible_experts: ExpertId[];
}

export interface ExpertMeta {
  id: ExpertId;
  name: string;
  name_en: string;
  color: string;
  icon: string;
  focus: string;
  system_prompt?: string;
  key_questions: string[];
}

export interface ImportanceMeta {
  id: Importance;
  label: string;
  description: string;
  color: string;
}

export interface IntelMeta {
  categories: CategoryMeta[];
  experts: ExpertMeta[];
  importance: ImportanceMeta[];
}

export interface WatchlistItem {
  keyword: string;
  category: IntelCategory;
  rationale: string;
  priority: 'high' | 'medium' | 'low';
}

export interface CategoryWatchlist {
  category: IntelCategory;
  label: string;
  description: string;
  targets: string[];
  items: WatchlistItem[];
}

// ─── 表示用ヘルパー定数 ──────────────────────────────────────────────

export const CATEGORY_LABELS_JA: Record<IntelCategory, string> = {
  ip_content: 'IP・コンテンツ',
  ai_agent: 'AI・エージェント',
  device_telecom: 'デバイス・通信',
  global_region: 'グローバル・地域',
  retail_md_license: '小売・MD・ライセンス',
  regulation_ip_law: '規制・著作権',
  competitor_capital: '競合・資本市場',
};

export const CATEGORY_ICONS: Record<IntelCategory, string> = {
  ip_content: '🎭',
  ai_agent: '🤖',
  device_telecom: '📱',
  global_region: '🌏',
  retail_md_license: '🛍️',
  regulation_ip_law: '⚖️',
  competitor_capital: '📊',
};

export const CATEGORY_COLORS: Record<IntelCategory, string> = {
  ip_content: '#E91E63',
  ai_agent: '#2196F3',
  device_telecom: '#9C27B0',
  global_region: '#FF9800',
  retail_md_license: '#4CAF50',
  regulation_ip_law: '#607D8B',
  competitor_capital: '#C8860A',
};

export const IMPORTANCE_COLORS: Record<Importance, string> = {
  A: '#D85A30',
  B: '#C8860A',
  C: '#2196F3',
  D: '#7B7F8C',
};

export const IMPORTANCE_LABELS_JA: Record<Importance, string> = {
  A: '経営アジェンダ化',
  B: '事業部で検討',
  C: '情報共有',
  D: '参考情報',
};

export const EXPERT_LABELS_JA: Record<ExpertId, string> = {
  ip_strategist: 'IP戦略家',
  global_expansion: 'グローバル展開',
  md_licensing: 'MD/ライセンス',
  ai_trend: 'AI技術トレンド',
  cfo: 'CFO視点',
  risk_manager: 'リスク管理',
};

export const EXPERT_ICONS: Record<ExpertId, string> = {
  ip_strategist: '🎭',
  global_expansion: '🌏',
  md_licensing: '🛍️',
  ai_trend: '🤖',
  cfo: '💰',
  risk_manager: '⚠️',
};

export const EXPERT_COLORS: Record<ExpertId, string> = {
  ip_strategist: '#E91E63',
  global_expansion: '#FF9800',
  md_licensing: '#4CAF50',
  ai_trend: '#2196F3',
  cfo: '#C8860A',
  risk_manager: '#D85A30',
};

export const PRIORITY_LABELS_JA: Record<ActionPriority, string> = {
  urgent: '🔴 緊急',
  this_week: '🟡 今週',
  this_month: '🟢 今月',
  watch: '⚪ 継続監視',
};

export const STANCE_LABELS_JA: Record<CouncilStance, string> = {
  support: '賛成',
  challenge: '反論',
  neutral: '中立',
  concern: '懸念',
  proposal: '提案',
};

export const STANCE_COLORS: Record<CouncilStance, string> = {
  support: '#4CAF50',
  challenge: '#D85A30',
  neutral: '#7B7F8C',
  concern: '#FF9800',
  proposal: '#2196F3',
};
