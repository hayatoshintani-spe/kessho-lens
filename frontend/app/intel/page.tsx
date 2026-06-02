'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Newspaper, Sparkles, AlertTriangle, RefreshCw } from 'lucide-react';
import {
  fetchIntelCards,
  fetchBriefs,
  fetchDailyBrief,
} from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import CardItem from '@/components/intel/CardItem';
import type {
  IntelCard,
  DailyBrief,
  BriefSummary,
  CouncilSession,
} from '@/lib/intel-types';

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

  async function handleRefreshNow() {
    if (isRefreshing) return;
    setIsRefreshing(true);
    setRefreshMsg('最新ニュースを取得中… (最大2分かかります)');
    // バックエンドを直接叩く。Vercel serverless の 10秒タイムアウト回避のため
    // Next.js プロキシを経由しない。CRON_SECRET はブラウザに露出するが
    // 本アプリは単一運用者向けで影響範囲は限定的（メール送信/コスト消費のみ）。
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? '';
    const secret = process.env.NEXT_PUBLIC_CRON_SECRET ?? '';
    if (!apiBase || !secret) {
      setRefreshMsg(
        '更新に失敗: NEXT_PUBLIC_API_BASE_URL / NEXT_PUBLIC_CRON_SECRET が未設定です',
      );
      setIsRefreshing(false);
      return;
    }
    try {
      const res = await fetch(`${apiBase}/api/intel/cron/daily-brief`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${secret}`,
        },
        signal: AbortSignal.timeout(150_000),
      });
      const data = await res.json();
      if (!res.ok) {
        setRefreshMsg(`更新に失敗: ${data.detail ?? data.error ?? res.statusText}`);
        return;
      }
      if (data.status === 'skipped') {
        setRefreshMsg(`取得できる新規ニュースがありませんでした (${data.date})`);
      } else {
        const ingested = data.ingest?.created ?? 0;
        const sent = data.email?.status === 'sent' ? '配信済み' : '配信スキップ';
        setRefreshMsg(`✅ 完了: ${ingested}件取得、${sent}。3秒後に再読み込みします`);
        setTimeout(() => window.location.reload(), 3000);
      }
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
        // 1. 最新ブリーフ一覧取得
        const briefs = await fetchBriefs();
        setRecentBriefs(briefs);

        // 2. 最新ブリーフ詳細
        if (briefs.length > 0) {
          const latest = briefs[0];
          const detail = await fetchDailyBrief(latest.date);
          setTodayBrief(detail.brief);
          setTopCards(detail.top_cards);
          setCouncil(detail.council);
        }

        // 3. 最近のカード（重要度A/B優先）
        const allCards = await fetchIntelCards({ limit: 30 });
        setRecentCards(allCards);
      } catch (e) {
        setErrorMsg((e as Error).message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      {/* Page header */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-accent-gold" />
            <h1 className="text-text-primary text-xl font-bold">
              Tsuburaya Intelligence Brief
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
          外部ニュース・規制動向・技術トレンドを、円谷の事業機会・リスク・経営論点に翻訳
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
      ) : todayBrief ? (
        <>
          {/* 本日のブリーフ */}
          <section className="card p-6 border-accent-gold/30 bg-gradient-to-br from-accent-gold/5 to-transparent">
            <div className="flex items-baseline justify-between mb-3">
              <div>
                <div className="text-accent-gold text-[10px] font-mono uppercase tracking-wider">
                  Daily Intelligence Brief
                </div>
                <h2 className="text-text-primary font-bold text-lg mt-0.5">
                  {formatDate(todayBrief.date)}
                </h2>
              </div>
              <Link
                href={`/intel/brief/${todayBrief.date}`}
                className="text-accent-gold text-sm flex items-center gap-1 hover:text-accent-gold-light"
              >
                ブリーフ全文 <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            <p className="text-text-secondary text-sm leading-relaxed mb-4">
              {todayBrief.executive_summary}
            </p>

            <div className="grid grid-cols-3 gap-3 text-center">
              <Stat
                label="重要トピックス"
                value={todayBrief.top_topics.length}
                color="#C8860A"
              />
              <Stat
                label="次アクション"
                value={todayBrief.next_actions.length}
                color="#1D9E75"
              />
              <Stat
                label="識別リスク"
                value={todayBrief.risks.length}
                color="#D85A30"
              />
            </div>
          </section>

          {/* Top topics */}
          {topCards.length > 0 && (
            <section>
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-accent-gold" />
                <h2 className="text-text-primary text-sm font-semibold">
                  本日の重要トピックス
                </h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {topCards.map((c) => (
                  <CardItem key={c.id} card={c} />
                ))}
              </div>
            </section>
          )}

          {/* AI council preview */}
          {council && (
            <section className="card p-5 border-accent-gold/20">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-text-muted text-[10px] font-mono uppercase tracking-wider">
                    AI Council Session
                  </div>
                  <h3 className="text-text-primary font-semibold text-sm mt-0.5">
                    {council.topic}
                  </h3>
                </div>
                <Link
                  href={`/intel/council`}
                  className="text-accent-gold text-xs flex items-center gap-1"
                >
                  全議論 <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
              <p className="text-text-secondary text-xs leading-relaxed mb-3">
                {council.summary}
              </p>
              <div className="flex flex-wrap gap-1.5 text-[10px]">
                {council.editor_conclusion.adopt.slice(0, 2).map((a, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded bg-profit/10 text-profit border border-profit/20"
                  >
                    採用: {a.length > 24 ? `${a.slice(0, 24)}…` : a}
                  </span>
                ))}
                {council.editor_conclusion.research.slice(0, 2).map((r, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20"
                  >
                    調査: {r.length > 24 ? `${r.slice(0, 24)}…` : r}
                  </span>
                ))}
              </div>
            </section>
          )}
        </>
      ) : (
        <div className="card p-6 text-center text-text-muted text-sm">
          まだブリーフが生成されていません
        </div>
      )}

      {/* Recent briefs */}
      {recentBriefs.length > 1 && (
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-text-primary text-sm font-semibold">過去のブリーフ</h2>
          </div>
          <div className="space-y-2">
            {recentBriefs.slice(1, 6).map((b) => (
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
                    {b.executive_summary.slice(0, 80)}…
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-text-muted flex-shrink-0" />
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Recent cards feed */}
      {recentCards.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-text-primary text-sm font-semibold">
              最近のインテリジェンスカード
            </h2>
            <Link
              href="/intel/cards"
              className="text-text-muted hover:text-accent-gold text-xs flex items-center gap-1"
            >
              全カード <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {recentCards.slice(0, 9).map((c) => (
              <CardItem key={c.id} card={c} compact />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-bg-elevated/40 rounded p-2.5">
      <div className="text-text-muted text-[10px]">{label}</div>
      <div className="text-2xl font-bold mt-1 font-tabular" style={{ color }}>
        {value}
      </div>
    </div>
  );
}
