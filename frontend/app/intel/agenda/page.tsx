'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Calendar,
  Sparkles,
  ArrowRight,
  ClipboardList,
  Download,
} from 'lucide-react';
import { fetchIntelCards } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import { enrichCards } from '@/lib/impact-score';
import { MOCK_WEEKLY_AGENDA } from '@/lib/reform-mock';
import { KPI_DEFS } from '@/lib/reform-taxonomies';
import type { IntelCard } from '@/lib/intel-types';
import type { WeeklyAgendaItem } from '@/lib/reform-types';

function thisMondayISO(): string {
  const d = new Date();
  const day = d.getDay(); // 0=Sun
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return d.toISOString().slice(0, 10);
}

export default function AgendaPage() {
  const [cards, setCards] = useState<IntelCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [agenda, setAgenda] = useState<WeeklyAgendaItem[]>(MOCK_WEEKLY_AGENDA);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(60_000);
      if (!alive) { setIsLoading(false); return; }
      try {
        const cs = await fetchIntelCards({ limit: 100 });
        setCards(cs);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const enriched = useMemo(() => enrichCards(cards), [cards]);
  const top5 = useMemo(
    () => [...enriched].sort((a, b) => b.impact.score - a.impact.score).slice(0, 5),
    [enriched],
  );

  // 実カードベースのアジェンダ提案を組み立てる(ルールベース)
  function regenerateFromSignals() {
    setGenerating(true);
    setTimeout(() => {
      const monday = thisMondayISO();
      const generated: WeeklyAgendaItem[] = top5.map((s, i) => ({
        id: `agd_gen_${i}`,
        rank: i + 1,
        topic: `${s.card.title} — 経営として何を意思決定するか`,
        background: s.card.fact || s.card.one_liner,
        why_now: `経営インパクト ${s.impact.score} 点 / 推奨: ${
          s.impact.recommendation === 'next_board_meeting' ? '経営会議討議'
            : s.impact.recommendation === 'this_week_action' ? '今週着手' : '今月着手'
        }`,
        related_card_ids: [s.card.id],
        related_kpi_ids: [],
        recommended_decision:
          s.card.insight?.what_it_means ?? '示唆未生成',
        next_action:
          s.card.actions?.[0]
            ? `${s.card.actions[0].who}: ${s.card.actions[0].what}`
            : '担当部門での1週間以内のアクション定義',
        week_of: monday,
      }));
      // 既存モックと混在: シグナルが少ない場合はモックで補完
      if (generated.length < 5) {
        const supplement = MOCK_WEEKLY_AGENDA.slice(0, 5 - generated.length);
        setAgenda([...generated, ...supplement]);
      } else {
        setAgenda(generated);
      }
      setGenerating(false);
    }, 400);
  }

  function copyMarkdown() {
    const md = agenda.map(a => (
`## ${a.rank}. ${a.topic}

**背景**: ${a.background}

**なぜ今**: ${a.why_now}

**推奨意思決定**: ${a.recommended_decision}

**次アクション**: ${a.next_action}
`
    )).join('\n---\n\n');
    navigator.clipboard?.writeText(md);
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl">
      <div>
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-accent-gold" />
            <h1 className="text-text-primary text-xl font-bold">
              今週の経営会議アジェンダ
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={regenerateFromSignals}
              disabled={isLoading || generating}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/10 disabled:opacity-50 transition"
            >
              <Sparkles className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
              {generating ? '生成中…' : 'シグナルから再生成'}
            </button>
            <button
              onClick={copyMarkdown}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded border border-border text-text-secondary hover:text-accent-gold transition"
              title="Markdown でクリップボードへ"
            >
              <Download className="w-3.5 h-3.5" />
              MD コピー
            </button>
          </div>
        </div>
        <p className="text-text-muted text-sm">
          外部シグナル × 経営インパクトスコアから「今週議論すべき 5 つの論点」を自動編集
        </p>
      </div>

      {agenda.map(item => (
        <AgendaCard key={item.id} item={item} cards={cards} />
      ))}
    </div>
  );
}

function AgendaCard({ item, cards }: { item: WeeklyAgendaItem; cards: IntelCard[] }) {
  const relatedCards = cards.filter(c => item.related_card_ids.includes(c.id));
  const relatedKpis = item.related_kpi_ids
    .map(id => KPI_DEFS.find(k => k.id === id))
    .filter(Boolean);

  return (
    <article className="card p-5 hover:border-accent-gold/30 transition">
      <div className="flex items-start gap-3 mb-3">
        <div
          className="w-9 h-9 rounded-full bg-accent-gold/15 border border-accent-gold/40 text-accent-gold font-bold flex items-center justify-center flex-shrink-0"
        >
          {item.rank}
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="text-text-primary font-bold text-base leading-snug">
            {item.topic}
          </h2>
        </div>
      </div>

      <div className="space-y-3 text-sm">
        <Block label="📋 背景" body={item.background} />
        <Block label="⏰ なぜ今議論すべきか" body={item.why_now} />
        <Block label="🎯 推奨される意思決定" body={item.recommended_decision} accent />
        <Block label="✅ 次アクション" body={item.next_action} />
      </div>

      {(relatedCards.length > 0 || relatedKpis.length > 0) && (
        <div className="mt-4 pt-3 border-t border-border flex flex-wrap gap-1.5 text-[10px]">
          {relatedCards.map(c => (
            <Link
              key={c.id}
              href={`/intel/cards/${c.id}`}
              className="px-2 py-1 rounded bg-bg-elevated/60 text-text-secondary hover:text-accent-gold border border-border"
            >
              <ClipboardList className="inline w-3 h-3 mr-1" />
              {c.title.length > 30 ? `${c.title.slice(0, 30)}…` : c.title}
            </Link>
          ))}
          {relatedKpis.map(k => k && (
            <Link
              key={k.id}
              href="/intel/kpi"
              className="px-2 py-1 rounded bg-bg-elevated/60 text-text-secondary hover:text-accent-gold border border-border"
            >
              📊 {k.label}
            </Link>
          ))}
        </div>
      )}
    </article>
  );
}

function Block({ label, body, accent }: { label: string; body: string; accent?: boolean }) {
  return (
    <div
      className={`rounded p-3 ${accent ? 'border-l-2 border-accent-gold/60 bg-accent-gold/5' : 'bg-bg-elevated/40'}`}
    >
      <div className="text-[10px] text-text-muted font-semibold uppercase tracking-wider mb-1">
        {label}
      </div>
      <div className="text-text-secondary text-xs leading-relaxed whitespace-pre-wrap">
        {body}
      </div>
    </div>
  );
}
