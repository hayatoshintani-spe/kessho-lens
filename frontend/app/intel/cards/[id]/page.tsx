'use client';

import { useEffect, useState } from 'react';
import { ExternalLink, AlertTriangle, Upload, CheckCircle2 } from 'lucide-react';
import { fetchIntelCard, syncCardToNotion, fetchNotionStatus } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { IntelCard } from '@/lib/intel-types';
import ImportanceBadge from '@/components/intel/ImportanceBadge';
import CategoryChip from '@/components/intel/CategoryChip';
import Alert from '@/components/ui/Alert';
import BackLink from '@/components/ui/BackLink';
import Button from '@/components/ui/Button';
import NoticeCard from '@/components/ui/NoticeCard';
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
  const [notionEnabled, setNotionEnabled] = useState(false);
  const [notionSyncMsg, setNotionSyncMsg] = useState<{
    ok: boolean;
    text: string;
    url?: string;
  } | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setErrorMsg('バックエンドに接続できません');
        setIsLoading(false);
        return;
      }
      try {
        const [data, status] = await Promise.all([
          fetchIntelCard(params.id),
          fetchNotionStatus().catch(() => null),
        ]);
        setCard(data);
        setNotionEnabled(Boolean(status?.enabled));
      } catch (e) {
        setErrorMsg((e as Error).message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [params.id]);

  async function handleSyncToNotion() {
    if (!card) return;
    setIsSyncing(true);
    setNotionSyncMsg(null);
    try {
      const res = await syncCardToNotion(card.id);
      const r = res.result;
      if (r.action === 'created' || r.action === 'updated') {
        setNotionSyncMsg({
          ok: true,
          text: r.action === 'created' ? 'Notion に作成しました' : 'Notion を更新しました',
          url: r.url ?? undefined,
        });
      } else {
        setNotionSyncMsg({
          ok: false,
          text: r.error || `同期失敗 (${r.action})`,
        });
      }
    } catch (e) {
      setNotionSyncMsg({ ok: false, text: (e as Error).message });
    } finally {
      setIsSyncing(false);
    }
  }

  return (
    <div className="space-y-5 animate-fade-in max-w-4xl">
      <BackLink href="/intel/cards">カードDBに戻る</BackLink>

      {isLoading ? (
        <NoticeCard>読み込み中...</NoticeCard>
      ) : errorMsg ? (
        <Alert>{errorMsg}</Alert>
      ) : !card ? (
        <NoticeCard>カードが見つかりません</NoticeCard>
      ) : (
        <>
          {/* Notion 同期ボタン */}
          {notionEnabled && (
            <div className="card p-3 flex items-center justify-between gap-3">
              <div className="text-xs text-text-secondary">
                このカードを Notion DB に同期できます
              </div>
              <div className="flex items-center gap-2">
                {notionSyncMsg && (
                  <span
                    className={`text-xs flex items-center gap-1 ${
                      notionSyncMsg.ok ? 'text-profit' : 'text-loss'
                    }`}
                  >
                    {notionSyncMsg.ok ? (
                      <CheckCircle2 className="w-3 h-3" />
                    ) : (
                      <AlertTriangle className="w-3 h-3" />
                    )}
                    {notionSyncMsg.text}
                    {notionSyncMsg.url && (
                      <a
                        href={notionSyncMsg.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-1 inline-flex items-center gap-1 text-accent-gold hover:underline"
                      >
                        開く <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </span>
                )}
                <Button size="sm" onClick={handleSyncToNotion} disabled={isSyncing}>
                  <Upload className="w-3 h-3" />
                  {isSyncing ? '同期中...' : 'Notion同期'}
                </Button>
              </div>
            </div>
          )}

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
            <Alert variant="warning" title={`Confidence: ${card.confidence.toUpperCase()}`}>
              {card.speculation_notes && <p>{card.speculation_notes}</p>}
            </Alert>
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
