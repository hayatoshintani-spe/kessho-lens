import Link from 'next/link';
import { TrendingUp, TrendingDown, ArrowRight, AlertTriangle } from 'lucide-react';
import type { Agent } from '@/lib/types';
import { formatPct, formatLargeNumber, cn } from '@/lib/utils';
import Badge from '@/components/ui/Badge';
import PriceMetaBadge from '@/components/ui/PriceMetaBadge';

interface AgentCardProps {
  agent: Agent;
}

const RANK_LABELS = ['', '1位', '2位', '3位', '4位'];

export default function AgentCard({ agent }: AgentCardProps) {
  const isProfit = agent.totalReturn >= 0;
  const warnings = agent.portfolio.consistencyWarnings ?? [];
  const hasError = warnings.some((w) => w.level === 'error');

  return (
    <Link href={`/agents/${agent.id}`}>
      <div
        className="card p-5 hover:border-[color:var(--agent-color)] transition-all duration-200 cursor-pointer group relative overflow-hidden"
        style={{ '--agent-color': agent.color + '66' } as React.CSSProperties}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center text-base font-bold text-white flex-shrink-0"
              style={{ backgroundColor: agent.color, boxShadow: `0 0 12px ${agent.color}44` }}
            >
              {agent.name.charAt(0)}
            </div>
            <div>
              <div className="text-text-primary font-semibold text-sm leading-tight">
                {agent.nameJa}
              </div>
              <div className="text-text-muted text-[11px] mt-0.5">{agent.style}</div>
            </div>
          </div>
          {/* Warning + Rank badges */}
          <div className="flex items-center gap-1.5">
            {warnings.length > 0 && (
              <span
                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold"
                style={{
                  color: hasError ? '#D85A30' : '#C8860A',
                  backgroundColor: hasError ? '#D85A3018' : '#C8860A18',
                  border: `1px solid ${hasError ? '#D85A3055' : '#C8860A55'}`,
                }}
                title={warnings.map((w) => w.message).join('\n')}
              >
                <AlertTriangle className="w-3 h-3" />
                {warnings.length}
              </span>
            )}
            <Badge variant="gold" size="sm">
              {RANK_LABELS[agent.rank] ?? `${agent.rank}位`}
            </Badge>
          </div>
        </div>

        {/* P&L */}
        <div className="flex items-end justify-between mb-3">
          <div>
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              累計リターン
            </div>
            <div
              className={cn(
                'text-2xl font-bold font-tabular',
                isProfit ? 'text-profit' : 'text-loss',
              )}
            >
              {formatPct(agent.totalReturn)}
            </div>
          </div>
          <div className="text-right">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              損益額
            </div>
            <div
              className={cn(
                'text-sm font-medium font-tabular',
                isProfit ? 'text-profit' : 'text-loss',
              )}
            >
              {isProfit ? <TrendingUp className="inline w-3 h-3 mr-1" /> : <TrendingDown className="inline w-3 h-3 mr-1" />}
              {formatLargeNumber(Math.abs(agent.totalReturnAbs))}
            </div>
          </div>
        </div>

        {/* Recent Decision */}
        {agent.recentDecision && (
          <div className="mt-3 pt-3 border-t border-border">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              最新判断
            </div>
            <p className="text-text-secondary text-xs leading-relaxed line-clamp-2">
              {agent.recentDecision}
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-3 flex items-center justify-between gap-2">
          <PriceMetaBadge
            source={agent.portfolio.priceSource}
            updatedAt={agent.portfolio.priceUpdatedAt}
            compact
          />
          <div className="flex items-center text-text-muted text-xs group-hover:text-accent-gold transition-colors">
            <span>詳細を見る</span>
            <ArrowRight className="w-3 h-3 ml-1" />
          </div>
        </div>

        {/* Bottom color bar */}
        <div
          className="absolute bottom-0 left-0 right-0 h-0.5 rounded-b-lg opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ backgroundColor: agent.color }}
        />
      </div>
    </Link>
  );
}
