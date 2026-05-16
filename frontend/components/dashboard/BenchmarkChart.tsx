'use client';

import { useMemo, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { BenchmarkComparison, BenchmarkName, FundAgentId } from '@/lib/types';
import { AGENT_COLORS, AGENT_NAMES, formatChartDate, formatPct } from '@/lib/utils';

const BENCHMARK_COLORS: Record<BenchmarkName, string> = {
  n225: '#C8860A',
  topix: '#5B9BD5',
  sp500: '#7C9F4F',
};

const FUND_IDS: FundAgentId[] = ['buffett', 'soros', 'lynch', 'flat'];
const BENCH_IDS: BenchmarkName[] = ['n225', 'topix', 'sp500'];

interface BenchmarkChartProps {
  data: BenchmarkComparison;
}

interface ChartPoint {
  date: string;
  [key: string]: string | number;
}

function CustomTooltip({ active, payload, label, meta }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string; dataKey: string }>;
  label?: string;
  meta: BenchmarkComparison['benchmarkMeta'];
}) {
  if (!active || !payload?.length) return null;
  const labelFor = (key: string): string => {
    if (FUND_IDS.includes(key as FundAgentId)) {
      return AGENT_NAMES[key]?.ja ?? key;
    }
    return meta[key as BenchmarkName]?.displayName ?? key;
  };
  return (
    <div className="card p-3 text-xs shadow-xl min-w-[180px]">
      <div className="text-text-muted mb-2 font-mono">{label}</div>
      {payload
        .sort((a, b) => b.value - a.value)
        .map((entry) => (
          <div key={entry.dataKey} className="flex items-center justify-between gap-4 py-0.5">
            <div className="flex items-center gap-1.5">
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-text-secondary">{labelFor(entry.dataKey)}</span>
            </div>
            <span
              className="font-tabular font-medium"
              style={{ color: entry.value >= 0 ? '#1D9E75' : '#D85A30' }}
            >
              {formatPct(entry.value)}
            </span>
          </div>
        ))}
    </div>
  );
}

export default function BenchmarkChart({ data }: BenchmarkChartProps) {
  const [enabledAgents, setEnabledAgents] = useState<Record<FundAgentId, boolean>>({
    buffett: true,
    soros: true,
    lynch: true,
    flat: true,
  });
  const [enabledBenchmarks, setEnabledBenchmarks] = useState<Record<BenchmarkName, boolean>>({
    n225: true,
    topix: true,
    sp500: true,
  });

  const chartData = useMemo<ChartPoint[]>(() => {
    return data.dates.map((d, i) => {
      const row: ChartPoint = { date: d };
      for (const id of FUND_IDS) {
        const s = data.agents[id];
        if (s && i < s.length) row[id] = s[i];
      }
      for (const k of BENCH_IDS) {
        const s = data.benchmarks[k];
        if (s && i < s.length) row[k] = s[i];
      }
      return row;
    });
  }, [data]);

  const noData = !data.dates.length;
  const noBenchmark = BENCH_IDS.every((b) => !(data.benchmarks[b] && data.benchmarks[b]!.length));

  return (
    <div className="space-y-4">
      {/* Toggles */}
      <div className="flex flex-wrap gap-4 items-center text-xs">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-text-muted uppercase tracking-wider text-[10px]">ファンド</span>
          {FUND_IDS.map((id) => {
            const on = enabledAgents[id];
            return (
              <button
                key={id}
                onClick={() => setEnabledAgents((s) => ({ ...s, [id]: !s[id] }))}
                className="px-2 py-0.5 rounded-md border transition-all"
                style={{
                  borderColor: on ? AGENT_COLORS[id] : '#1E2535',
                  backgroundColor: on ? `${AGENT_COLORS[id]}18` : 'transparent',
                  color: on ? AGENT_COLORS[id] : '#7B7F8C',
                }}
              >
                <span className="inline-block w-2 h-2 rounded-full mr-1 align-middle" style={{ backgroundColor: AGENT_COLORS[id] }} />
                {AGENT_NAMES[id]?.ja ?? id}
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-text-muted uppercase tracking-wider text-[10px]">ベンチマーク</span>
          {BENCH_IDS.map((k) => {
            const on = enabledBenchmarks[k];
            const meta = data.benchmarkMeta[k];
            return (
              <button
                key={k}
                onClick={() => setEnabledBenchmarks((s) => ({ ...s, [k]: !s[k] }))}
                className="px-2 py-0.5 rounded-md border transition-all"
                style={{
                  borderColor: on ? BENCHMARK_COLORS[k] : '#1E2535',
                  backgroundColor: on ? `${BENCHMARK_COLORS[k]}18` : 'transparent',
                  color: on ? BENCHMARK_COLORS[k] : '#7B7F8C',
                }}
              >
                <span className="inline-block w-2 h-2 rounded-full mr-1 align-middle" style={{ backgroundColor: BENCHMARK_COLORS[k] }} />
                {meta?.displayName ?? k}
              </button>
            );
          })}
        </div>
      </div>

      {/* Chart */}
      {noData ? (
        <div className="flex flex-col items-center justify-center h-64 text-text-muted text-sm gap-1">
          <span>データがありません</span>
          {noBenchmark && (
            <span className="text-[11px]">
              ベンチマーク取得に失敗しました（Stooq への接続を確認してください）
            </span>
          )}
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2535" />
            <XAxis
              dataKey="date"
              tickFormatter={formatChartDate}
              tick={{ fill: '#7B7F8C', fontSize: 11 }}
              axisLine={{ stroke: '#1E2535' }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tickFormatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(1)}%`}
              tick={{ fill: '#7B7F8C', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={52}
            />
            <Tooltip content={<CustomTooltip meta={data.benchmarkMeta} />} />
            <Legend wrapperStyle={{ display: 'none' }} />
            <ReferenceLine y={0} stroke="#2A3345" strokeDasharray="4 2" />
            {FUND_IDS.filter((id) => enabledAgents[id]).map((id) => (
              <Line
                key={id}
                type="monotone"
                dataKey={id}
                stroke={AGENT_COLORS[id]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 0 }}
              />
            ))}
            {BENCH_IDS.filter((k) => enabledBenchmarks[k]).map((k) => (
              <Line
                key={k}
                type="monotone"
                dataKey={k}
                stroke={BENCHMARK_COLORS[k]}
                strokeWidth={1.5}
                strokeDasharray="6 3"
                dot={false}
                activeDot={{ r: 3, strokeWidth: 0 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}

      {/* Summary table */}
      {data.summary.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                {['エージェント', 'リターン', 'vs 日経225', 'vs TOPIX', 'vs S&P500'].map((h) => (
                  <th key={h} className="text-right text-text-muted text-[10px] uppercase tracking-wider pb-2 px-3 font-medium first:text-left whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.summary.map((row) => (
                <tr key={row.agentId} className="border-b border-border/50">
                  <td className="py-2.5 px-3">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: AGENT_COLORS[row.agentId] }}
                      />
                      <span className="text-text-primary font-medium">
                        {AGENT_NAMES[row.agentId]?.ja ?? row.agentId}
                      </span>
                    </div>
                  </td>
                  <td className="py-2.5 px-3 text-right font-tabular text-text-primary font-semibold">
                    {formatPct(row.fundReturnPct)}
                  </td>
                  <td className="py-2.5 px-3 text-right font-tabular" style={{ color: row.vsN225Pct >= 0 ? '#1D9E75' : '#D85A30' }}>
                    {formatPct(row.vsN225Pct)}
                  </td>
                  <td className="py-2.5 px-3 text-right font-tabular" style={{ color: row.vsTopixPct >= 0 ? '#1D9E75' : '#D85A30' }}>
                    {formatPct(row.vsTopixPct)}
                  </td>
                  <td className="py-2.5 px-3 text-right font-tabular" style={{ color: row.vsSp500Pct >= 0 ? '#1D9E75' : '#D85A30' }}>
                    {formatPct(row.vsSp500Pct)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
