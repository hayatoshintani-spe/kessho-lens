'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, BarChart3, Loader2 } from 'lucide-react';
import { fetchAttribution } from '@/lib/api';
import type { AttributionAnalysis, BenchmarkName, FundAgentId } from '@/lib/types';
import { formatPct } from '@/lib/utils';

interface AttributionCardProps {
  agentId: FundAgentId;
  defaultBenchmark?: BenchmarkName;
  days?: number;
}

const BENCHMARK_OPTIONS: { value: BenchmarkName; label: string }[] = [
  { value: 'topix', label: 'TOPIX' },
  { value: 'n225', label: '日経225' },
  { value: 'sp500', label: 'S&P 500' },
];

function valueColor(v: number): string {
  if (v > 0.05) return '#1D9E75';
  if (v < -0.05) return '#D85A30';
  return '#7B7F8C';
}

export default function AttributionCard({
  agentId,
  defaultBenchmark = 'topix',
  days = 90,
}: AttributionCardProps) {
  const [benchmark, setBenchmark] = useState<BenchmarkName>(defaultBenchmark);
  const [data, setData] = useState<AttributionAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchAttribution(agentId, benchmark, days)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [agentId, benchmark, days]);

  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h3 className="text-text-primary font-semibold text-sm flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-accent-gold" />
          ベンチマーク比較・寄与分析
        </h3>
        <div className="flex gap-1">
          {BENCHMARK_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setBenchmark(opt.value)}
              className="px-2.5 py-1 rounded-md border text-[11px] font-medium transition-all"
              style={{
                borderColor: benchmark === opt.value ? '#C8860A' : '#1E2535',
                backgroundColor: benchmark === opt.value ? '#C8860A18' : 'transparent',
                color: benchmark === opt.value ? '#C8860A' : '#7B7F8C',
              }}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8 text-text-muted text-xs gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          ベンチマークデータを取得中...
        </div>
      )}

      {error && !loading && (
        <div className="text-xs text-loss bg-loss/5 border border-loss/30 rounded-md p-3">
          取得に失敗しました: {error}
        </div>
      )}

      {data && !loading && (
        <>
          {/* Top stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <div className="bg-bg-elevated rounded-md p-3">
              <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">ファンド</div>
              <div className="font-bold font-tabular text-base" style={{ color: valueColor(data.fundReturnPct) }}>
                {formatPct(data.fundReturnPct)}
              </div>
            </div>
            <div className="bg-bg-elevated rounded-md p-3">
              <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">{data.benchmarkDisplay}</div>
              <div className="font-bold font-tabular text-base" style={{ color: valueColor(data.benchmarkReturnPct) }}>
                {formatPct(data.benchmarkReturnPct)}
              </div>
            </div>
            <div
              className="rounded-md p-3 border"
              style={{
                borderColor: data.excessReturnPct >= 0 ? '#1D9E7555' : '#D85A3055',
                backgroundColor: data.excessReturnPct >= 0 ? '#1D9E750D' : '#D85A300D',
              }}
            >
              <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">超過リターン</div>
              <div className="font-bold font-tabular text-base flex items-center gap-1" style={{ color: valueColor(data.excessReturnPct) }}>
                {data.excessReturnPct >= 0 ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                {formatPct(data.excessReturnPct)}
              </div>
            </div>
            <div className="bg-bg-elevated rounded-md p-3">
              <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">現金比率</div>
              <div className="font-bold font-tabular text-base text-text-primary">
                {data.cashRatioPct.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Decomposition */}
          <div className="bg-bg-elevated/50 rounded-md p-3 space-y-2">
            <div className="text-text-muted text-[10px] uppercase tracking-wider">差分の内訳</div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-secondary">キャッシュドラッグ</span>
              <span className="font-tabular font-medium" style={{ color: valueColor(data.cashDragPct) }}>
                {formatPct(data.cashDragPct)}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-secondary">銘柄選択効果</span>
              <span className="font-tabular font-medium" style={{ color: valueColor(data.selectionEffectPct) }}>
                {formatPct(data.selectionEffectPct)}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-secondary">残差（タイミング等）</span>
              <span className="font-tabular font-medium" style={{ color: valueColor(data.residualPct) }}>
                {formatPct(data.residualPct)}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs pt-2 border-t border-border">
              <span className="text-text-secondary font-semibold">合計（超過リターン）</span>
              <span className="font-tabular font-bold" style={{ color: valueColor(data.excessReturnPct) }}>
                {formatPct(data.excessReturnPct)}
              </span>
            </div>
          </div>

          {/* Narrative */}
          {data.narrative && (
            <p className="text-text-secondary text-xs leading-relaxed">{data.narrative}</p>
          )}

          {/* Contributors / Detractors */}
          <div className="grid md:grid-cols-2 gap-3">
            <div>
              <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-profit mb-2">
                <TrendingUp className="w-3 h-3" />
                上位貢献銘柄
              </div>
              {data.topContributors.length === 0 ? (
                <div className="text-text-muted text-xs">ベンチマークを上回る銘柄なし</div>
              ) : (
                <ul className="space-y-1.5">
                  {data.topContributors.map((c) => (
                    <li key={c.ticker} className="flex items-start justify-between gap-2 text-xs">
                      <div className="min-w-0">
                        <div className="text-text-primary font-mono text-[11px] truncate">{c.ticker}</div>
                        <div className="text-text-muted text-[10px] truncate">{c.name}</div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="font-tabular text-profit font-medium">{formatPct(c.contributionPct)}</div>
                        <div className="text-text-muted text-[10px] font-tabular">
                          {formatPct(c.returnPct, 1)} × {c.weightPct.toFixed(1)}%
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-loss mb-2">
                <TrendingDown className="w-3 h-3" />
                下位足を引っ張った銘柄
              </div>
              {data.topDetractors.length === 0 ? (
                <div className="text-text-muted text-xs">ベンチマークを下回る銘柄なし</div>
              ) : (
                <ul className="space-y-1.5">
                  {data.topDetractors.map((c) => (
                    <li key={c.ticker} className="flex items-start justify-between gap-2 text-xs">
                      <div className="min-w-0">
                        <div className="text-text-primary font-mono text-[11px] truncate">{c.ticker}</div>
                        <div className="text-text-muted text-[10px] truncate">{c.name}</div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="font-tabular text-loss font-medium">{formatPct(c.contributionPct)}</div>
                        <div className="text-text-muted text-[10px] font-tabular">
                          {formatPct(c.returnPct, 1)} × {c.weightPct.toFixed(1)}%
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
