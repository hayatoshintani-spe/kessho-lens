'use client';

import { useState, useEffect } from 'react';
import { fetchDiscoveries } from '@/lib/api';
import DiscoveryLog from '@/components/discovery/DiscoveryLog';
import EmptyState from '@/components/ui/EmptyState';
import type { DiscoveryEntry } from '@/lib/types';
import { Search } from 'lucide-react';

const MOCK_DISCOVERIES: DiscoveryEntry[] = [
  {
    id: '1',
    date: '2026-05-14',
    ticker: '3697',
    name: 'SHIFT Inc.',
    nameJa: 'シフト',
    agentId: 'lynch',
    reason: '四半期売上成長率45%を達成。QAテスト自動化市場でのシェア拡大が続いており、AI活用による生産性向上も確認。成長ストーリーが明確で、テンバガー候補として評価。',
    score: 88,
    status: 'watchlist',
    sector: 'IT・ソフトウェア',
    priceAtDiscovery: 22400,
  },
  {
    id: '2',
    date: '2026-05-14',
    ticker: '9432',
    name: 'NTT',
    nameJa: '日本電信電話',
    agentId: 'buffett',
    reason: 'PBR0.7倍と明らかな割安水準。通信インフラの安定キャッシュフローと政府保有による安心感。配当利回り3.2%も魅力。本質的価値に対して割安と判断。',
    score: 75,
    status: 'found',
    sector: '通信',
    priceAtDiscovery: 175,
  },
  {
    id: '3',
    date: '2026-05-14',
    ticker: '4592',
    name: 'Sanbio',
    nameJa: 'サンバイオ',
    agentId: 'soros',
    reason: '脳神経疾患治療薬の臨床試験結果が来月発表予定。バイナリーイベントとして大きな反応が予想されるが、リスクが高いため見送り。マクロ戦略に合致しない。',
    score: 30,
    status: 'rejected',
    sector: 'バイオ・医薬品',
    priceAtDiscovery: 2800,
  },
  {
    id: '4',
    date: '2026-05-13',
    ticker: '6758',
    name: 'Sony Group',
    nameJa: 'ソニーグループ',
    agentId: 'lynch',
    reason: '決算でゲーム・音楽・映画部門が揃って好調。PS5の普及とPlayStation Networkのサブスク収益が拡大。エンタメコングロマリットとして長期成長が期待できる。',
    score: 82,
    status: 'found',
    sector: 'エレクトロニクス・エンタメ',
    priceAtDiscovery: 13200,
  },
  {
    id: '5',
    date: '2026-05-13',
    ticker: '2413',
    name: 'M3 Inc.',
    nameJa: 'エムスリー',
    agentId: 'lynch',
    reason: '医療系デジタルプラットフォームのパイオニア。AI医療診断ツールの展開が加速中。ただし現在のバリュエーションは成長を過度に織り込んでいる可能性。引き続き監視。',
    score: 62,
    status: 'watchlist',
    sector: '医療IT',
    priceAtDiscovery: 2350,
  },
  {
    id: '6',
    date: '2026-05-12',
    ticker: '7267',
    name: 'Honda Motor',
    nameJa: 'ホンダ技研工業',
    agentId: 'soros',
    reason: '円安環境下での収益改善と日産との統合協議が進展。マクロ的に見て輸出企業への追い風が継続する見通し。ソロスAIのマクロ戦略に完全に合致。買い増しを実行。',
    score: 91,
    status: 'found',
    sector: '自動車',
    priceAtDiscovery: 1850,
  },
];

export default function DiscoveryPage() {
  const [entries, setEntries] = useState<DiscoveryEntry[]>(MOCK_DISCOVERIES);

  useEffect(() => {
    fetchDiscoveries(1, 50).then(data => { if (data && data.items.length > 0) setEntries(data.items); }).catch(() => {});
  }, []);

  const statusCounts = {
    found: entries.filter((e) => e.status === 'found').length,
    watchlist: entries.filter((e) => e.status === 'watchlist').length,
    rejected: entries.filter((e) => e.status === 'rejected').length,
    scanning: entries.filter((e) => e.status === 'scanning').length,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-text-primary text-xl font-bold flex items-center gap-2">
          <Search className="w-5 h-5 text-accent-gold" />
          銘柄探索ログ
        </h1>
        <p className="text-text-muted text-sm mt-0.5">
          AIエージェントが発掘・評価した銘柄の記録
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: '発見', count: statusCounts.found, color: '#1D9E75' },
          { label: 'ウォッチ', count: statusCounts.watchlist, color: '#C8860A' },
          { label: '却下', count: statusCounts.rejected, color: '#D85A30' },
          { label: '合計', count: entries.length, color: '#7B7F8C' },
        ].map(({ label, count, color }) => (
          <div key={label} className="card p-4 text-center">
            <div
              className="text-2xl font-bold font-tabular"
              style={{ color }}
            >
              {count}
            </div>
            <div className="text-text-muted text-xs mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Discovery log */}
      {entries.length === 0 ? (
        <EmptyState
          icon={Search}
          title="銘柄探索ログがありません"
          description="AIエージェントが銘柄を探索すると記録されます"
        />
      ) : (
        <DiscoveryLog entries={entries} />
      )}
    </div>
  );
}
