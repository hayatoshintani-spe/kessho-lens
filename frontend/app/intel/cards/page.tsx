'use client';

import { useEffect, useMemo, useState } from 'react';
import { Database, Filter } from 'lucide-react';
import { fetchIntelCards } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import CardItem from '@/components/intel/CardItem';
import type { IntelCard, IntelCategory, Importance } from '@/lib/intel-types';
import {
  CATEGORY_ICONS,
  CATEGORY_LABELS_JA,
  IMPORTANCE_LABELS_JA,
  IMPORTANCE_COLORS,
} from '@/lib/intel-types';

const CATEGORIES: IntelCategory[] = [
  'ip_content',
  'ai_agent',
  'device_telecom',
  'global_region',
  'retail_md_license',
  'regulation_ip_law',
  'competitor_capital',
];

const IMPORTANCES: Importance[] = ['A', 'B', 'C', 'D'];

export default function CardsDBPage() {
  const [cards, setCards] = useState<IntelCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterCat, setFilterCat] = useState<IntelCategory | null>(null);
  const [filterImp, setFilterImp] = useState<Importance | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setIsLoading(false);
        return;
      }
      const data = await fetchIntelCards({ limit: 300 });
      setCards(data);
      setIsLoading(false);
    })();
  }, []);

  const filtered = useMemo(() => {
    return cards.filter((c) => {
      if (filterCat && c.category !== filterCat) return false;
      if (filterImp && c.importance !== filterImp) return false;
      if (search) {
        const q = search.toLowerCase();
        const haystack = [
          c.title,
          c.one_liner,
          c.fact,
          c.interpretation,
          ...c.tags,
        ]
          .join(' ')
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [cards, filterCat, filterImp, search]);

  // 集計
  const stats = useMemo(() => {
    const byImp: Record<Importance, number> = { A: 0, B: 0, C: 0, D: 0 };
    cards.forEach((c) => {
      byImp[c.importance] = (byImp[c.importance] ?? 0) + 1;
    });
    return byImp;
  }, [cards]);

  return (
    <div className="space-y-6 animate-fade-in max-w-7xl">
      <div className="flex items-center gap-2">
        <Database className="w-5 h-5 text-accent-gold" />
        <h1 className="text-text-primary text-xl font-bold">カードDB</h1>
        <span className="text-text-muted text-sm ml-2">
          全 {cards.length} 件 / 絞り込み後 {filtered.length} 件
        </span>
      </div>

      {/* 重要度別カウント */}
      <div className="grid grid-cols-4 gap-3">
        {IMPORTANCES.map((imp) => (
          <button
            key={imp}
            onClick={() => setFilterImp(filterImp === imp ? null : imp)}
            className={`card p-3 text-left transition-colors ${
              filterImp === imp ? 'border-accent-gold/40' : ''
            }`}
          >
            <div
              className="text-2xl font-bold font-tabular"
              style={{ color: IMPORTANCE_COLORS[imp] }}
            >
              {stats[imp]}
            </div>
            <div className="text-text-muted text-[10px] mt-1">
              [{imp}] {IMPORTANCE_LABELS_JA[imp]}
            </div>
          </button>
        ))}
      </div>

      {/* フィルター */}
      <div className="card p-4 space-y-3">
        <div className="flex items-center gap-2 text-text-secondary text-xs">
          <Filter className="w-3 h-3" />
          <span>フィルター</span>
        </div>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="タイトル・タグで検索..."
          className="w-full bg-bg-elevated border border-border rounded px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-gold/40"
        />
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setFilterCat(null)}
            className={`px-2 py-1 rounded text-[10px] border ${
              filterCat === null
                ? 'bg-accent-gold/10 text-accent-gold border-accent-gold/40'
                : 'bg-bg-elevated text-text-muted border-border hover:text-text-primary'
            }`}
          >
            全カテゴリ
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCat(filterCat === cat ? null : cat)}
              className={`px-2 py-1 rounded text-[10px] border ${
                filterCat === cat
                  ? 'bg-accent-gold/10 text-accent-gold border-accent-gold/40'
                  : 'bg-bg-elevated text-text-muted border-border hover:text-text-primary'
              }`}
            >
              {CATEGORY_ICONS[cat]} {CATEGORY_LABELS_JA[cat]}
            </button>
          ))}
        </div>
      </div>

      {/* カード一覧 */}
      {isLoading ? (
        <div className="card p-8 text-center text-text-muted text-sm">読み込み中...</div>
      ) : filtered.length === 0 ? (
        <div className="card p-8 text-center text-text-muted text-sm">
          該当するカードがありません
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filtered.map((c) => (
            <CardItem key={c.id} card={c} />
          ))}
        </div>
      )}
    </div>
  );
}
