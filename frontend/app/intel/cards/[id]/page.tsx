'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, AlertTriangle } from 'lucide-react';
import { fetchIntelCard } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { IntelCard } from '@/lib/intel-types';
import ImportanceBadge from '@/components/intel/ImportanceBadge';
import CategoryChip from '@/components/intel/CategoryChip';
import {
  EXPERT_ICONS,
  EXPERT_LABELS_JA,
  EXPERT_COLORS,
  PRIORITY_LABELS_JA,
} from '@/lib/intel-types';

interface PageProps {
  params: { id: string };
}

export default function CardDetailPage({ params }: PageProps) {
  const [card, setCard] = useState<IntelCard | null>(null);
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
        const data = await fetchIntelCard(params.id);
        setCard(data);
      } catch (e) {
        setErrorMsg((e as Error).message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [params.id]);

  return (
    <div className="space-y-5 animate-fade-in max-w-4xl">
      <Link
        href="/intel/cards"
        className="inline-flex items-center gap-1 text-text-muted hover:text-accent-gold text-xs"
      >
        <ArrowLeft className="w-3 h-3" /> カードDBに戻る
      </Link>

      {isLoading ? (
        <div className="card p-8 text-center text-text-muted text-sm">読み込み中...</div>
      ) : errorMsg ? (
        <div className="card p-4 border-loss/40 bg-loss/5 text-loss text-sm">
          {errorMsg}
        </div>
      ) : !card ? (
        <div className="card p-6 text-center text-text-muted">カードが見つかりません</div>
      ) : (
        <>
          {/* ヘッダー */}
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-3 flex-wrap">
              <ImportanceBadge importance={card.importance} />
              <CategoryChip category={card.category} />
              <span className="text-text-muted text-xs ml-auto font-mono">
                {formatDate(card.date)}
              </span>
            </div>
            <h1 className="text-text-primary font-bold text-xl leading-tight mb-2">
              {card.title}
            </h1>
            <p className="text-text-secondary text-sm leading-relaxed">
              {card.one_liner}
            </p>
            {card.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-4">
                {card.tags.map((tag, i) => (
                  <span
                    key={i}
                    className="text-[10px] px-2 py-0.5 rounded-full bg-bg-elevated text-text-secondary border border-border"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Confidence / Speculation 警告 */}
          {(card.confidence === 'low' || card.speculation_notes) && (
            <div className="card p-4 border-amber-500/40 bg-amber-500/5">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-text-secondary leading-relaxed">
                  <div className="font-semibold text-amber-500 mb-1">
                    Confidence: {card.confidence.toUpperCase()}
                  </div>
                  {card.speculation_notes && <p>{card.speculation_notes}</p>}
                </div>
              </div>
            </div>
          )}

          {/* 事実 / 解釈 */}
          <div className="card p-6">
            <h2 className="text-text-primary font-bold text-sm mb-3">📋 事実</h2>
            <p className="text-text-secondary text-sm leading-relaxed whitespace-pre-wrap">
              {card.fact}
            </p>
          </div>

          <div className="card p-6">
            <h2 className="text-text-primary font-bold text-sm mb-3">🔍 解釈</h2>
            <p className="text-text-secondary text-sm leading-relaxed whitespace-pre-wrap">
              {card.interpretation}
            </p>
          </div>

          {/* 円谷への示唆 */}
          <div className="card p-6 border-accent-gold/30 bg-accent-gold/5">
            <h2 className="text-accent-gold font-bold text-sm mb-3">
              💡 円谷への示唆
            </h2>
            <p className="text-text-secondary text-sm leading-relaxed mb-4">
              {card.insight.what_it_means}
            </p>

            {card.insight.business_opportunity.length > 0 && (
              <div className="mb-4">
                <div className="text-profit text-xs font-semibold mb-2">
                  🌱 事業機会
                </div>
                <ul className="space-y-1.5">
                  {card.insight.business_opportunity.map((o, i) => (
                    <li
                      key={i}
                      className="text-text-secondary text-xs leading-relaxed pl-3 relative"
                    >
                      <span className="absolute left-0 top-1.5 w-1 h-1 rounded-full bg-profit" />
                      {o}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {card.insight.risk.length > 0 && (
              <div>
                <div className="text-loss text-xs font-semibold mb-2">⚠️ リスク</div>
                <ul className="space-y-1.5">
                  {card.insight.risk.map((r, i) => (
                    <li
                      key={i}
                      className="text-text-secondary text-xs leading-relaxed pl-3 relative"
                    >
                      <span className="absolute left-0 top-1.5 w-1 h-1 rounded-full bg-loss" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* 次アクション */}
          {card.actions.length > 0 && (
            <div className="card p-6">
              <h2 className="text-text-primary font-bold text-sm mb-3">
                ✅ 次アクション
              </h2>
              <div className="space-y-2">
                {card.actions.map((a, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 rounded bg-bg-elevated/40 border border-border"
                  >
                    <div className="text-xs flex-shrink-0 min-w-[88px] font-medium">
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
            </div>
          )}

          {/* 関連エキスパート */}
          {card.related_agents.length > 0 && (
            <div className="card p-5">
              <h2 className="text-text-primary font-bold text-sm mb-3">
                👥 関連エキスパート
              </h2>
              <div className="flex flex-wrap gap-2">
                {card.related_agents.map((e) => (
                  <div
                    key={e}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs"
                    style={{
                      borderColor: `${EXPERT_COLORS[e]}40`,
                      backgroundColor: `${EXPERT_COLORS[e]}10`,
                      color: EXPERT_COLORS[e],
                    }}
                  >
                    <span>{EXPERT_ICONS[e]}</span>
                    <span>{EXPERT_LABELS_JA[e]}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 出典 */}
          {card.sources.length > 0 && (
            <div className="card p-5">
              <h2 className="text-text-primary font-bold text-sm mb-3">📰 出典</h2>
              <div className="space-y-2">
                {card.sources.map((s, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 p-2 rounded bg-bg-elevated/40"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-text-primary text-xs font-medium leading-snug">
                        {s.title}
                      </div>
                      <div className="text-text-muted text-[10px] mt-0.5">
                        {s.publisher} · {s.published_at} ·{' '}
                        <span className="font-mono">{s.access_status}</span>
                      </div>
                    </div>
                    {s.url && (
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-text-muted hover:text-accent-gold flex-shrink-0"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
