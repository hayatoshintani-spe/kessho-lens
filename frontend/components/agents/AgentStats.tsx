import type { Agent } from '@/lib/types';
import { formatPct, formatCurrency, cn } from '@/lib/utils';
import { Package, DollarSign } from 'lucide-react';
import PriceMetaBadge from '@/components/ui/PriceMetaBadge';
import ConsistencyBanner from '@/components/ui/ConsistencyBanner';

interface AgentStatsProps {
  agent: Agent;
}

export default function AgentStats({ agent }: AgentStatsProps) {
  const { portfolio } = agent;
  const holdingsCount = portfolio.holdings?.length ?? 0;
  const topHoldings = [...(portfolio.holdings ?? [])]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 8);
  const equityRatio = portfolio.equityRatio ?? (
    portfolio.totalValue > 0
      ? ((portfolio.totalValue - portfolio.cash) / portfolio.totalValue) * 100
      : 0
  );

  return (
    <div className="space-y-5">
      {/* Consistency warnings — only shown if any */}
      {portfolio.consistencyWarnings && portfolio.consistencyWarnings.length > 0 && (
        <ConsistencyBanner warnings={portfolio.consistencyWarnings} />
      )}

      {/* Portfolio summary */}
      <div className="card p-5">
        <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
          <h3 className="text-text-primary font-semibold text-sm flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-accent-gold" />
            ポートフォリオ概要
          </h3>
          <PriceMetaBadge source={portfolio.priceSource} updatedAt={portfolio.priceUpdatedAt} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-bg-elevated rounded-md p-3">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              総資産
            </div>
            <div className="text-text-primary font-bold font-tabular text-base">
              {formatCurrency(portfolio.totalValue)}
            </div>
          </div>
          <div className="bg-bg-elevated rounded-md p-3">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              現金
            </div>
            <div className="text-text-primary font-bold font-tabular text-base">
              {formatCurrency(portfolio.cash)}
            </div>
          </div>
          <div className="bg-bg-elevated rounded-md p-3">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              保有銘柄数
            </div>
            <div className="text-text-primary font-bold text-base">
              {holdingsCount}銘柄
            </div>
          </div>
          <div className="bg-bg-elevated rounded-md p-3">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              株式比率
            </div>
            <div className="text-text-primary font-bold font-tabular text-base">
              {portfolio.totalValue > 0 ? formatPct(equityRatio, 0) : '—'}
            </div>
          </div>
        </div>
      </div>

      {/* Holdings table */}
      {topHoldings.length > 0 && (
        <div className="card p-5">
          <h3 className="text-text-primary font-semibold text-sm mb-4 flex items-center gap-2">
            <Package className="w-4 h-4 text-accent-gold" />
            保有銘柄
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  {['銘柄', '保有株数', '平均単価', '時価', '損益率', '比率'].map((h) => (
                    <th
                      key={h}
                      className="text-left text-text-muted text-[10px] uppercase tracking-wider pb-2 px-1.5 font-medium whitespace-nowrap"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {topHoldings.map((h) => (
                  <tr key={h.ticker} className="border-b border-border/50">
                    <td className="py-2.5 px-1.5">
                      <div className="text-text-primary font-medium font-mono text-xs">
                        {h.ticker}
                      </div>
                      <div className="text-text-muted text-[10px] truncate max-w-[100px]">
                        {h.name}
                      </div>
                    </td>
                    <td className="py-2.5 px-1.5 text-text-secondary font-tabular text-xs whitespace-nowrap">
                      {h.shares.toLocaleString()}株
                    </td>
                    <td className="py-2.5 px-1.5 text-text-secondary font-tabular text-xs whitespace-nowrap">
                      ¥{h.avgCost.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-1.5 text-text-primary font-tabular text-xs whitespace-nowrap">
                      ¥{h.currentPrice.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-1.5 text-xs font-tabular whitespace-nowrap">
                      <span
                        className={cn(
                          h.unrealizedPnLPct >= 0 ? 'text-profit' : 'text-loss',
                        )}
                      >
                        {formatPct(h.unrealizedPnLPct)}
                      </span>
                    </td>
                    <td className="py-2.5 px-1.5">
                      <div className="flex items-center gap-1.5">
                        <div
                          className="h-1.5 rounded-full"
                          style={{
                            width: `${Math.min(h.weight, 100) * 0.8}px`,
                            backgroundColor: agent.color,
                            minWidth: '4px',
                          }}
                        />
                        <span className="text-text-muted text-[10px] font-tabular whitespace-nowrap">
                          {h.weight.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {holdingsCount > 8 && (
            <p className="text-text-muted text-xs mt-3 text-center">
              他 {holdingsCount - 8} 銘柄
            </p>
          )}
        </div>
      )}
    </div>
  );
}
