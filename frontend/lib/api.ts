import type {
  Agent,
  AgentId,
  MeetingLog,
  MessageType,
  DailyReport,
  DiscoveryEntry,
  DiscoveryStatus,
  PerformanceDataPoint,
  FundStats,
  PaginatedResponse,
  Portfolio,
  Holding,
  AgentSummary,
} from './types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'https://kessho-lens-backend.onrender.com';

// ─── HTTP helpers ─────────────────────────────────────────────────────────────

async function get<T>(path: string, attempt = 0): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
  // Render free tier returns 5xx while cold-starting (~50s). Retry up to 4 times with 8s gaps.
  if (res.status >= 500 && attempt < 4) {
    await new Promise(r => setTimeout(r, 8_000));
    return get<T>(path, attempt + 1);
  }
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// Poll /api/health until it returns 200 or we give up after maxMs milliseconds.
// This warms up Render's free-tier container before making actual data requests.
export async function warmupBackend(maxMs = 70_000): Promise<boolean> {
  const deadline = Date.now() + maxMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
      if (res.ok) return true;
    } catch {
      // network error — keep waiting
    }
    const remaining = deadline - Date.now();
    if (remaining <= 0) break;
    await new Promise(r => setTimeout(r, Math.min(5_000, remaining)));
  }
  return false;
}

async function post<T>(path: string, body?: unknown, secret?: string): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (secret) headers['Authorization'] = `Bearer ${secret}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ─── Adapters: backend snake_case → frontend camelCase ────────────────────────

const KNOWN_AGENT_IDS: AgentId[] = ['buffett', 'soros', 'lynch', 'flat'];

const AGENT_COLOR_MAP: Record<AgentId, string> = {
  buffett: '#4CAF50',
  soros: '#E91E63',
  lynch: '#2196F3',
  flat: '#9E9E9E',
};

const AGENT_NAME_JA: Record<AgentId, string> = {
  buffett: 'バフェットAI',
  soros: 'ソロスAI',
  lynch: 'リンチAI',
  flat: 'フラットAI',
};

function isAgentId(v: string): v is AgentId {
  return KNOWN_AGENT_IDS.includes(v as AgentId);
}

function toHolding(h: Record<string, unknown>): Holding {
  const shares = Number(h.shares ?? 0);
  const avgCost = Number(h.avg_cost ?? h.avgCost ?? 0);
  const currentPrice = Number(h.current_price ?? h.currentPrice ?? 0);
  const value = Number(h.value ?? shares * currentPrice);
  const cost = shares * avgCost;
  const pnl = value - cost;
  const pnlPct = cost > 0 ? (pnl / cost) * 100 : 0;
  return {
    ticker: String(h.ticker ?? h.symbol ?? ''),
    name: String(h.name ?? ''),
    shares,
    avgCost,
    currentPrice,
    unrealizedPnL: pnl,
    unrealizedPnLPct: Number(h.gain_pct ?? pnlPct),
    weight: 0,
  };
}

function toPortfolio(p: Record<string, unknown> | undefined | null): Portfolio {
  if (!p) return { totalValue: 0, cash: 0, holdings: [] };
  const totalValue = Number(p.total_value ?? p.totalValue ?? 0);
  const cash = Number(p.cash ?? 0);
  const rawHoldings = (p.holdings as Record<string, unknown>[] | undefined) ?? [];
  const holdings = rawHoldings.map(toHolding);
  const equityValue = holdings.reduce((s, h) => s + h.shares * h.currentPrice, 0);
  const basis = equityValue + cash;
  for (const h of holdings) {
    h.weight = basis > 0 ? ((h.shares * h.currentPrice) / basis) * 100 : 0;
  }
  return { totalValue, cash, holdings };
}

function deriveBeliefs(d: Record<string, unknown>): string[] {
  const quotes = (d.famous_quotes as string[] | undefined) ?? [];
  if (quotes.length) return quotes.slice(0, 4);
  const tags = (d.style_tags as string[] | undefined) ?? [];
  return tags;
}

function adaptAgentListItem(raw: Record<string, unknown>, rankMap?: Map<string, number>): Agent {
  const id = String(raw.id ?? '');
  const agentId: AgentId = isAgentId(id) ? id : 'flat';
  const portfolio = toPortfolio(raw.portfolio as Record<string, unknown> | undefined);
  const perf = ((raw.portfolio as Record<string, unknown> | undefined)?.performance as
    | Record<string, unknown>
    | undefined) ?? (raw.performance as Record<string, unknown> | undefined);
  const totalReturn = Number(perf?.total_return_pct ?? 0);
  const totalReturnAbs = Number(perf?.daily_pnl ?? 0);
  return {
    id: agentId,
    name: String(raw.display_name ?? raw.full_name ?? agentId),
    nameJa: AGENT_NAME_JA[agentId],
    personality: String(raw.bio_ja ?? raw.catchphrase ?? ''),
    style: String(raw.style ?? ''),
    color: String(raw.color ?? AGENT_COLOR_MAP[agentId]),
    portfolio,
    totalReturn,
    totalReturnAbs,
    rank: rankMap?.get(agentId) ?? 0,
    beliefs: deriveBeliefs(raw),
    recentDecision: (() => {
      const msgs = raw.recent_messages as Array<Record<string, unknown>> | undefined;
      return msgs && msgs[0] ? String(msgs[0].content) : undefined;
    })(),
  };
}

function adaptMeeting(raw: Record<string, unknown>): MeetingLog {
  const participants = ((raw.participants as string[] | undefined) ?? []).map((p) => {
    const lower = p.toLowerCase().replace(/ai$/, '');
    return isAgentId(lower) ? lower : (p as AgentId);
  });
  const messagesRaw = (raw.messages as Array<Record<string, unknown>> | undefined) ?? [];
  const messages = messagesRaw.map((m) => {
    const rawAgent = String(m.agent ?? '').toLowerCase().replace(/ai$/, '');
    const agent: AgentId = isAgentId(rawAgent) ? rawAgent : 'flat';
    return {
      agent,
      time: String(m.time ?? ''),
      content: String(m.content ?? ''),
      type: (m.type as MessageType) ?? 'debate',
    };
  });
  return {
    date: String(raw.date ?? ''),
    participants: participants as AgentId[],
    summary: String(raw.summary ?? ''),
    keyDecisions: (raw.key_decisions as string[] | undefined) ?? (raw.keyDecisions as string[] | undefined) ?? [],
    marketTheme: String(raw.market_theme ?? raw.marketTheme ?? ''),
    messages,
  };
}

function adaptReport(raw: Record<string, unknown>): DailyReport {
  const summariesRaw = (raw.agent_summaries ?? raw.agentSummaries ?? {}) as Record<string, unknown>;
  const agentSummaries = {} as Record<AgentId, AgentSummary>;
  for (const id of KNOWN_AGENT_IDS) {
    const v = summariesRaw[id];
    if (typeof v === 'string') {
      agentSummaries[id] = { agentId: id, summary: v, decisions: [], pnlChange: 0 };
    } else if (v && typeof v === 'object') {
      const obj = v as Record<string, unknown>;
      agentSummaries[id] = {
        agentId: id,
        summary: String(obj.summary ?? ''),
        decisions: (obj.decisions as string[] | undefined) ?? [],
        pnlChange: Number(obj.pnl_change ?? obj.pnlChange ?? 0),
      };
    } else {
      agentSummaries[id] = { agentId: id, summary: '', decisions: [], pnlChange: 0 };
    }
  }
  return {
    date: String(raw.date ?? ''),
    title: String(raw.title ?? ''),
    content: String(raw.content ?? ''),
    agentSummaries,
    totalFundReturn: Number(raw.total_fund_return ?? raw.totalFundReturn ?? 0),
    marketTheme: String(raw.market_theme ?? raw.marketTheme ?? ''),
  };
}

function adaptDiscovery(raw: Record<string, unknown>): DiscoveryEntry {
  const action = String(raw.action ?? '');
  let status: DiscoveryStatus = 'scanning';
  if (action.includes('保有') || action.includes('購入') || action.includes('投資') || action.includes('積立')) status = 'found';
  else if (action.includes('ウォッチ') || action.includes('注視') || action.includes('調査') || action.includes('候補')) status = 'watchlist';
  else if (action.includes('却下') || action.includes('見送り')) status = 'rejected';
  const rawAgent = String(raw.agent_id ?? raw.agentId ?? 'flat').toLowerCase();
  const agentId: AgentId = isAgentId(rawAgent) ? rawAgent : 'flat';
  const confidence = Number(raw.confidence ?? 0);
  const score = confidence > 0 && confidence <= 1 ? Math.round(confidence * 100) : Number(raw.score ?? 50);
  return {
    id: `${raw.date ?? ''}-${rawAgent}-${raw.ticker ?? raw.symbol ?? Math.random()}`,
    date: String(raw.date ?? ''),
    ticker: String(raw.ticker ?? raw.symbol ?? ''),
    name: String(raw.name ?? ''),
    agentId,
    reason: String(raw.discovery_reason ?? raw.reason ?? ''),
    score,
    status,
    sector: raw.criteria ? String(raw.criteria) : undefined,
    priceAtDiscovery: raw.price_at_discovery !== undefined ? Number(raw.price_at_discovery) : undefined,
  };
}

// ─── Public API ───────────────────────────────────────────────────────────────

interface DashboardResponse {
  timestamp: string;
  agents: Array<Record<string, unknown>>;
  rankings: Array<{ agent_id: string; rank: number }>;
  history_chart: {
    dates: string[];
    series: Record<string, { data: number[] }>;
  };
}

async function getDashboard(): Promise<DashboardResponse> {
  return get<DashboardResponse>('/api/dashboard');
}

// ─── Fund / Overview ──────────────────────────────────────────────────────────

export async function fetchFundStats(): Promise<FundStats> {
  const d = await getDashboard();
  const totalAum = d.agents.reduce((s, a) => s + Number(a.total_value ?? 0), 0);
  const totalReturn =
    d.agents.reduce((s, a) => {
      const p = a.performance as Record<string, unknown> | undefined;
      return s + Number(p?.total_return_pct ?? 0);
    }, 0) / Math.max(d.agents.length, 1);
  const sortedByReturn = [...d.agents].sort((a, b) => {
    const ar = ((a.performance as Record<string, unknown>)?.total_return_pct ?? 0) as number;
    const br = ((b.performance as Record<string, unknown>)?.total_return_pct ?? 0) as number;
    return br - ar;
  });
  const bestId = String(sortedByReturn[0]?.id ?? 'soros');
  const worstId = String(sortedByReturn[sortedByReturn.length - 1]?.id ?? 'flat');
  return {
    totalAum,
    inception: '2026-01-01',
    totalReturn,
    bestAgent: isAgentId(bestId) ? bestId : 'soros',
    worstAgent: isAgentId(worstId) ? worstId : 'flat',
    lastUpdated: d.timestamp,
  };
}

export async function fetchPerformance(days = 30): Promise<PerformanceDataPoint[]> {
  const d = await getDashboard();
  const { dates, series } = d.history_chart;
  const sliceCount = Math.min(days, dates.length);
  const start = dates.length - sliceCount;
  const out: PerformanceDataPoint[] = [];
  for (let i = start; i < dates.length; i++) {
    out.push({
      date: dates[i],
      buffett: series.buffett?.data[i] ?? 0,
      soros: series.soros?.data[i] ?? 0,
      lynch: series.lynch?.data[i] ?? 0,
      flat: series.flat?.data[i] ?? 0,
    });
  }
  return out;
}

// ─── Agents ───────────────────────────────────────────────────────────────────

export async function fetchAgents(): Promise<Agent[]> {
  const [list, dashboard] = await Promise.all([
    get<{ agents: Array<Record<string, unknown>> }>('/api/agents'),
    getDashboard().catch(() => null),
  ]);
  const rankMap = new Map<string, number>();
  if (dashboard) for (const r of dashboard.rankings) rankMap.set(r.agent_id, r.rank);
  // The list endpoint returns lightweight items; merge with dashboard agent data for richer fields
  return list.agents.map((raw) => {
    const id = String(raw.id ?? '');
    const dashAgent = dashboard?.agents.find((a) => String(a.id) === id);
    const merged = { ...raw, ...(dashAgent ?? {}) };
    return adaptAgentListItem(merged, rankMap);
  });
}

export async function fetchAgent(id: AgentId): Promise<Agent> {
  const detail = await get<Record<string, unknown>>(`/api/agents/${id}`);
  return adaptAgentListItem(detail);
}

export async function fetchAgentPerformance(_id: AgentId, days = 30): Promise<PerformanceDataPoint[]> {
  return fetchPerformance(days);
}

// ─── Meetings ────────────────────────────────────────────────────────────────

export async function fetchMeetings(page = 1, pageSize = 20): Promise<PaginatedResponse<MeetingLog>> {
  const res = await get<{ meetings: Array<Record<string, unknown>>; count: number }>('/api/meetings');
  const all = res.meetings.map(adaptMeeting);
  const start = (page - 1) * pageSize;
  return {
    items: all.slice(start, start + pageSize),
    total: all.length,
    page,
    pageSize,
  };
}

export async function fetchMeeting(date: string): Promise<MeetingLog> {
  const res = await get<{ meeting: Record<string, unknown> }>(`/api/meetings/${date}`);
  return adaptMeeting(res.meeting);
}

export async function fetchLatestMeeting(): Promise<MeetingLog> {
  const res = await get<{ meetings: Array<Record<string, unknown>> }>('/api/meetings');
  if (!res.meetings.length) throw new Error('No meetings available');
  const latestDate = String(res.meetings[0].date);
  return fetchMeeting(latestDate);
}

// ─── Reports ─────────────────────────────────────────────────────────────────

export async function fetchReports(page = 1, pageSize = 20): Promise<PaginatedResponse<DailyReport>> {
  const res = await get<{ reports: Array<Record<string, unknown>> }>('/api/reports');
  const all = res.reports.map(adaptReport);
  const start = (page - 1) * pageSize;
  return {
    items: all.slice(start, start + pageSize),
    total: all.length,
    page,
    pageSize,
  };
}

export async function fetchReport(date: string): Promise<DailyReport> {
  const res = await get<{ report: Record<string, unknown> }>(`/api/reports/${date}`);
  return adaptReport(res.report);
}

export async function fetchLatestReport(): Promise<DailyReport> {
  const res = await get<{ reports: Array<Record<string, unknown>> }>('/api/reports');
  if (!res.reports.length) throw new Error('No reports available');
  const latestDate = String(res.reports[0].date);
  return fetchReport(latestDate);
}

// ─── Discovery ────────────────────────────────────────────────────────────────

export async function fetchDiscoveries(
  page = 1,
  pageSize = 50,
): Promise<PaginatedResponse<DiscoveryEntry>> {
  const res = await get<{ discoveries: Array<Record<string, unknown>> }>('/api/discovery');
  const all = res.discoveries.map(adaptDiscovery);
  const start = (page - 1) * pageSize;
  return {
    items: all.slice(start, start + pageSize),
    total: all.length,
    page,
    pageSize,
  };
}

export async function fetchDiscoveriesByAgent(agentId: AgentId): Promise<DiscoveryEntry[]> {
  const res = await get<{ discoveries: Array<Record<string, unknown>> }>(
    `/api/discovery?agent_id=${agentId}`,
  );
  return res.discoveries.map(adaptDiscovery);
}

// ─── Simulation / Cron ───────────────────────────────────────────────────────

export async function triggerDailySimulation(
  secret: string,
): Promise<{ message: string; date: string }> {
  return post<{ message: string; date: string }>('/api/cron/run-daily', undefined, secret);
}

export async function runDailyNow(): Promise<{ message: string; date: string }> {
  return post<{ message: string; date: string }>('/api/run-daily');
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  return get('/api/health');
}

// ─── Advisor ──────────────────────────────────────────────────────────────────

export type AdvisorPeriod = 'short' | 'medium' | 'long';
export type AdvisorRisk = 'low' | 'medium' | 'high';

export async function fetchAdvisorDebate(
  amount: number,
  period: AdvisorPeriod,
  risk: AdvisorRisk,
): Promise<MeetingLog> {
  const raw = await post<Record<string, unknown>>('/api/advisor', { amount, period, risk });
  return adaptMeeting(raw);
}
