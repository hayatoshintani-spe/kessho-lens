'use client';

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
import type { PerformanceDataPoint } from '@/lib/types';
import { AGENT_COLORS, AGENT_NAMES, formatChartDate, formatPct } from '@/lib/utils';

interface PnLChartProps {
  data: PerformanceDataPoint[];
}

const AGENTS = ['buffett', 'soros', 'lynch', 'flat'] as const;

function CustomTooltip({ active, payload, label }: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;

  return (
    <div className="card p-3 text-xs shadow-xl min-w-[160px]">
      <div className="text-text-muted mb-2 font-mono">{label}</div>
      {payload
        .sort((a, b) => b.value - a.value)
        .map((entry) => (
          <div key={entry.name} className="flex items-center justify-between gap-4 py-0.5">
            <div className="flex items-center gap-1.5">
              <div
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-text-secondary">
                {AGENT_NAMES[entry.name as keyof typeof AGENT_NAMES]?.ja ?? entry.name}
              </span>
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

function CustomLegend({ payload }: { payload?: Array<{ value: string; color: string }> }) {
  if (!payload?.length) return null;
  return (
    <div className="flex flex-wrap gap-4 justify-center mt-2">
      {payload.map((entry) => (
        <div key={entry.value} className="flex items-center gap-1.5">
          <div className="w-3 h-0.5 rounded" style={{ backgroundColor: entry.color }} />
          <span className="text-text-muted text-[11px]">
            {AGENT_NAMES[entry.value as keyof typeof AGENT_NAMES]?.ja ?? entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function PnLChart({ data }: PnLChartProps) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-muted text-sm">
        データがありません
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
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
        <Tooltip content={<CustomTooltip />} />
        <Legend content={<CustomLegend />} />
        <ReferenceLine y={0} stroke="#2A3345" strokeDasharray="4 2" />
        {AGENTS.map((agentId) => (
          <Line
            key={agentId}
            type="monotone"
            dataKey={agentId}
            stroke={AGENT_COLORS[agentId]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
