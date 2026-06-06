// 改革カード / 経営課題マップ / IPビジネスレンズ / アクション / KPI / 週次アジェンダ
// すべて IntelCard を拡張せず、サイドカー的に紐付ける構造。
// 将来的に AI 算出 / Notion 連携 / Slack 連携を差し込めるよう疎結合に保つ。

import type { IntelCard } from './intel-types';

// ─── 経営課題マップ (Management Theme) ────────────────────────────────

export type ThemeGroupId =
  | 'revenue_growth'
  | 'profit_improvement'
  | 'org_reform'
  | 'finance_ir'
  | 'risk';

export type ThemeId =
  // 売上成長
  | 'global_ip'
  | 'd2c'
  | 'md_reform'
  | 'experience'
  | 'collab'
  // 利益改善
  | 'royalty_design'
  | 'cogs'
  | 'sga_opt'
  | 'high_margin_products'
  // 組織改革
  | 'sales_org'
  | 'product_org'
  | 'crm_org'
  | 'data_org'
  // 財務・株価
  | 'ir_story'
  | 'capital_efficiency'
  | 'midterm_plan'
  // リスク
  | 'china_dependence'
  | 'contract_risk'
  | 'counterfeit'
  | 'ip_damage'
  | 'regulation';

export interface ThemeMeta {
  id: ThemeId;
  group: ThemeGroupId;
  label: string;
  short: string;
  description: string;
}

export interface ThemeGroupMeta {
  id: ThemeGroupId;
  label: string;
  color: string;
  icon: string;
}

// ─── IPビジネスレンズ ─────────────────────────────────────────────────

export type IPLensId =
  | 'ip_monetization'
  | 'china'
  | 'product_planning'
  | 'harajuku'
  | 'd2c_crm'
  | 'license_contract'
  | 'global_expansion'
  | 'fan_community';

export interface IPLensMeta {
  id: IPLensId;
  label: string;
  short: string;
  icon: string;
  description: string;
}

// ─── 経営インパクトスコア ─────────────────────────────────────────────

export interface ImpactComponents {
  revenue: number;          // 売上インパクト 0-100
  profit: number;           // 利益インパクト 0-100
  urgency: number;          // 緊急度 0-100
  executability: number;    // 実行可能性 0-100
  relevance: number;        // 自社との関連度 0-100
  competitive_edge: number; // 競争優位への影響 0-100
  risk: number;             // リスク度 0-100
  boardroom: number;        // 経営会議で扱うべき度 0-100
}

export type RecommendedAction =
  | 'next_board_meeting'    // 次回経営会議で討議
  | 'this_week_action'      // 今週中に動く
  | 'this_month_action'     // 今月中に動く
  | 'watch_continuously'    // 継続監視
  | 'archive';              // アーカイブ

export interface ManagementImpact {
  score: number;            // 0-100, 加重平均
  components: ImpactComponents;
  recommendation: RecommendedAction;
  rationale: string;        // 1行で算出根拠
}

// ─── 改革カード (IntelCard + 経営改革ステータス) ─────────────────────

export type ReformStatus =
  | 'unreviewed'   // 未検討
  | 'reviewing'   // 検討中
  | 'in_progress' // 実行中
  | 'done'        // 完了
  | 'on_hold';    // 保留

export interface ReformCardEnrichment {
  card_id: string;
  themes: ThemeId[];
  lenses: IPLensId[];
  impact: ManagementImpact;
  status: ReformStatus;
  hypothesis?: string;        // 仮説
  management_question?: string; // 経営論点
  owner_department?: string;
  deadline?: string;
  linked_kpi_ids?: string[];
  linked_council_id?: string;
}

// ─── アクション ───────────────────────────────────────────────────────

export type ActionStatus =
  | 'not_started'
  | 'in_progress'
  | 'awaiting_review'
  | 'done'
  | 'on_hold';

export type ActionPriorityLevel = 'urgent' | 'high' | 'medium' | 'low';

export interface ReformAction {
  id: string;
  title: string;
  card_id?: string;           // 関連改革カード
  owner: string;
  deadline: string;
  status: ActionStatus;
  priority: ActionPriorityLevel;
  memo?: string;
  linked_kpi_ids?: string[];
  next_review_date?: string;
  created_at: string;
  updated_at: string;
}

// ─── KPI ──────────────────────────────────────────────────────────────

export type KPIUnit = 'jpy' | 'pct' | 'count' | 'people' | 'ratio';

export interface KPIDefinition {
  id: string;
  label: string;
  unit: KPIUnit;
  category: 'revenue' | 'profit' | 'product' | 'customer' | 'global' | 'license' | 'social';
  description: string;
}

export interface KPISnapshot {
  kpi_id: string;
  value: number;
  target?: number;
  period: string;          // YYYY-MM or YYYY-Q1 etc
  delta_vs_prev?: number;  // 前期比 (-1 to +inf)
  status: 'on_track' | 'at_risk' | 'off_track' | 'no_data';
  updated_at: string;
}

// ─── 週次経営会議アジェンダ ───────────────────────────────────────────

export interface WeeklyAgendaItem {
  id: string;
  rank: number;             // 1-5
  topic: string;
  background: string;
  why_now: string;
  related_card_ids: string[];
  related_kpi_ids: string[];
  recommended_decision: string;
  next_action: string;
  week_of: string;          // YYYY-MM-DD (週開始日)
}

// ─── ダッシュボード集計 ───────────────────────────────────────────────

export interface DashboardSignal {
  card: IntelCard;
  impact: ManagementImpact;
  themes: ThemeId[];
  lenses: IPLensId[];
}

export interface ReformDashboard {
  important_signals: DashboardSignal[];      // 本日見るべき重要シグナル
  board_discussion_points: DashboardSignal[]; // 経営会議で扱うべき論点
  opportunities: DashboardSignal[];          // 新規事業機会
  risks: DashboardSignal[];                  // 重要リスク
  in_progress_themes: ThemeId[];             // 進行中の改革テーマ
  delayed_actions: ReformAction[];           // 遅延しているアクション
  pending_decisions: ReformAction[];         // 経営判断待ち
  weekly_priority_themes: ThemeId[];         // 今週優先すべき改革テーマ
}

// ─── 表示用ヘルパー ─────────────────────────────────────────────────

export const REFORM_STATUS_LABELS: Record<ReformStatus, string> = {
  unreviewed: '未検討',
  reviewing: '検討中',
  in_progress: '実行中',
  done: '完了',
  on_hold: '保留',
};

export const REFORM_STATUS_COLORS: Record<ReformStatus, string> = {
  unreviewed: '#7B7F8C',
  reviewing: '#2196F3',
  in_progress: '#1D9E75',
  done: '#4CAF50',
  on_hold: '#FF9800',
};

export const ACTION_STATUS_LABELS: Record<ActionStatus, string> = {
  not_started: '未着手',
  in_progress: '進行中',
  awaiting_review: '確認待ち',
  done: '完了',
  on_hold: '保留',
};

export const ACTION_STATUS_COLORS: Record<ActionStatus, string> = {
  not_started: '#7B7F8C',
  in_progress: '#2196F3',
  awaiting_review: '#FF9800',
  done: '#4CAF50',
  on_hold: '#9E9E9E',
};

export const ACTION_PRIORITY_LABELS: Record<ActionPriorityLevel, string> = {
  urgent: '🔴 緊急',
  high: '🟠 高',
  medium: '🟡 中',
  low: '⚪ 低',
};

export const RECOMMENDED_ACTION_LABELS: Record<RecommendedAction, string> = {
  next_board_meeting: '次回経営会議で討議',
  this_week_action: '今週中に動く',
  this_month_action: '今月中に動く',
  watch_continuously: '継続監視',
  archive: 'アーカイブ',
};
