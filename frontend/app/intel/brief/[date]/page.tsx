'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Calendar, MessageSquare } from 'lucide-react';
import Alert from '@/components/ui/Alert';
import BackLink from '@/components/ui/BackLink';
import NoticeCard from '@/components/ui/NoticeCard';
import { fetchDailyBrief } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import CardItem from '@/components/intel/CardItem';
import { PRIORITY_LABELS_JA } from '@/lib/intel-types';
import type {
  DailyBrief,
  IntelCard,
  CouncilSession,
} from '@/lib/intel-types';

interface PageProps {
  params: { date: string };
}

export default function BriefDetailPage({ params }: PageProps) {
  const [brief, setBrief] = useState<DailyBrief | null>(null);
  const [topCards, setTopCards] = useState<IntelCard[]>([]);
  const [council, setCouncil] = useState<CouncilSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setErrorMsg('バックエンドに接続できません');
        setIsLoading(false);
        return;
      }
      try {
        const data = await fetchDailyBrief(params.date);
        setBrief(data.brief);
        setTopCards(data.top_cards);
        setCouncil(data.council);
      } catch (e) {
        setErrorMsg((e as Error).message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [params.date]);

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <BackLink href="/intel">ブリーフ一覧に戻る</BackLink>

      {errorMsg && <Alert>{errorMsg}</Alert>}

      {isLoading ? (
        <NoticeCard>読み込み中...</NoticeCard>
      ) : !brief ? (
        <NoticeCard>ブリーフが見つかりません</NoticeCard>
      ) : (
        <>
          {/* Brief header */}
          <div className="card p-6 border-accent-gold/30">
            <div className="flex items-center gap-1.5 text-accent-gold text-[10px] font-mono uppercase tracking-wider mb-1">
              <Calendar className="w-3 h-3" />
              {brief.brief_type === 'daily' ? 'Daily' : brief.brief_type === 'weekly' ? 'Weekly' : 'Monthly'} Intelligence Brief
            </div>
            <h1 className="text-text-primary text-xl font-bold mb-1">
              {formatDate(brief.date)}
            </h1>
            <p className="text-text-secondary text-sm leading-relaxed mt-3">
              {brief.executive_summary}
            </p>
          </div>

          {/* Top cards */}
          {topCards.length > 0 && (
            <section>
              <h2 className="text-text-primary text-sm font-semibold mb-3">
                🔝 重要トピックス
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {topCards.map((c) => (
                  <CardItem key={c.id} card={c} />
                ))}
              </div>
            </section>
          )}

          {/* Sections (markdown) */}
          {brief.sections.map((section, i) => (
            <section key={i} className="card p-6">
              <h2 className="text-text-primary font-bold text-base mb-4">
                {section.heading}
              </h2>
              <div className="markdown-report">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {section.body}
                </ReactMarkdown>
              </div>
            </section>
          ))}

          {/* Council link */}
          {council && (
            <section className="card p-5 border-accent-gold/30 bg-accent-gold/5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-accent-gold" />
                  <h3 className="text-text-primary font-semibold text-sm">
                    関連AIエージェント会議
                  </h3>
                </div>
                <Link
                  href={`/intel/council`}
                  className="text-accent-gold text-xs flex items-center gap-1"
                >
                  全議論を読む →
                </Link>
              </div>
              <div className="text-text-primary text-sm font-medium mb-2">
                {council.topic}
              </div>
              <p className="text-text-secondary text-xs leading-relaxed">
                {council.summary}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="text-[10px] px-2 py-0.5 rounded bg-bg-elevated text-text-muted">
                  発言: {council.messages.length}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-profit/10 text-profit border border-profit/20">
                  採用: {council.editor_conclusion.adopt.length}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-500 border border-amber-500/20">
                  保留: {council.editor_conclusion.hold.length}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  追加調査: {council.editor_conclusion.research.length}
                </span>
              </div>
            </section>
          )}

          {/* Next actions detail */}
          {brief.next_actions.length > 0 && (
            <section className="card p-6">
              <h2 className="text-text-primary font-bold text-base mb-4">
                ✅ 次アクション詳細
              </h2>
              <div className="space-y-2">
                {brief.next_actions.map((a, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded bg-bg-elevated/30 border border-border"
                  >
                    <div className="text-xs flex-shrink-0 min-w-[88px]">
                      {PRIORITY_LABELS_JA[a.priority]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-text-primary text-xs font-semibold">
                        {a.who}
                      </div>
                      <div className="text-text-secondary text-xs leading-relaxed mt-0.5">
                        {a.what}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
