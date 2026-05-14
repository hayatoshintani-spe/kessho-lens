import type { Agent } from '@/lib/types';
import { formatPct, formatLargeNumber, cn } from '@/lib/utils';
import Link from 'next/link';

interface RankingTableProps {
  agents: Agent[];
}

const RANK_MEDALS = ['🥇', '🥈', '🥉', ''];

export default function RankingTable({ agents }: RankingTableProps) {
  const sorted = [...agents].sort((a, b) => a.rank - b.rank);

  return (
    <div className="overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left text-text-muted text-[11px] uppercase tracking-wider pb-2 px-2 font-medium">
              順位
            </th>
            <th className="text-left text-text-muted text-[11px] uppercase tracking-wider pb-2 px-2 font-medium">
              エージェント
            </th>
            <th className="text-right text-text-muted text-[11px] uppercase tracking-wider pb-2 px-2 font-medium">
              累計リターン
            </th>
            <th className="text-right text-text-muted text-[11px] uppercase tracking-wider pb-2 px-2 font-medium hidden sm:table-cell">
              損益額
            </th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((agent, i) => {
            const isProfit = agent.totalReturn >= 0;
            return (
              <tr
                key={agent.id}
                className="border-b border-border/50 hover:bg-bg-elevated/50 transition-colors"
              >
                <td className="py-3 px-2">
                  <span className="text-sm">
                    {RANK_MEDALS[i] || `${i + 1}`}
                  </span>
                </td>
                <td className="py-3 px-2">
                  <Link
                    href={`/agents/${agent.id}`}
                    className="flex items-center gap-2 hover:text-accent-gold transition-colors"
                  >
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                      style={{ backgroundColor: agent.color }}
                    >
                      {agent.name.charAt(0)}
                    </div>
                    <div>
                      <div className="text-text-primary text-sm font-medium leading-tight">
                        {agent.nameJa}
                      </div>
                      <div className="text-text-muted text-[10px]">{agent.style}</div>
                    </div>
                  </Link>
                </td>
                <td className="py-3 px-2 text-right">
                  <span
                    className={cn(
                      'text-sm font-bold font-tabular',
                      isProfit ? 'text-profit' : 'text-loss',
                    )}
                  >
                    {formatPct(agent.totalReturn)}
                  </span>
                </td>
                <td className="py-3 px-2 text-right hidden sm:table-cell">
                  <span
                    className={cn(
                      'text-xs font-tabular',
                      isProfit ? 'text-profit' : 'text-loss',
                    )}
                  >
                    {isProfit ? '+' : '-'}
                    {formatLargeNumber(Math.abs(agent.totalReturnAbs))}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
