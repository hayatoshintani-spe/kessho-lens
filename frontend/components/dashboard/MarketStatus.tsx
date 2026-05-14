import { Activity, TrendingUp, TrendingDown } from 'lucide-react';
import type { FundStats } from '@/lib/types';
import { formatDate, formatLargeNumber, formatPct, cn } from '@/lib/utils';
import { AGENT_NAMES } from '@/lib/utils';

interface MarketStatusProps {
  stats: FundStats;
  marketTheme?: string;
}

export default function MarketStatus({ stats, marketTheme }: MarketStatusProps) {
  const isProfit = stats.totalReturn >= 0;

  return (
    <div className="card p-5">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-accent-gold" />
        <h3 className="text-text-primary text-sm font-semibold">ファンド概況</h3>
        <div className="ml-auto flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-profit animate-pulse-slow" />
          <span className="text-profit text-[11px]">稼働中</span>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-bg-elevated rounded-md p-3">
          <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
            運用総額
          </div>
          <div className="text-text-primary font-bold text-base font-tabular">
            {formatLargeNumber(stats.totalAum)}
          </div>
        </div>

        <div className="bg-bg-elevated rounded-md p-3">
          <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
            総合リターン
          </div>
          <div
            className={cn(
              'font-bold text-base font-tabular flex items-center gap-1',
              isProfit ? 'text-profit' : 'text-loss',
            )}
          >
            {isProfit ? (
              <TrendingUp className="w-3.5 h-3.5" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5" />
            )}
            {formatPct(stats.totalReturn)}
          </div>
        </div>

        <div className="bg-bg-elevated rounded-md p-3">
          <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
            最優秀AI
          </div>
          <div className="text-text-primary text-sm font-medium">
            {AGENT_NAMES[stats.bestAgent]?.ja ?? stats.bestAgent}
          </div>
        </div>

        <div className="bg-bg-elevated rounded-md p-3">
          <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
            設定来
          </div>
          <div className="text-text-secondary text-sm">
            {formatDate(stats.inception)}〜
          </div>
        </div>
      </div>

      {/* Market Theme */}
      {marketTheme && (
        <div className="pt-3 border-t border-border">
          <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1.5">
            今日の市場テーマ
          </div>
          <p className="text-text-secondary text-sm leading-relaxed">{marketTheme}</p>
        </div>
      )}
    </div>
  );
}
