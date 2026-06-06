// 経営インパクトスコア算出 (ルールベース v1)
// IntelCard を受け取り、8 軸のサブスコアと総合スコア(0-100)+推奨アクションを返す
//
// 設計方針:
// - 透明な算出根拠を rationale で返す(経営陣への説明性)
// - LLM 算出に差し替えやすいよう純粋関数で実装
// - 既存の importance / category / tags / actions を活用

import type { IntelCard, ActionPriority } from './intel-types';
import type {
  ImpactComponents,
  ManagementImpact,
  RecommendedAction,
  ThemeId,
  IPLensId,
} from './reform-types';
import {
  KEYWORD_TO_THEMES,
  KEYWORD_TO_LENSES,
  DEFAULT_LENS,
} from './reform-taxonomies';

const clamp = (n: number, min = 0, max = 100) => Math.max(min, Math.min(max, n));

// 重要度 → ベーススコア
const IMPORTANCE_BASE: Record<'A' | 'B' | 'C' | 'D', number> = {
  A: 85, B: 70, C: 50, D: 30,
};

// カテゴリ別 重みプロファイル(円谷の業態を踏まえて手動チューニング)
const CATEGORY_PROFILE: Record<
  IntelCard['category'],
  Partial<ImpactComponents>
> = {
  ip_content:       { revenue: 80, relevance: 90, competitive_edge: 80 },
  retail_md_license:{ revenue: 75, profit: 80, relevance: 85, executability: 70 },
  global_region:    { revenue: 70, relevance: 75, urgency: 65, risk: 60 },
  competitor_capital:{ competitive_edge: 85, urgency: 70, boardroom: 80 },
  regulation_ip_law:{ risk: 85, urgency: 75, boardroom: 80 },
  ai_agent:         { competitive_edge: 70, relevance: 60, executability: 60 },
  device_telecom:   { relevance: 40, executability: 50 },
};

const ACTION_URGENCY: Record<ActionPriority, number> = {
  urgent: 95, this_week: 80, this_month: 60, watch: 40,
};

const TSUBURAYA_KEYWORDS = /円谷|tsuburaya|ウルトラマン|ultraman|怪獣|セブン|ゼロ|tiga/i;

export function classifyThemes(card: IntelCard): ThemeId[] {
  const text = [
    card.title, card.one_liner, card.fact, card.interpretation,
    ...(card.tags ?? []),
    card.insight?.what_it_means ?? '',
  ].join(' ');
  const matched = new Set<ThemeId>();
  for (const { kw, themes } of KEYWORD_TO_THEMES) {
    if (kw.test(text)) themes.forEach(t => matched.add(t));
  }
  return Array.from(matched);
}

export function classifyLenses(card: IntelCard): IPLensId[] {
  const text = [
    card.title, card.one_liner, card.fact, card.interpretation,
    ...(card.tags ?? []),
  ].join(' ');
  const matched = new Set<IPLensId>();
  for (const { kw, lenses } of KEYWORD_TO_LENSES) {
    if (kw.test(text)) lenses.forEach(l => matched.add(l));
  }
  if (matched.size === 0) matched.add(DEFAULT_LENS);
  return Array.from(matched);
}

export function computeImpact(card: IntelCard): ManagementImpact {
  const base = IMPORTANCE_BASE[card.importance] ?? 50;
  const profile = CATEGORY_PROFILE[card.category] ?? {};

  const text = `${card.title} ${card.one_liner} ${card.fact} ${card.interpretation} ${(card.tags ?? []).join(' ')}`;
  const tsuburayaHit = TSUBURAYA_KEYWORDS.test(text);

  // 最大アクション優先度から緊急度を抽出
  const maxActionUrgency = card.actions.reduce(
    (m, a) => Math.max(m, ACTION_URGENCY[a.priority] ?? 40), 40,
  );

  // 仮置きで base から開始し、カテゴリプロファイル/キーワード/アクションで上書き
  const components: ImpactComponents = {
    revenue: clamp(profile.revenue ?? base * 0.8),
    profit: clamp(profile.profit ?? base * 0.75),
    urgency: clamp((profile.urgency ?? base * 0.7) * 0.5 + maxActionUrgency * 0.5),
    executability: clamp(profile.executability ?? 55),
    relevance: clamp(profile.relevance ?? base * 0.7),
    competitive_edge: clamp(profile.competitive_edge ?? base * 0.6),
    risk: clamp(profile.risk ?? (card.insight?.risk?.length ?? 0) * 25),
    boardroom: clamp(profile.boardroom ?? base),
  };

  // 円谷直接言及があれば関連度を底上げ
  if (tsuburayaHit) {
    components.relevance = clamp(components.relevance + 15);
    components.boardroom = clamp(components.boardroom + 10);
  }

  // 信頼度低 → 経営会議度を引く
  if (card.confidence === 'low') {
    components.boardroom = clamp(components.boardroom - 15);
  }

  // 機会数 → 売上/競争優位を底上げ
  const oppCount = card.insight?.business_opportunity?.length ?? 0;
  if (oppCount > 0) {
    components.revenue = clamp(components.revenue + oppCount * 3);
    components.competitive_edge = clamp(components.competitive_edge + oppCount * 2);
  }
  // リスク数 → リスク/経営会議度を底上げ
  const riskCount = card.insight?.risk?.length ?? 0;
  if (riskCount > 0) {
    components.risk = clamp(Math.max(components.risk, 40 + riskCount * 15));
    components.boardroom = clamp(components.boardroom + Math.min(15, riskCount * 5));
  }

  // 加重平均(経営会議への持ち込み度合いを重視)
  const weights = {
    revenue: 1.4,
    profit: 1.2,
    urgency: 1.2,
    executability: 0.8,
    relevance: 1.5,
    competitive_edge: 1.0,
    risk: 1.0,
    boardroom: 1.4,
  };
  const wSum = Object.values(weights).reduce((a, b) => a + b, 0);
  const score = Math.round(
    (
      components.revenue * weights.revenue +
      components.profit * weights.profit +
      components.urgency * weights.urgency +
      components.executability * weights.executability +
      components.relevance * weights.relevance +
      components.competitive_edge * weights.competitive_edge +
      components.risk * weights.risk +
      components.boardroom * weights.boardroom
    ) / wSum,
  );

  let recommendation: RecommendedAction = 'watch_continuously';
  if (score >= 80) recommendation = 'next_board_meeting';
  else if (score >= 65 && components.urgency >= 70) recommendation = 'this_week_action';
  else if (score >= 60) recommendation = 'this_month_action';
  else if (score < 40) recommendation = 'archive';

  // rationale: 上位 3 軸を抜き出す
  const top3 = (Object.entries(components) as [keyof ImpactComponents, number][])
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);
  const labelMap: Record<keyof ImpactComponents, string> = {
    revenue: '売上',
    profit: '利益',
    urgency: '緊急度',
    executability: '実行可能性',
    relevance: '自社関連',
    competitive_edge: '競争優位',
    risk: 'リスク',
    boardroom: '会議度',
  };
  const rationale =
    `重要度${card.importance}・${top3.map(([k, v]) => `${labelMap[k]}${v}`).join('/')}`;

  return { score, components, recommendation, rationale };
}

// 既存カードリストを ManagementImpact 付きで返す
export function enrichCards<T extends IntelCard>(cards: T[]):
  Array<{ card: T; impact: ManagementImpact; themes: ThemeId[]; lenses: IPLensId[] }> {
  return cards.map(card => ({
    card,
    impact: computeImpact(card),
    themes: classifyThemes(card),
    lenses: classifyLenses(card),
  }));
}
