'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { CheckSquare, Filter, ArrowRight, Plus, X } from 'lucide-react';
import { warmupBackend } from '@/lib/api';
import {
  fetchReformActions,
  createReformAction,
  updateReformAction,
} from '@/lib/reform-api';
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
  const [actions, setActions] = useState<ReformAction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(60_000);
      if (!alive) {
        setErrorMsg('バックエンドに接続できません');
        setIsLoading(false);
        return;
      }
      try {
        setActions(await fetchReformActions());
      } catch (e) {
        setErrorMsg((e as Error).message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

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

  async function updateStatus(id: string, status: ActionStatus) {
    const prev = actions;
    // 楽観更新 → 失敗時ロールバック
    setActions(p => p.map(a => (a.id === id ? { ...a, status, updated_at: TODAY } : a)));
    try {
      const saved = await updateReformAction(id, { status });
      setActions(p => p.map(a => (a.id === id ? saved : a)));
    } catch (e) {
      setActions(prev);
      setErrorMsg(`ステータス更新に失敗: ${(e as Error).message}`);
    }
  }

  async function handleCreate(input: {
    title: string; owner: string; deadline: string;
    priority: ActionPriorityLevel; memo?: string;
  }) {
    const created = await createReformAction(input);
    setActions(p => [created, ...p]);
    setShowForm(false);
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
            onClick={() => setShowForm(v => !v)}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/10 transition"
          >
            {showForm ? <X className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
            {showForm ? '閉じる' : '新規アクション'}
          </button>
        </div>
        <p className="text-text-muted text-sm">
          改革カードから生まれた打ち手を、担当者・期限・KPI とともに追跡
        </p>
      </div>

      {errorMsg && (
        <div className="card p-3 border-loss/40 bg-loss/5 text-loss text-xs">
          {errorMsg}
        </div>
      )}

      {showForm && <NewActionForm onCreate={handleCreate} />}

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
        {isLoading ? (
          <div className="card p-6 text-center text-text-muted text-sm">
            読み込み中...
          </div>
        ) : (
          <>
            {filtered.map(a => (
              <ActionCard key={a.id} action={a} onUpdateStatus={updateStatus} />
            ))}
            {filtered.length === 0 && (
              <div className="card p-6 text-center text-text-muted text-sm">
                該当するアクションはありません
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function NewActionForm({
  onCreate,
}: {
  onCreate: (input: {
    title: string; owner: string; deadline: string;
    priority: ActionPriorityLevel; memo?: string;
  }) => Promise<void>;
}) {
  const [title, setTitle] = useState('');
  const [owner, setOwner] = useState('');
  const [deadline, setDeadline] = useState('');
  const [priority, setPriority] = useState<ActionPriorityLevel>('medium');
  const [memo, setMemo] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const valid = title.trim() && owner.trim() && deadline;

  async function submit() {
    if (!valid || saving) return;
    setSaving(true);
    setError(null);
    try {
      await onCreate({
        title: title.trim(),
        owner: owner.trim(),
        deadline,
        priority,
        memo: memo.trim() || undefined,
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const inputCls =
    'w-full bg-bg-elevated border border-border rounded px-2 py-1.5 text-xs text-text-primary placeholder:text-text-muted';

  return (
    <div className="card p-4 border-accent-gold/30 space-y-3">
      <div className="text-text-primary text-sm font-semibold">新規アクション</div>
      <input
        className={inputCls}
        placeholder="タイトル(例: 中国MD自社企画比率の引き上げ施策案を立案)"
        value={title}
        onChange={e => setTitle(e.target.value)}
      />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <input
          className={inputCls}
          placeholder="担当(例: 商品企画部)"
          value={owner}
          onChange={e => setOwner(e.target.value)}
        />
        <input
          className={inputCls}
          type="date"
          value={deadline}
          onChange={e => setDeadline(e.target.value)}
        />
        <select
          className={inputCls}
          value={priority}
          onChange={e => setPriority(e.target.value as ActionPriorityLevel)}
        >
          {PRIORITIES.map(p => (
            <option key={p} value={p}>{ACTION_PRIORITY_LABELS[p]}</option>
          ))}
        </select>
      </div>
      <textarea
        className={inputCls}
        rows={2}
        placeholder="メモ(任意)"
        value={memo}
        onChange={e => setMemo(e.target.value)}
      />
      {error && <div className="text-loss text-xs">{error}</div>}
      <div className="flex justify-end">
        <button
          type="button"
          onClick={submit}
          disabled={!valid || saving}
          className="text-xs px-4 py-1.5 rounded bg-accent-gold/15 border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/25 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {saving ? '保存中…' : '作成'}
        </button>
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
