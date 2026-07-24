'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { GitMerge, ArrowLeft } from 'lucide-react';
import { fetchCouncilSessions, fetchCouncilSession } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import CouncilDebate from '@/components/intel/CouncilDebate';
import type { CouncilSession, IntelCard } from '@/lib/intel-types';
import CardItem from '@/components/intel/CardItem';
import NoticeCard from '@/components/ui/NoticeCard';

export default function CouncilPage() {
  const [sessions, setSessions] = useState<CouncilSession[]>([]);
  const [selected, setSelected] = useState<CouncilSession | null>(null);
  const [relatedCards, setRelatedCards] = useState<IntelCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setIsLoading(false);
        return;
      }
      const data = await fetchCouncilSessions();
      setSessions(data);
      // 最新セッションを自動選択
      if (data.length > 0) {
        const detail = await fetchCouncilSession(data[0].id);
        setSelected(detail.session);
        setRelatedCards(detail.related_cards);
      }
      setIsLoading(false);
    })();
  }, []);

  async function handleSelect(id: string) {
    const detail = await fetchCouncilSession(id);
    setSelected(detail.session);
    setRelatedCards(detail.related_cards);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  return (
    <div className="space-y-5 animate-fade-in max-w-5xl">
      <div className="flex items-center gap-2">
        <GitMerge className="w-5 h-5 text-accent-gold" />
        <h1 className="text-text-primary text-xl font-bold">AIエージェント会議</h1>
        <span className="text-text-muted text-sm ml-2">
          6人のエキスパートが重要テーマを議論
        </span>
      </div>

      {isLoading ? (
        <NoticeCard>読み込み中...</NoticeCard>
      ) : sessions.length === 0 ? (
        <NoticeCard>まだ会議セッションが生成されていません</NoticeCard>
      ) : (
        <>
          {/* セッション選択 */}
          {sessions.length > 1 && (
            <div className="card p-4">
              <div className="text-text-secondary text-xs mb-2">過去のセッション</div>
              <div className="space-y-1.5">
                {sessions.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleSelect(s.id)}
                    className={`w-full text-left p-2 rounded text-xs hover:bg-bg-elevated transition-colors ${
                      selected?.id === s.id
                        ? 'bg-accent-gold/10 text-accent-gold'
                        : 'text-text-secondary'
                    }`}
                  >
                    <span className="font-mono text-text-muted mr-2">{s.date}</span>
                    {s.topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {selected && <CouncilDebate session={selected} />}

          {/* 関連カード */}
          {relatedCards.length > 0 && (
            <section>
              <h3 className="text-text-primary text-sm font-semibold mb-3">
                🔗 議論の引き金となったカード
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {relatedCards.map((c) => (
                  <CardItem key={c.id} card={c} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
