import type {
  Agent,
  AgentId,
  MeetingLog,
  DailyReport,
  DiscoveryEntry,
  PerformanceDataPoint,
  FundStats,
  PaginatedResponse,
} from './types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

// ─── HTTP helpers ─────────────────────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate: 60 }, // ISR: revalidate every 60s
    headers: { 'Content-Type': 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

// ─── Fund / Overview ──────────────────────────────────────────────────────────

export async function fetchFundStats(): Promise<FundStats> {
  return get<FundStats>('/api/fund/stats');
}

export async function fetchPerformance(days = 30): Promise<PerformanceDataPoint[]> {
  return get<PerformanceDataPoint[]>(`/api/fund/performance?days=${days}`);
}

// ─── Agents ───────────────────────────────────────────────────────────────────

export async function fetchAgents(): Promise<Agent[]> {
  return get<Agent[]>('/api/agents');
}

export async function fetchAgent(id: AgentId): Promise<Agent> {
  return get<Agent>(`/api/agents/${id}`);
}

export async function fetchAgentPerformance(
  id: AgentId,
  days = 30,
): Promise<PerformanceDataPoint[]> {
  return get<PerformanceDataPoint[]>(
    `/api/agents/${id}/performance?days=${days}`,
  );
}

// ─── Meetings ────────────────────────────────────────────────────────────────

export async function fetchMeetings(
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<MeetingLog>> {
  return get<PaginatedResponse<MeetingLog>>(
    `/api/meetings?page=${page}&page_size=${pageSize}`,
  );
}

export async function fetchMeeting(date: string): Promise<MeetingLog> {
  return get<MeetingLog>(`/api/meetings/${date}`);
}

export async function fetchLatestMeeting(): Promise<MeetingLog> {
  return get<MeetingLog>('/api/meetings/latest');
}

// ─── Reports ─────────────────────────────────────────────────────────────────

export async function fetchReports(
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<DailyReport>> {
  return get<PaginatedResponse<DailyReport>>(
    `/api/reports?page=${page}&page_size=${pageSize}`,
  );
}

export async function fetchReport(date: string): Promise<DailyReport> {
  return get<DailyReport>(`/api/reports/${date}`);
}

export async function fetchLatestReport(): Promise<DailyReport> {
  return get<DailyReport>('/api/reports/latest');
}

// ─── Discovery ────────────────────────────────────────────────────────────────

export async function fetchDiscoveries(
  page = 1,
  pageSize = 50,
): Promise<PaginatedResponse<DiscoveryEntry>> {
  return get<PaginatedResponse<DiscoveryEntry>>(
    `/api/discovery?page=${page}&page_size=${pageSize}`,
  );
}

export async function fetchDiscoveriesByAgent(
  agentId: AgentId,
): Promise<DiscoveryEntry[]> {
  return get<DiscoveryEntry[]>(`/api/discovery?agent=${agentId}`);
}

// ─── Simulation / Cron ───────────────────────────────────────────────────────

export async function triggerDailySimulation(
  secret: string,
): Promise<{ message: string; date: string }> {
  return post<{ message: string; date: string }>('/api/cron/run-daily', {
    secret,
  });
}

export async function fetchSimulationStatus(): Promise<{
  running: boolean;
  lastRun: string | null;
  nextRun: string | null;
}> {
  return get('/api/cron/status');
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  return get('/api/health');
}
