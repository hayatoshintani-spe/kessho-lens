import type { DiscoveryEntry } from '@/lib/types';
import { AGENT_COLORS, AGENT_NAMES, formatDate, cn } from '@/lib/utils';
import Badge from '@/components/ui/Badge';
import { Search, Star, XCircle, Eye } from 'lucide-react';

interface DiscoveryLogProps {
  entries: DiscoveryEntry[];
}

const STATUS_LABELS: Record<string, string> = {
  scanning: 'スキャン中',
  found: '発見',
  rejected: '却下',
  watchlist: 'ウォッチ',
};

const STATUS_VARIANTS: Record<string, 'default' | 'profit' | 'loss' | 'gold' | 'neutral'> = {
  scanning: 'neutral',
  found: 'profit',
  rejected: 'loss',
  watchlist: 'gold',
};

const STATUS_ICONS = {
  scanning: Search,
  found: Star,
  rejected: XCircle,
  watchlist: Eye,
};

export default function DiscoveryLog({ entries }: DiscoveryLogProps) {
  if (!entries.length) {
    return (
      <div className="text-center py-12 text-text-muted text-sm">
        銘柄探索ログがありません
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map((entry) => {
        const agentColor = AGENT_COLORS[entry.agentId] ?? '#7B7F8C';
        const StatusIcon = STATUS_ICONS[entry.status] ?? Search;

        return (
          <div
            key={entry.id}
            className="card p-4 hover:border-border-light transition-colors"
          >
            <div className="flex items-start gap-3">
              {/* Agent dot */}
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0 mt-0.5"
                style={{ backgroundColor: agentColor }}
              >
                {AGENT_NAMES[entry.agentId]?.en.charAt(0)}
              </div>

              <div className="flex-1 min-w-0">
                {/* Top row */}
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="text-text-primary font-bold font-mono text-sm">
                    {entry.ticker}
                  </span>
                  {entry.name && (
                    <span className="text-text-secondary text-xs">{entry.name}</span>
                  )}
                  {entry.nameJa && entry.nameJa !== entry.name && (
                    <span className="text-text-muted text-xs">({entry.nameJa})</span>
                  )}
                  <div className="ml-auto flex items-center gap-2 flex-shrink-0">
                    <Badge variant={STATUS_VARIANTS[entry.status]} size="sm">
                      <StatusIcon className="w-2.5 h-2.5 mr-0.5 inline" />
                      {STATUS_LABELS[entry.status] ?? entry.status}
                    </Badge>
                    {/* Score */}
                    <div
                      className="text-[11px] font-tabular font-bold px-1.5 py-0.5 rounded"
                      style={{
                        color: entry.score >= 70 ? '#1D9E75' : entry.score >= 40 ? '#C8860A' : '#D85A30',
                        backgroundColor: entry.score >= 70
                          ? '#1D9E7522'
                          : entry.score >= 40
                          ? '#C8860A22'
                          : '#D85A3022',
                      }}
                    >
                      {entry.score}pt
                    </div>
                  </div>
                </div>

                {/* Agent name + date */}
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className="text-[11px] font-medium"
                    style={{ color: agentColor }}
                  >
                    {AGENT_NAMES[entry.agentId]?.ja}
                  </span>
                  {entry.sector && (
                    <>
                      <span className="text-text-muted text-[10px]">·</span>
                      <span className="text-text-muted text-[11px]">{entry.sector}</span>
                    </>
                  )}
                  <span className="text-text-muted text-[10px] ml-auto">
                    {formatDate(entry.date)}
                  </span>
                </div>

                {/* Reason */}
                <p className="text-text-secondary text-xs leading-relaxed">{entry.reason}</p>

                {/* Price */}
                {entry.priceAtDiscovery && (
                  <div className="mt-2 text-text-muted text-[11px]">
                    発見時価格: <span className="text-text-secondary font-tabular">¥{entry.priceAtDiscovery.toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
