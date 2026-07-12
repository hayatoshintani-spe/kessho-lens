'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  Sparkles,
  AlertTriangle,
  RefreshCw,
  Lightbulb,
  ShieldAlert,
  Clock4,
  CheckSquare,
  Target,
  Compass,
  ListChecks,
  Calendar,
} from 'lucide-react';
import {
  fetchIntelCards,
  fetchBriefs,
  fetchDailyBrief,
} from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import CardItem from '@/components/intel/CardItem';
import ImpactScoreBadge from '@/components/intel/ImpactScoreBadge';
import ThemeChip from '@/components/intel/ThemeChip';
import type {
  IntelCard,
  DailyBrief,
  BriefSummary,
  CouncilSession,
} from '@/lib/intel-types';
import { enrichCards } from '@/lib/impact-score';
import type { ReformAction, ThemeId } from '@/lib/reform-types';
import { ACTION_STATUS_LABELS, ACTION_STATUS_COLORS } from '@/lib/reform-types';
import { fetchReformActions } from '@/lib/reform-api';
import { THEMES, THEMES_BY_GROUP, THEME_GROUPS } from '@/lib/reform-taxonomies';

const TODAY = new Date().toISOString().slice(0, 10);

export default function IntelIndexPage() {
  const [todayBrief, setTodayBrief] = useState<DailyBrief | null>(null);
  const [topCards, setTopCards] = useState<IntelCard[]>([]);
  const [recentBriefs, setRecentBriefs] = useState<BriefSummary[]>([]);
  const [council, setCouncil] = useState<CouncilSession | null>(null);
  const [recentCards, setRecentCards] = useState<IntelCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMsg, setRefreshMsg] = useState<string | null>(null);
  const [actions, setActions] = useState<ReformAction[]>([]);

  async function handleRefreshNow() {
    if (isRefreshing) return;
    // 暴走課金防止: 明示確認(Anthropic API を消費するため)
    const ok = window.confirm(
      '最新ニュースを取得し、ブリーフ生成・メール配信・Notion 保存まで実行します。\n'
      + 'Anthropic API トークンを消費します(目安: 1回 ¥10〜30)。\n'
      + '実行しますか?',
    );
    if (!ok) return;
    setIsRefreshing(true);
    setRefreshMsg('起動中…');
    try {
      const startRes = await fetch('/api/intel/refresh-today', { method: 'POST' });
      const startData = await startRes.json();
      if (!startRes.ok) {
        setRefreshMsg(`更新に失敗: ${startData.error ?? startData.details?.detail ?? startRes.statusText}`);
        setIsRefreshing(false);
        return;
      }
      if (typeof startData.runs_remaining_24h === 'number') {
        setRefreshMsg(
          `起動済 (24h内 残り ${startData.runs_remaining_24h}/${startData.daily_limit} 回)`,
        );
      }
      const deadline = Date.now() + 180_000;
      const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
      while (Date.now() < deadline) {
        await new Promise(r => setTimeout(r, 4_000));
        try {
          const sRes = await fetch(`${apiBase}/api/intel/cron/status`, {
            cache: 'no-store',
          });
          if (!sRes.ok) continue;
          const s = await sRes.json();
          if (s.state === 'running') {
            setRefreshMsg(`実行中: ${s.message ?? ''}`);
            continue;
          }
          if (s.state === 'skipped') {
            setRefreshMsg(`取得できる新規ニュースがありませんでした (${s.date})`);
            setIsRefreshing(false);
            return;
          }
          if (s.state === 'done') {
            const ingested = s.ingest?.created ?? 0;
            const sent = s.email?.status === 'sent' ? '配信済み' : '配信スキップ';
            setRefreshMsg(`✅ 完了: ${ingested}件取得、${sent}。3秒後に再読み込みします`);
            setTimeout(() => window.location.reload(), 3000);
            return;
          }
          if (s.state === 'error') {
            setRefreshMsg(`更新に失敗: ${s.message ?? '不明なエラー'}`);
            setIsRefreshing(false);
            return;
          }
        } catch {/* ignore */}
      }
      setRefreshMsg('タイムアウト(3分)。完了している可能性があるので画面を再読み込みしてください');
    } catch (e) {
      setRefreshMsg(`更新に失敗: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setIsRefreshing(false);
    }
  }

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setErrorMsg('バックエンドに接続できません');
        setIsLoading(false);
        return;
      }
      try {
        const briefs = await fetchBriefs();
        setRecentBriefs(briefs);
        if (briefs.length > 0) {
          const latest = briefs[0];
          const detail = await fetchDailyBrief(latest.date);
          setTodayBrief(detail.brief);
          setTopCards(detail.top_cards);
          setCouncil(detail.council);
        }
        const allCards = await fetchIntelCards({ limit: 60 });
        setRecentCards(allCards);
        // アクションは補助情報なので取得失敗してもダッシュボード全体は落とさない
        try {
          setActions(await fetchReformActions());
        } catch {/* ignore */}
      } catch (e) {
        setErrorMsg((e as Error).message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  // 経営改革ダッシュボード集計
  const dashboard = useMemo(() => {
    const enriched = enrichCards(recentCards);
    const sorted = [...enriched].sort((a, b) => b.impact.score - a.impact.score);
    const importantSignals = sorted.slice(0, 4);
    const boardDiscussion = enriched
      .filter(e => e.impact.recommendation === 'next_board_meeting')
      .slice(0, 4);
    const opportunities = enriched
      .filter(e => (e.card.insight?.business_opportunity?.length ?? 0) >= 1)
      .sort((a, b) =>
        (b.card.insight?.business_opportunity?.length ?? 0) -
        (a.card.insight?.business_opportunity?.length ?? 0),
      )
      .slice(0, 4);
    const risks = enriched
      .filter(e =>
        (e.card.insight?.risk?.length ?? 0) >= 1 ||
        e.impact.components.risk >= 60,
      )
      .sort((a, b) => b.impact.components.risk - a.impact.components.risk)
      .slice(0, 4);
    // テーマ別シグナル数
    const themeFreq: Record<string, number> = {};
    enriched.forEach(e => e.themes.forEach(t => {
      themeFreq[t] = (themeFreq[t] ?? 0) + 1;
    }));
    const weeklyPriorityThemes = Object.entries(themeFreq)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([t]) => t as ThemeId);

    const delayedActions = actions
      .filter(a =>
        a.status !== 'done' && a.status !== 'on_hold' &&
        a.deadline < TODAY,
      )
      .sort((a, b) => a.deadline.localeCompare(b.deadline));
    const pendingDecisions = actions
      .filter(a => a.status === 'awaiting_review')
      .sort((a, b) => a.deadline.localeCompare(b.deadline));
    const inProgress = actions.filter(a => a.status === 'in_progress');
    const inProgressThemeIds: ThemeId[] = Array.from(
      new Set(inProgress.flatMap(() => weeklyPriorityThemes.slice(0, 3))),
    ).slice(0, 4);

    return {
      importantSignals,
      boardDiscussion,
      opportunities,
      risks,
      delayedActions,
      pendingDecisions,
      weeklyPriorityThemes,
      inProgressThemeIds,
    };
  }, [recentCards, actions]);

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      {/* Page header */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-1">
          <div>
            <div className="text-accent-gold text-[10px] font-mono uppercase tracking-wider">
              Reform Operating Dashboard
            </div>
            <h1 className="text-text-primary text-xl font-bold mt-0.5">
              今日見るべき経営改革ダッシュボード
            </h1>
          </div>
          <button
            type="button"
            onClick={handleRefreshNow}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/10 disabled:opacity-50 disabled:cursor-not-allowed transition"
            title="最新ニュースを取得してブリーフ生成・配信・Notion保存まで実行"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? '更新中…' : '今すぐ更新'}
          </button>
        </div>
        <p className="text-text-muted text-sm">
          外部変化を、経営改革の論点・打ち手・KPI・実行計画に変換する AI 経営 OS
        </p>
        {refreshMsg && (
          <div className="mt-2 text-xs text-text-muted">{refreshMsg}</div>
        )}
      </div>

      {errorMsg && (
        <div className="card p-4 border-loss/40 bg-loss/5">
          <div className="flex items-center gap-2 text-loss text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>{errorMsg}</span>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="card p-8 text-center text-text-muted text-sm">
          読み込み中...
        </div>
      ) : (
        <>
          {/* ── 上段: 本日見るべき重要シグナル ────────────────────────── */}
          <DashboardSection
            title="本日見るべき重要シグナル"
            subtitle="経営インパクトスコア順"
            icon={<Sparkles className="w-4 h-4 text-accent-gold" />}
            link={{ href: '/intel/cards', label: '全カード' }}
          >
            {dashboard.importantSignals.length === 0 ? (
              <EmptyHint text="シグナルがまだありません" />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {dashboard.importantSignals.map(s => (
                  <CardItem key={s.card.id} card={s.card} />
                ))}
              </div>
            )}
          </DashboardSection>

          {/* ── 中段: 4 カラムサマリ ──────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 経営会議で扱うべき論点 */}
            <SummaryCard
              title="経営会議で扱うべき論点"
              icon={<Compass className="w-4 h-4" />}
              link={{ href: '/intel/agenda', label: 'アジェンダ生成' }}
              accent="#C8860A"
            >
              {dashboard.boardDiscussion.length === 0 ? (
                <EmptyHint text="該当する論点はありません" />
              ) : (
                <ul className="space-y-2">
                  {dashboard.boardDiscussion.slice(0, 3).map(d => (
                    <li key={d.card.id}>
                      <Link
                        href={`/intel/cards/${d.card.id}`}
                        className="flex items-start gap-2 text-xs hover:text-accent-gold"
                      >
                        <ImpactScoreBadge impact={d.impact} size="sm" />
                        <div className="min-w-0 flex-1">
                          <div className="text-text-primary line-clamp-2">
                            {d.card.title}
                          </div>
                          <div className="text-text-muted text-[10px] mt-0.5 line-clamp-1">
                            {d.card.one_liner}
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </SummaryCard>

            {/* 新規事業機会 */}
            <SummaryCard
              title="新規の事業機会"
              icon={<Lightbulb className="w-4 h-4" />}
              link={{ href: '/intel/themes', label: '経営課題マップ' }}
              accent="#1D9E75"
            >
              {dashboard.opportunities.length === 0 ? (
                <EmptyHint text="事業機会の抽出待ち" />
              ) : (
                <ul className="space-y-2">
                  {dashboard.opportunities.slice(0, 3).map(d => (
                    <li key={d.card.id} className="text-xs">
                      <Link
                        href={`/intel/cards/${d.card.id}`}
                        className="block hover:text-accent-gold"
                      >
                        <div className="text-text-primary font-medium line-clamp-1">
                          {d.card.title}
                        </div>
                        <div className="text-text-muted text-[10px] mt-0.5 line-clamp-2">
                          💡 {d.card.insight?.business_opportunity?.[0] ?? ''}
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </SummaryCard>

            {/* 重要リスク */}
            <SummaryCard
              title="重要リスク"
              icon={<ShieldAlert className="w-4 h-4" />}
              link={{ href: '/intel/cards', label: '全リスク' }}
              accent="#D85A30"
            >
              {dashboard.risks.length === 0 ? (
                <EmptyHint text="主要なリスクはありません" />
              ) : (
                <ul className="space-y-2">
                  {dashboard.risks.slice(0, 3).map(d => (
                    <li key={d.card.id} className="text-xs">
                      <Link
                        href={`/intel/cards/${d.card.id}`}
                        className="block hover:text-accent-gold"
                      >
                        <div className="text-text-primary font-medium line-clamp-1">
                          {d.card.title}
                        </div>
                        <div className="text-text-muted text-[10px] mt-0.5 line-clamp-2">
                          ⚠️ {d.card.insight?.risk?.[0] ?? `リスク度 ${d.impact.components.risk}`}
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </SummaryCard>

            {/* 進行中の改革テーマ */}
            <SummaryCard
              title="進行中の改革テーマ"
              icon={<Target className="w-4 h-4" />}
              link={{ href: '/intel/themes', label: '全テーマ' }}
              accent="#2196F3"
            >
              {dashboard.inProgressThemeIds.length === 0 ? (
                <EmptyHint text="進行中テーマなし" />
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {dashboard.inProgressThemeIds.map(t => (
                    <ThemeChip key={t} themeId={t} size="md" />
                  ))}
                </div>
              )}
              <div className="mt-3 pt-3 border-t border-border text-[10px] text-text-muted">
                実行中アクション{' '}
                <span className="text-text-primary font-bold">
                  {actions.filter(a => a.status === 'in_progress').length}
                </span>
                {' / '}着手済テーマ{' '}
                <span className="text-text-primary font-bold">
                  {dashboard.inProgressThemeIds.length}
                </span>
              </div>
            </SummaryCard>
          </div>

          {/* ── 下段: アクション & 今週優先テーマ ───────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SummaryCard
              title="遅延しているアクション"
              icon={<Clock4 className="w-4 h-4" />}
              link={{ href: '/intel/actions', label: '全アクション' }}
              accent="#D85A30"
            >
              {dashboard.delayedActions.length === 0 ? (
                <EmptyHint text="遅延はありません 🎉" />
              ) : (
                <ul className="space-y-2">
                  {dashboard.delayedActions.slice(0, 4).map(a => (
                    <ActionRow key={a.id} action={a} highlight="overdue" />
                  ))}
                </ul>
              )}
            </SummaryCard>

            <SummaryCard
              title="経営判断待ち"
              icon={<CheckSquare className="w-4 h-4" />}
              link={{ href: '/intel/actions', label: '全アクション' }}
              accent="#C8860A"
            >
              {dashboard.pendingDecisions.length === 0 ? (
                <EmptyHint text="判断待ち項目はありません" />
              ) : (
                <ul className="space-y-2">
                  {dashboard.pendingDecisions.slice(0, 4).map(a => (
                    <ActionRow key={a.id} action={a} />
                  ))}
                </ul>
              )}
            </SummaryCard>
          </div>

          {/* ── 今週優先すべき改革テーマ ───────────────────────────────── */}
          <SummaryCard
            title="今週優先すべき改革テーマ"
            icon={<ListChecks className="w-4 h-4" />}
            link={{ href: '/intel/agenda', label: '週次アジェンダ' }}
            accent="#1D9E75"
          >
            {dashboard.weeklyPriorityThemes.length === 0 ? (
              <EmptyHint text="シグナル蓄積後に表示" />
            ) : (
              <div className="flex flex-wrap gap-2">
                {dashboard.weeklyPriorityThemes.map(t => (
                  <Link
                    key={t}
                    href={`/intel/themes?theme=${t}`}
                    className="hover:opacity-80"
                  >
                    <ThemeChip themeId={t} size="md" />
                  </Link>
                ))}
              </div>
            )}
            {/* テーマグループ別俯瞰 */}
            <div className="mt-4 pt-4 border-t border-border space-y-2">
              {Object.values(THEME_GROUPS).map(g => {
                const ts = THEMES_BY_GROUP[g.id];
                const matched = ts.filter(t =>
                  dashboard.weeklyPriorityThemes.includes(t),
                );
                return (
                  <div key={g.id} className="flex items-start gap-2 text-[11px]">
                    <span style={{ color: g.color }} className="font-semibold whitespace-nowrap">
                      {g.icon} {g.label}
                    </span>
                    <span className="text-text-muted">
                      {matched.length > 0
                        ? matched.map(t => THEMES[t].short).join(' / ')
                        : '— 該当シグナルなし'}
                    </span>
                  </div>
                );
              })}
            </div>
          </SummaryCard>

          {/* ── 本日のブリーフ全文導線 ──────────────────────────────────── */}
          {todayBrief && (
            <section className="card p-5 border-accent-gold/20">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-accent-gold text-[10px] font-mono uppercase tracking-wider">
                    Daily Intelligence Brief
                  </div>
                  <h2 className="text-text-primary font-bold text-base mt-0.5">
                    {formatDate(todayBrief.date)} ブリーフ全文
                  </h2>
                </div>
                <Link
                  href={`/intel/brief/${todayBrief.date}`}
                  className="text-accent-gold text-sm flex items-center gap-1 hover:text-accent-gold-light"
                >
                  読む <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
              <p className="text-text-secondary text-sm leading-relaxed">
                {todayBrief.executive_summary}
              </p>
              {council && (
                <div className="mt-3 pt-3 border-t border-border text-xs text-text-muted">
                  関連 AI 会議: {council.topic}
                </div>
              )}
            </section>
          )}

          {/* ── 過去ブリーフ ───────────────────────────────────────── */}
          {recentBriefs.length > 1 && (
            <section>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-text-primary text-sm font-semibold flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-text-muted" />
                  過去のブリーフ
                </h2>
              </div>
              <div className="space-y-2">
                {recentBriefs.slice(1, 6).map(b => (
                  <Link
                    key={b.date}
                    href={`/intel/brief/${b.date}`}
                    className="card p-3 flex items-center justify-between hover:border-accent-gold/30"
                  >
                    <div>
                      <div className="text-text-muted text-[10px] font-mono">
                        {b.date}
                      </div>
                      <div className="text-text-primary text-sm mt-0.5">
                        {b.executive_summary.slice(0, 80)}
                        {b.executive_summary.length > 80 ? '…' : ''}
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-text-muted flex-shrink-0" />
                  </Link>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}

// ─── 補助コンポーネント ───────────────────────────────────────────────

function DashboardSection({
  title, subtitle, icon, link, children,
}: {
  title: string;
  subtitle?: string;
  icon: React.ReactNode;
  link?: { href: string; label: string };
  children: React.ReactNode;
}) {
  return (
    <section>
      <div className="flex items-end justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          {icon}
          <h2 className="text-text-primary text-sm font-semibold">{title}</h2>
          {subtitle && (
            <span className="text-text-muted text-[10px]">/ {subtitle}</span>
          )}
        </div>
        {link && (
          <Link
            href={link.href}
            className="text-text-muted hover:text-accent-gold text-xs flex items-center gap-1"
          >
            {link.label} <ArrowRight className="w-3 h-3" />
          </Link>
        )}
      </div>
      {children}
    </section>
  );
}

function SummaryCard({
  title, icon, link, accent, children,
}: {
  title: string;
  icon: React.ReactNode;
  link?: { href: string; label: string };
  accent: string;
  children: React.ReactNode;
}) {
  return (
    <section
      className="card p-4 hover:border-accent-gold/30 transition-colors"
      style={{ borderLeft: `3px solid ${accent}` }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-sm font-semibold" style={{ color: accent }}>
          {icon}
          <span>{title}</span>
        </div>
        {link && (
          <Link
            href={link.href}
            className="text-text-muted hover:text-accent-gold text-[10px] flex items-center gap-1"
          >
            {link.label} <ArrowRight className="w-3 h-3" />
          </Link>
        )}
      </div>
      {children}
    </section>
  );
}

function ActionRow({
  action, highlight,
}: { action: ReformAction; highlight?: 'overdue' }) {
  return (
    <li className="flex items-start gap-2 text-xs">
      <span
        className="mt-0.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
        style={{ background: ACTION_STATUS_COLORS[action.status] }}
        title={ACTION_STATUS_LABELS[action.status]}
      />
      <div className="flex-1 min-w-0">
        <Link href="/intel/actions" className="hover:text-accent-gold">
          <div className="text-text-primary font-medium line-clamp-2">
            {action.title}
          </div>
        </Link>
        <div className="flex items-center gap-2 text-[10px] text-text-muted mt-0.5">
          <span>{action.owner}</span>
          <span>·</span>
          <span className={highlight === 'overdue' ? 'text-loss' : ''}>
            期限 {action.deadline}
          </span>
        </div>
      </div>
    </li>
  );
}

function EmptyHint({ text }: { text: string }) {
  return <div className="text-text-muted text-xs py-2">{text}</div>;
}
