'use client';

import { useEffect, useState } from 'react';
import { Radar } from 'lucide-react';
import { fetchWatchlists } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import type { CategoryWatchlist } from '@/lib/intel-types';
import {
  CATEGORY_COLORS,
  CATEGORY_ICONS,
  CATEGORY_LABELS_JA,
} from '@/lib/intel-types';

export default function WatchlistPage() {
  const [watchlists, setWatchlists] = useState<CategoryWatchlist[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setIsLoading(false);
        return;
      }
      const data = await fetchWatchlists();
      setWatchlists(data);
      setIsLoading(false);
    })();
  }, []);

  return (
    <div className="space-y-5 animate-fade-in max-w-6xl">
      <div className="flex items-center gap-2">
        <Radar className="w-5 h-5 text-accent-gold" />
        <h1 className="text-text-primary text-xl font-bold">ウォッチリスト</h1>
        <span className="text-text-muted text-sm ml-2">
          7カテゴリ × 監視対象企業・キーワード
        </span>
      </div>

      {isLoading ? (
        <div className="card p-8 text-center text-text-muted text-sm">
          読み込み中...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {watchlists.map((wl) => {
            const color = CATEGORY_COLORS[wl.category];
            return (
              <div key={wl.category} className="card p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div
                    className="w-8 h-8 rounded flex items-center justify-center text-base"
                    style={{
                      backgroundColor: `${color}20`,
                      border: `1px solid ${color}40`,
                    }}
                  >
                    {CATEGORY_ICONS[wl.category]}
                  </div>
                  <div>
                    <div className="text-text-primary font-semibold text-sm">
                      {CATEGORY_LABELS_JA[wl.category]}
                    </div>
                  </div>
                </div>

                <p className="text-text-secondary text-xs leading-relaxed mb-3">
                  {wl.description}
                </p>

                <div className="space-y-1.5 mb-4">
                  {wl.items.map((item, i) => {
                    const priColor =
                      item.priority === 'high'
                        ? '#D85A30'
                        : item.priority === 'medium'
                          ? '#C8860A'
                          : '#7B7F8C';
                    return (
                      <div
                        key={i}
                        className="flex items-start gap-2 p-2 rounded bg-bg-elevated/40"
                      >
                        <div
                          className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
                          style={{ backgroundColor: priColor }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-text-primary text-xs font-medium">
                            {item.keyword}
                          </div>
                          <div className="text-text-muted text-[10px] mt-0.5 leading-snug">
                            {item.rationale}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div>
                  <div className="text-text-muted text-[10px] mb-1.5 uppercase tracking-wider">
                    主要対象
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {wl.targets.map((t, i) => (
                      <span
                        key={i}
                        className="text-[10px] px-1.5 py-0.5 rounded bg-bg-elevated text-text-secondary border border-border"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
