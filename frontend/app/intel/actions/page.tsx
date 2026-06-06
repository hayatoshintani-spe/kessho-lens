'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { CheckSquare, Filter, ArrowRight, Plus } from 'lucide-react';
import { MOCK_ACTIONS } from '@/lib/reform-mock';
import {
  ACTION_STATUS_COLORS,
  ACTION_STATUS_LABELS,
  ACTION_PRIORITY_LABELS,
} from '@/lib/reform-types';
import type {
  ActionStatus,
  ActionPriorityLevel,
  ReformAction,
} from '@/lib/reform-types';
import { KPI_DEFS } from '@/lib/reform-taxonomies';

const TODAY = new Date().toISOString().slice(0, 10);

const STATUSES: ActionStatus[] =
  ['not_started', 'in_progress', 'awaiting_review', 'done', 'on_hold'];
const PRIORITIES: ActionPriorityLevel[] = ['urgent', 'high', 'medium', 'low'];

export default function ActionsPage() {
  const [statusFilter, setStatusFilter] = useState<ActionStatus | 'all'>('all');
  const [priorityFilter, setPriorityFilter] =
    useState<ActionPriorityLevel | 'all'>('all');
  const [actions, setActions] = useState<ReformAction[]>(MOCK_ACTIONS);

  const counts = useMemo(() => {
    const c: Record<ActionStatus, number> = {
      not_started: 0, in_progress: 0, awaiting_review: 0, done: 0, on_hold: 0,
    };
    actions.forEach(a => { c[a.status]++; });
    const overdue = actions.filter(a =>
      a.status !== 'done' && a.status !== 'on_hold' && a.deadline < TODAY,
    ).length;
    const dueThisWeek = actions.filter(a => {
      const wkAhead = new Date();
      wkAhead.setDate(wkAhead.getDate() + 7);
      return (
        a.status !== 'done' && a.status !== 'on_hold' &&
        a.deadline >= TODAY && a.deadline <= wkAhead.toISOString().slice(0, 10)
      );
    }).length;
    return { ...c, overdue, dueThisWeek };
  }, [actions]);

  const filtered = useMemo(() => {
    return actions
      .filter(a => statusFilter === 'all' ? true : a.status === statusFilter)
      .filter(a => priorityFilter === 'all' ? true : a.priority === priorityFilter)
      .sort((a, b) => {
        const overdue = (x: ReformAction) =>
          x.status !== 'done' && x.status !== 'on_hold' && x.deadline < TODAY;
        if (overdue(a) !== overdue(b)) return overdue(a) ? -1 : 1;
        return a.deadline.localeCompare(b.deadline);
      });
  }, [actions, statusFilter, priorityFilter]);

  function updateStatus(id: string, status: ActionStatus) {
    setActions(prev => prev.map(a => (a.id === id ? { ...a, status,
      updated_at: TODAY } : a)));
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      <div>
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-accent-gold" />
            <h1 className="text-text-primary text-xl font-bold">アクション管理</h1>
          </div>
          <button
            type="button"
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/10 transition opacity-60 cursor-not-allowed"
            title="将来実装: 新規アクション追加"
            disabled
          >
            <Plus className="w-3.5 h-3.5" />
            新規アクション
          </button>
        </div>
        <p className="text-text-muted text-sm">
          改革カードから生まれた打ち手を、担当者・期限・KPI とともに追跡
        </p>
      </div>

      {/* サマリ */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <SummaryStat label="遅延" value={counts.overdue} color="#D85A30" />
        <SummaryStat label="今週期限" value={counts.dueThisWeek} color="#C8860A" />
        <SummaryStat label="進行中" value={counts.in_progress} color="#2196F3" />
        <SummaryStat label="判断待ち" value={counts.awaiting_review} color="#FF9800" />
        <SummaryStat label="完了" value={counts.done} color="#4CAF50" />
      </div>

      {/* フィルタ */}
      <div className="card p-3 flex flex-wrap items-center gap-3 text-xs">
        <Filter className="w-3.5 h-3.5 text-text-muted" />
        <FilterPill
          label={`ステータス: ${statusFilter === 'all' ? 'すべて' : ACTION_STATUS_LABELS[statusFilter]}`}
          onClick={() => {
            const idx = statusFilter === 'all' ? 0 : STATUSES.indexOf(statusFilter) + 1;
            setStatusFilter(idx >= STATUSES.length ? 'all' : STATUSES[idx]);
          }}
        />
        <FilterPill
          label={`優先度: ${priorityFilter === 'all' ? 'すべて' : ACTION_PRIORITY_LABELS[priorityFilter]}`}
          onClick={() => {
            const idx = priorityFilter === 'all' ? 0 : PRIORITIES.indexOf(priorityFilter) + 1;
            setPriorityFilter(idx >= PRIORITIES.length ? 'all' : PRIORITIES[idx]);
          }}
        />
        <span className="ml-auto text-text-muted">{filtered.length} 件</span>
      </div>

      {/* アクション一覧 */}
      <div className="space-y-2">
        {filtered.map(a => (
          <ActionCard key={a.id} action={a} onUpdateStatus={updateStatus} />
        ))}
        {filtered.length === 0 && (
          <div className="card p-6 text-center text-text-muted text-sm">
            該当するアクションはありません
          </div>
        )}
      </div>
    </div>
  );
}

function ActionCard({
  action, onUpdateStatus,
}: {
  action: ReformAction;
  onUpdateStatus: (id: string, status: ActionStatus) => void;
}) {
  const overdue =
    action.status !== 'done' && action.status !== 'on_hold' && action.deadline < TODAY;
  return (
    <div
      className="card p-4"
      style={{ borderLeft: `3px solid ${ACTION_STATUS_COLORS[action.status]}` }}
    >
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap text-[10px]">
            <span
              className="px-1.5 py-0.5 rounded font-semibold"
              style={{
                background: `${ACTION_STATUS_COLORS[action.status]}1A`,
                color: ACTION_STATUS_COLORS[action.status],
              }}
            >
              {ACTION_STATUS_LABELS[action.status]}
            </span>
            <span>{ACTION_PRIORITY_LABELS[action.priority]}</span>
            <span className="text-text-muted">·</span>
            <span className="text-text-muted">{action.owner}</span>
            <span className="text-text-muted">·</span>
            <span className={overdue ? 'text-loss font-medium' : 'text-text-muted'}>
              期限 {action.deadline}{overdue ? ' (遅延)' : ''}
            </span>
          </div>
          <h3 className="text-text-primary font-semibold text-sm leading-snug">
            {action.title}
          </h3>
          {action.memo && (
            <p className="text-text-secondary text-xs mt-1.5 leading-relaxed">
              {action.memo}
            </p>
          )}
          {(action.linked_kpi_ids?.length ?? 0) > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {action.linked_kpi_ids!.map(kid => {
                const kpi = KPI_DEFS.find(k => k.id === kid);
                if (!kpi) return null;
                return (
                  <Link
                    key={kid}
                    href="/intel/kpi"
                    className="text-[10px] px-1.5 py-0.5 rounded bg-bg-elevated/60 text-text-muted hover:text-accent-gold border border-border"
                  >
                    📊 {kpi.label}
                  </Link>
                );
              })}
            </div>
          )}
          {action.card_id && (
            <Link
              href={`/intel/cards/${action.card_id}`}
              className="mt-2 inline-flex items-center gap-1 text-[10px] text-accent-gold hover:text-accent-gold-light"
            >
              関連カード <ArrowRight className="w-3 h-3" />
            </Link>
          )}
        </div>
        <div className="flex-shrink-0">
          <select
            value={action.status}
            onChange={e => onUpdateStatus(action.id, e.target.value as ActionStatus)}
            className="text-[10px] bg-bg-elevated border border-border rounded px-1.5 py-1 text-text-primary"
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>{ACTION_STATUS_LABELS[s]}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

function SummaryStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="card p-3" style={{ borderTop: `2px solid ${color}` }}>
      <div className="text-text-muted text-[10px]">{label}</div>
      <div className="text-2xl font-bold mt-1 font-tabular" style={{ color }}>
        {value}
      </div>
    </div>
  );
}

function FilterPill({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="px-2.5 py-1 rounded border border-border text-text-secondary hover:text-accent-gold hover:border-accent-gold/40 transition"
    >
      {label}
    </button>
  );
}
