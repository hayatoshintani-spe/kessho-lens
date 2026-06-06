'use client';

import { useState } from 'react';
import { BarChart3, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { KPI_DEFS } from '@/lib/reform-taxonomies';
import { MOCK_KPI_SNAPSHOTS } from '@/lib/reform-mock';
import type { KPIDefinition, KPISnapshot, KPIUnit } from '@/lib/reform-types';

const STATUS_COLOR: Record<KPISnapshot['status'], string> = {
  on_track: '#1D9E75',
  at_risk: '#C8860A',
  off_track: '#D85A30',
  no_data: '#7B7F8C',
};
const STATUS_LABEL: Record<KPISnapshot['status'], string> = {
  on_track: '順調',
  at_risk: '注意',
  off_track: '未達',
  no_data: '未集計',
};

const CATEGORIES: Array<{ id: KPIDefinition['category']; label: string }> = [
  { id: 'revenue', label: '売上' },
  { id: 'profit', label: '利益' },
  { id: 'product', label: '商品' },
  { id: 'customer', label: '顧客' },
  { id: 'global', label: '海外' },
  { id: 'license', label: 'ライセンス' },
  { id: 'social', label: 'ソーシャル' },
];

function formatValue(value: number, unit: KPIUnit): string {
  if (unit === 'jpy') {
    if (value >= 100_000_000) return `${(value / 100_000_000).toFixed(2)}億円`;
    if (value >= 10_000) return `${(value / 10_000).toFixed(1)}万円`;
    return `${value.toLocaleString()}円`;
  }
  if (unit === 'pct' || unit === 'ratio') return `${value.toFixed(1)}%`;
  if (unit === 'people') return `${value.toLocaleString()}人`;
  return value.toLocaleString();
}

function progressPct(value: number, target?: number): number {
  if (!target || target === 0) return 0;
  return Math.min(100, Math.round((value / target) * 100));
}

export default function KPIPage() {
  const [activeCategory, setActiveCategory] =
    useState<KPIDefinition['category'] | 'all'>('all');

  const filtered = KPI_DEFS.filter(k =>
    activeCategory === 'all' ? true : k.category === activeCategory,
  );

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <BarChart3 className="w-5 h-5 text-accent-gold" />
          <h1 className="text-text-primary text-xl font-bold">KPI ダッシュボード</h1>
        </div>
        <p className="text-text-muted text-sm">
          改革テーマに紐づく KPI を一元管理。スプレッドシート / BI 連携の土台。
        </p>
      </div>

      {/* カテゴリフィルタ */}
      <div className="flex flex-wrap gap-2 text-xs">
        <button
          className={`px-2.5 py-1 rounded border ${activeCategory === 'all'
            ? 'border-accent-gold/60 text-accent-gold bg-accent-gold/10'
            : 'border-border text-text-secondary hover:text-accent-gold'}`}
          onClick={() => setActiveCategory('all')}
        >
          すべて
        </button>
        {CATEGORIES.map(c => (
          <button
            key={c.id}
            className={`px-2.5 py-1 rounded border ${activeCategory === c.id
              ? 'border-accent-gold/60 text-accent-gold bg-accent-gold/10'
              : 'border-border text-text-secondary hover:text-accent-gold'}`}
            onClick={() => setActiveCategory(c.id)}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* KPI カード一覧 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {filtered.map(def => {
          const snap = MOCK_KPI_SNAPSHOTS.find(s => s.kpi_id === def.id);
          return <KPICard key={def.id} def={def} snap={snap} />;
        })}
      </div>

      {/* 連携ヒント */}
      <div className="card p-4 border-dashed border-border text-xs text-text-muted">
        <div className="font-semibold text-text-secondary mb-1">将来連携想定</div>
        <ul className="space-y-1 list-disc list-inside">
          <li>Google Sheets / Notion DB から KPI 実績を自動取得</li>
          <li>BI ツール (Looker / Metabase) ダッシュボード埋め込み</li>
          <li>改革テーマと KPI の紐付けを自動推論</li>
          <li>未達 KPI から関連シグナル/アクション提案</li>
        </ul>
      </div>
    </div>
  );
}

function KPICard({ def, snap }: { def: KPIDefinition; snap?: KPISnapshot }) {
  if (!snap) {
    return (
      <div className="card p-4">
        <h3 className="text-text-primary text-sm font-semibold">{def.label}</h3>
        <p className="text-text-muted text-[11px] mt-0.5">{def.description}</p>
        <div className="mt-3 text-text-muted text-xs italic">データ未連携</div>
      </div>
    );
  }
  const pct = progressPct(snap.value, snap.target);
  const color = STATUS_COLOR[snap.status];
  const Delta =
    !snap.delta_vs_prev ? Minus
      : snap.delta_vs_prev > 0 ? TrendingUp
      : TrendingDown;
  const deltaColor =
    !snap.delta_vs_prev ? '#7B7F8C'
      : snap.delta_vs_prev > 0 ? '#1D9E75' : '#D85A30';

  return (
    <div className="card p-4" style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="text-text-primary text-sm font-semibold truncate">{def.label}</h3>
          <p className="text-text-muted text-[10px] mt-0.5 line-clamp-2">{def.description}</p>
        </div>
        <span
          className="text-[10px] px-1.5 py-0.5 rounded whitespace-nowrap flex-shrink-0"
          style={{ background: `${color}1A`, color, border: `1px solid ${color}40` }}
        >
          {STATUS_LABEL[snap.status]}
        </span>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <div className="text-2xl font-bold tabular-nums" style={{ color }}>
          {formatValue(snap.value, def.unit)}
        </div>
        {snap.target && (
          <div className="text-[10px] text-text-muted">
            / 目標 {formatValue(snap.target, def.unit)}
          </div>
        )}
      </div>

      {snap.target && (
        <div className="mt-2 h-1.5 rounded bg-bg-elevated overflow-hidden">
          <div
            className="h-full transition-all"
            style={{ width: `${pct}%`, background: color }}
          />
        </div>
      )}

      <div className="mt-2 flex items-center justify-between text-[10px]">
        <span className="text-text-muted">{snap.period}</span>
        {snap.delta_vs_prev !== undefined && (
          <span className="flex items-center gap-1" style={{ color: deltaColor }}>
            <Delta className="w-3 h-3" />
            {snap.delta_vs_prev > 0 ? '+' : ''}
            {(snap.delta_vs_prev * 100).toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  );
}
