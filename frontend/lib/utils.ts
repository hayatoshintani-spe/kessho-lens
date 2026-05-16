import { type ClassValue, clsx } from 'clsx';
import { format, parseISO, isValid, formatDistanceToNow } from 'date-fns';
import { ja } from 'date-fns/locale';
import type { AgentId, MessageType } from './types';

// ─── Tailwind class merging ───────────────────────────────────────────────────

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// ─── Date formatting ──────────────────────────────────────────────────────────

export function formatDate(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'yyyy年M月d日', { locale: ja });
  } catch {
    return dateStr;
  }
}

export function formatDateShort(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'M月d日', { locale: ja });
  } catch {
    return dateStr;
  }
}

export function formatDatetime(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'yyyy年M月d日 HH:mm', { locale: ja });
  } catch {
    return dateStr;
  }
}

export function formatRelative(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return formatDistanceToNow(d, { locale: ja, addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function formatChartDate(dateStr: string): string {
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'M/d');
  } catch {
    return dateStr;
  }
}

// ─── Number formatting ────────────────────────────────────────────────────────

export function formatPct(value: number, decimals = 2): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

export function formatCurrency(value: number, currency = 'JPY'): string {
  if (currency === 'JPY') {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      maximumFractionDigits: 0,
    }).format(value);
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatLargeNumber(value: number): string {
  if (Math.abs(value) >= 1_0000_0000) {
    return `${(value / 1_0000_0000).toFixed(1)}億円`;
  }
  if (Math.abs(value) >= 1_0000) {
    return `${(value / 1_0000).toFixed(0)}万円`;
  }
  return `${value.toLocaleString('ja-JP')}円`;
}

// ─── Agent helpers ────────────────────────────────────────────────────────────

export const AGENT_COLORS: Record<string, string> = {
  // ファンドメンバー（4名）
  buffett: '#4CAF50',
  soros: '#E91E63',
  lynch: '#2196F3',
  flat: '#9E9E9E',
  // 専門分析AI（3名）
  macro: '#7C3AED',   // 紫: マクロ経済
  quant: '#0891B2',   // シアン: 定量分析
  risk: '#DC2626',    // 赤: リスク管理
};

export const AGENT_NAMES: Record<string, { en: string; ja: string }> = {
  buffett: { en: 'BuffettAI', ja: 'バフェットAI' },
  soros: { en: 'SorosAI', ja: 'ソロスAI' },
  lynch: { en: 'LynchAI', ja: 'リンチAI' },
  flat: { en: 'FlatAI', ja: 'フラットAI' },
  macro: { en: 'MacroAI', ja: 'マクロAI' },
  quant: { en: 'QuantAI', ja: 'クオンツAI' },
  risk: { en: 'RiskAI', ja: 'リスクAI' },
};

export function agentColor(id: AgentId): string {
  return AGENT_COLORS[id] ?? '#7B7F8C';
}

export function agentInitial(id: AgentId): string {
  return AGENT_NAMES[id]?.en.charAt(0) ?? id.charAt(0).toUpperCase();
}

// ─── Message type labels ──────────────────────────────────────────────────────

export const MESSAGE_TYPE_LABELS: Record<string, string> = {
  opening: '開始',
  debate: '議論',
  proposal: '提案',
  rebuttal: '反論',
  decision: '決定',
  analysis: '分析',
  closing: '締め',
  risk_check: 'リスク確認',
  scenario: 'シナリオ分析',
};

export const MESSAGE_TYPE_COLORS: Record<string, string> = {
  opening: '#C8860A',
  debate: '#E91E63',
  proposal: '#2196F3',
  rebuttal: '#FF7043',
  decision: '#1D9E75',
  analysis: '#9C27B0',
  closing: '#607D8B',
  risk_check: '#DC2626',  // 赤: リスク確認
  scenario: '#0891B2',    // シアン: シナリオ分析
};

// ─── P&L helpers ─────────────────────────────────────────────────────────────

export function pnlColor(value: number): string {
  if (value > 0) return '#1D9E75';
  if (value < 0) return '#D85A30';
  return '#7B7F8C';
}

export function pnlClass(value: number): string {
  if (value > 0) return 'text-profit';
  if (value < 0) return 'text-loss';
  return 'text-text-secondary';
}

// ─── Mock data generators (for when backend is offline) ───────────────────────

export function generateMockPnlData(days = 30): Array<{ date: string; buffett: number; soros: number; lynch: number; flat: number }> {
  const data = [];
  const today = new Date();
  let b = 0, s = 0, l = 0, f = 0;

  for (let i = days; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateStr = format(d, 'yyyy-MM-dd');

    b += (Math.random() - 0.45) * 1.2;
    s += (Math.random() - 0.42) * 2.0;
    l += (Math.random() - 0.44) * 1.5;
    f += (Math.random() - 0.47) * 0.4;

    data.push({
      date: dateStr,
      buffett: parseFloat(b.toFixed(2)),
      soros: parseFloat(s.toFixed(2)),
      lynch: parseFloat(l.toFixed(2)),
      flat: parseFloat(f.toFixed(2)),
    });
  }

  return data;
}
