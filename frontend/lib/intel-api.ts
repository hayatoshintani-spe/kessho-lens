// Tsuburaya Intelligence Brief API クライアント

import type {
  IntelCard,
  DailyBrief,
  BriefSummary,
  CouncilSession,
  IntelMeta,
  CategoryWatchlist,
  IntelCategory,
  Importance,
} from './intel-types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'https://kessho-lens-backend.onrender.com';

async function get<T>(path: string, attempt = 0): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
  if (res.status >= 500 && attempt < 4) {
    await new Promise(r => setTimeout(r, 6_000));
    return get<T>(path, attempt + 1);
  }
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ─── Cards ─────────────────────────────────────────────────────────────

export async function fetchIntelCards(opts?: {
  category?: IntelCategory;
  importance?: Importance;
  limit?: number;
}): Promise<IntelCard[]> {
  const params = new URLSearchParams();
  if (opts?.category) params.set('category', opts.category);
  if (opts?.importance) params.set('importance', opts.importance);
  if (opts?.limit) params.set('limit', String(opts.limit));
  const qs = params.toString();
  const res = await get<{ cards: IntelCard[] }>(`/api/intel/cards${qs ? `?${qs}` : ''}`);
  return res.cards;
}

export async function fetchIntelCard(id: string): Promise<IntelCard> {
  const res = await get<{ card: IntelCard }>(`/api/intel/cards/${id}`);
  return res.card;
}

export interface CreateCardInput {
  title: string;
  url?: string;
  publisher?: string;
  summary?: string;
  user_note?: string;
  access_status?: 'full' | 'title_only' | 'paywalled' | 'estimated';
  category?: IntelCategory;
  importance?: Importance;
  date?: string;
}

export async function createIntelCard(input: CreateCardInput): Promise<IntelCard> {
  const res = await post<{ card: IntelCard }>('/api/intel/cards', input);
  return res.card;
}

// ─── Briefs ────────────────────────────────────────────────────────────

export async function fetchBriefs(): Promise<BriefSummary[]> {
  const res = await get<{ briefs: BriefSummary[] }>('/api/intel/briefs');
  return res.briefs;
}

export async function fetchDailyBrief(date: string): Promise<{
  brief: DailyBrief;
  top_cards: IntelCard[];
  council: CouncilSession | null;
}> {
  return get<{
    brief: DailyBrief;
    top_cards: IntelCard[];
    council: CouncilSession | null;
  }>(`/api/intel/briefs/daily/${date}`);
}

export async function buildDailyBrief(opts: {
  date: string;
  generate_council?: boolean;
  council_topic?: string;
}): Promise<{ brief: DailyBrief; council_session_id?: string }> {
  return post('/api/intel/briefs/daily/build', opts);
}

// ─── Council ───────────────────────────────────────────────────────────

export async function fetchCouncilSessions(): Promise<CouncilSession[]> {
  const res = await get<{ sessions: CouncilSession[] }>('/api/intel/council');
  return res.sessions;
}

export async function fetchCouncilSession(id: string): Promise<{
  session: CouncilSession;
  related_cards: IntelCard[];
}> {
  return get<{ session: CouncilSession; related_cards: IntelCard[] }>(
    `/api/intel/council/${id}`,
  );
}

export async function createCouncilSession(input: {
  topic: string;
  card_ids?: string[];
  date?: string;
}): Promise<CouncilSession> {
  const res = await post<{ session: CouncilSession }>('/api/intel/council', input);
  return res.session;
}

// ─── Meta / Watchlist ──────────────────────────────────────────────────

export async function fetchIntelMeta(): Promise<IntelMeta> {
  return get<IntelMeta>('/api/intel/meta');
}

export async function fetchWatchlists(): Promise<CategoryWatchlist[]> {
  const res = await get<{ watchlists: CategoryWatchlist[] }>('/api/intel/watchlist');
  return res.watchlists;
}

// ─── Notion ────────────────────────────────────────────────────────────

export interface NotionStatus {
  enabled: boolean;
  has_api_key: boolean;
  has_db_id: boolean;
  db_id: string | null;
  db: {
    title?: string;
    url?: string;
    properties?: string[];
    error?: string;
  };
}

export interface NotionSyncResult {
  action: 'created' | 'updated' | 'skipped' | 'error';
  page_id: string | null;
  url: string | null;
  error: string | null;
}

export async function fetchNotionStatus(): Promise<NotionStatus> {
  return get<NotionStatus>('/api/intel/notion/status');
}

export async function syncCardToNotion(cardId: string): Promise<{
  mode: 'single';
  result: NotionSyncResult;
}> {
  return post('/api/intel/notion/sync', { card_id: cardId });
}

export async function syncAllCardsToNotion(): Promise<{
  mode: 'all';
  result: {
    created: number;
    updated: number;
    skipped: number;
    errors: Array<{ card_id?: string; error?: string } | string>;
  };
}> {
  return post('/api/intel/notion/sync', {});
}

export async function setupNotionDatabase(
  parentPageId: string,
): Promise<{
  database_id?: string;
  url?: string;
  message?: string;
  error?: string;
}> {
  return post('/api/intel/notion/setup', { parent_page_id: parentPageId });
}

// ─── Email Delivery ──────────────────────────────────────────────────────

export interface EmailDeliveryStatus {
  enabled: boolean;
  has_api_key: boolean;
  from: string | null;
  recipients: string[];
  recipient_count: number;
  frontend_url: string;
  timezone: string;
}

export type EmailSendStatus = 'sent' | 'skipped' | 'error' | 'dry_run';

export interface EmailSendResult {
  status: EmailSendStatus;
  message_id?: string;
  recipients?: string[];
  subject?: string;
  reason?: string;
  error?: string;
  html_preview?: string;
  text_preview?: string;
}

export async function fetchEmailStatus(): Promise<EmailDeliveryStatus> {
  return get<EmailDeliveryStatus>('/api/intel/email/status');
}

export async function sendTestEmail(input: {
  date?: string;
  recipients?: string[];
  dry_run?: boolean;
}): Promise<{ date: string; result: EmailSendResult }> {
  return post('/api/intel/email/test', input);
}
