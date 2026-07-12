// 改革ダッシュボード (アクション / KPI / 週次アジェンダ) API クライアント
// バックエンド: backend/api/intel.py の /api/intel/reform/*

import type {
  ReformAction,
  ActionStatus,
  ActionPriorityLevel,
  KPISnapshot,
  WeeklyAgendaItem,
} from './reform-types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'https://kessho-lens-backend.onrender.com';

async function request<T>(
  path: string,
  init?: RequestInit,
  attempt = 0,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: 'no-store',
    headers: init?.body ? { 'Content-Type': 'application/json' } : undefined,
    ...init,
  });
  // Render 無料/起動直後の 5xx はリトライ (intel-api.ts と同じ方針)
  if (res.status >= 500 && attempt < 3 && (!init || init.method === undefined)) {
    await new Promise(r => setTimeout(r, 6_000));
    return request<T>(path, init, attempt + 1);
  }
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ─── Actions ───────────────────────────────────────────────────────────

export async function fetchReformActions(): Promise<ReformAction[]> {
  const res = await request<{ actions: ReformAction[] }>('/api/intel/reform/actions');
  return res.actions;
}

export interface CreateActionInput {
  title: string;
  owner: string;
  deadline: string;
  priority?: ActionPriorityLevel;
  status?: ActionStatus;
  memo?: string;
  card_id?: string;
  linked_kpi_ids?: string[];
  next_review_date?: string;
}

export async function createReformAction(
  input: CreateActionInput,
): Promise<ReformAction> {
  const res = await request<{ action: ReformAction }>(
    '/api/intel/reform/actions',
    { method: 'POST', body: JSON.stringify(input) },
  );
  return res.action;
}

export async function updateReformAction(
  id: string,
  patch: Partial<Omit<ReformAction, 'id' | 'created_at' | 'updated_at'>>,
): Promise<ReformAction> {
  const res = await request<{ action: ReformAction }>(
    `/api/intel/reform/actions/${id}`,
    { method: 'PATCH', body: JSON.stringify(patch) },
  );
  return res.action;
}

export async function deleteReformAction(id: string): Promise<void> {
  await request(`/api/intel/reform/actions/${id}`, { method: 'DELETE' });
}

// ─── KPI Snapshots ─────────────────────────────────────────────────────

export async function fetchKpiSnapshots(): Promise<KPISnapshot[]> {
  const res = await request<{ snapshots: KPISnapshot[] }>('/api/intel/reform/kpis');
  return res.snapshots;
}

export interface UpsertKpiInput {
  value: number;
  target?: number;
  period: string;
  delta_vs_prev?: number;
  status?: KPISnapshot['status'];
}

export async function upsertKpiSnapshot(
  kpiId: string,
  input: UpsertKpiInput,
): Promise<KPISnapshot> {
  const res = await request<{ snapshot: KPISnapshot }>(
    `/api/intel/reform/kpis/${kpiId}`,
    { method: 'PUT', body: JSON.stringify(input) },
  );
  return res.snapshot;
}

// ─── Weekly Agenda ─────────────────────────────────────────────────────

export interface WeeklyAgenda {
  week_of: string;
  items: WeeklyAgendaItem[];
  source: string;
  saved_at?: string;
}

export async function fetchWeeklyAgenda(
  weekOf?: string,
): Promise<WeeklyAgenda | null> {
  const qs = weekOf ? `?week_of=${weekOf}` : '';
  const res = await request<{ agenda: WeeklyAgenda | null }>(
    `/api/intel/reform/agenda${qs}`,
  );
  return res.agenda;
}

export async function saveWeeklyAgenda(
  weekOf: string,
  items: WeeklyAgendaItem[],
  source: 'manual' | 'signals' | 'llm' = 'signals',
): Promise<WeeklyAgenda> {
  const res = await request<{ agenda: WeeklyAgenda }>(
    '/api/intel/reform/agenda',
    { method: 'POST', body: JSON.stringify({ week_of: weekOf, items, source }) },
  );
  return res.agenda;
}
