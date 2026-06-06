'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Target, ArrowRight } from 'lucide-react';
import { fetchIntelCards } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import {
  THEMES,
  THEMES_BY_GROUP,
  THEME_GROUPS,
} from '@/lib/reform-taxonomies';
import { enrichCards } from '@/lib/impact-score';
import type { IntelCard } from '@/lib/intel-types';
import type { ThemeGroupId, ThemeId } from '@/lib/reform-types';
import ImpactScoreBadge from '@/components/intel/ImpactScoreBadge';

export default function ThemesPage() {
  const [cards, setCards] = useState<IntelCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeGroup, setActiveGroup] = useState<ThemeGroupId | 'all'>('all');

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(60_000);
      if (!alive) { setIsLoading(false); return; }
      try {
        const cs = await fetchIntelCards({ limit: 200 });
        setCards(cs);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const enriched = useMemo(() => enrichCards(cards), [cards]);

  // テーマ別シグナル集計
  const themeStats = useMemo(() => {
    const stats: Record<ThemeId, { count: number; avgScore: number; topCards: typeof enriched }> =
      {} as Record<ThemeId, { count: number; avgScore: number; topCards: typeof enriched }>;
    (Object.keys(THEMES) as ThemeId[]).forEach(t => {
      const matches = enriched.filter(e => e.themes.includes(t));
      const avg = matches.length
        ? Math.round(matches.reduce((s, m) => s + m.impact.score, 0) / matches.length)
        : 0;
      const topCards = [...matches]
        .sort((a, b) => b.impact.score - a.impact.score)
        .slice(0, 3);
      stats[t] = { count: matches.length, avgScore: avg, topCards };
    });
    return stats;
  }, [enriched]);

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Target className="w-5 h-5 text-accent-gold" />
          <h1 className="text-text-primary text-xl font-bold">経営課題マップ</h1>
        </div>
        <p className="text-text-muted text-sm">
          外部シグナルを 5 グループ・21 テーマに分類し、改革テーマ別に優先順位を可視化
        </p>
      </div>

      {/* グループフィルタ */}
      <div className="flex flex-wrap gap-2">
        <FilterButton
          label="すべて"
          active={activeGroup === 'all'}
          onClick={() => setActiveGroup('all')}
          color="#C8860A"
        />
        {Object.values(THEME_GROUPS).map(g => (
          <FilterButton
            key={g.id}
            label={`${g.icon} ${g.label}`}
            active={activeGroup === g.id}
            onClick={() => setActiveGroup(g.id)}
            color={g.color}
          />
        ))}
      </div>

      {isLoading ? (
        <div className="card p-8 text-center text-text-muted text-sm">読み込み中...</div>
      ) : (
        <div className="space-y-6">
          {Object.values(THEME_GROUPS)
            .filter(g => activeGroup === 'all' || g.id === activeGroup)
            .map(g => (
              <section key={g.id}>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xl">{g.icon}</span>
                  <h2 className="text-text-primary text-base font-semibold" style={{ color: g.color }}>
                    {g.label}
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {THEMES_BY_GROUP[g.id].map(tid => {
                    const meta = THEMES[tid];
                    const stat = themeStats[tid];
                    return (
                      <div key={tid} className="card p-4">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h3 className="text-text-primary text-sm font-semibold">
                            {meta.label}
                          </h3>
                          <span
                            className="text-[10px] px-1.5 py-0.5 rounded border"
                            style={{
                              background: `${g.color}1A`,
                              color: g.color,
                              borderColor: `${g.color}40`,
                            }}
                          >
                            シグナル {stat.count}
                          </span>
                        </div>
                        <p className="text-text-muted text-xs leading-relaxed mb-3">
                          {meta.description}
                        </p>

                        {stat.count > 0 ? (
                          <>
                            <div className="flex items-center gap-2 mb-2 text-[10px] text-text-muted">
                              <span>平均インパクト</span>
                              <span className="text-text-primary font-bold">{stat.avgScore}</span>
                            </div>
                            <ul className="space-y-1.5">
                              {stat.topCards.map(t => (
                                <li key={t.card.id} className="flex items-start gap-2">
                                  <ImpactScoreBadge impact={t.impact} size="sm" />
                                  <Link
                                    href={`/intel/cards/${t.card.id}`}
                                    className="text-xs text-text-primary hover:text-accent-gold line-clamp-2 flex-1"
                                  >
                                    {t.card.title}
                                  </Link>
                                </li>
                              ))}
                            </ul>
                          </>
                        ) : (
                          <div className="text-text-muted text-[11px] italic">
                            該当シグナルなし
                          </div>
                        )}

                        <Link
                          href={`/intel/cards?theme=${tid}`}
                          className="mt-3 inline-flex items-center gap-1 text-[10px] text-accent-gold hover:text-accent-gold-light"
                        >
                          このテーマを深掘り <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    );
                  })}
                </div>
              </section>
            ))}
        </div>
      )}
    </div>
  );
}

function FilterButton({
  label, active, onClick, color,
}: { label: string; active: boolean; onClick: () => void; color: string }) {
  return (
    <button
      onClick={onClick}
      className="px-3 py-1.5 rounded text-xs font-medium transition border"
      style={{
        background: active ? `${color}1A` : 'transparent',
        color: active ? color : '#7B7F8C',
        borderColor: active ? `${color}60` : '#2A2D36',
      }}
    >
      {label}
    </button>
  );
}
