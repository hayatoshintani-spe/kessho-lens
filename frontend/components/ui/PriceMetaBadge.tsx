import { Clock, Wifi } from 'lucide-react';
import { formatRelative } from '@/lib/utils';

const SOURCE_LABELS: Record<string, { label: string; color: string }> = {
  alpaca:        { label: 'Alpaca',        color: '#7C9F4F' },
  finnhub:       { label: 'Finnhub',       color: '#5B9BD5' },
  yfinance:      { label: 'Yahoo Finance', color: '#7C3AED' },
  alpha_vantage: { label: 'Alpha Vantage', color: '#0891B2' },
  mock:          { label: 'モック',        color: '#D85A30' },
  unknown:       { label: '不明',          color: '#7B7F8C' },
};

interface PriceMetaBadgeProps {
  source?: string;
  updatedAt?: string;
  compact?: boolean;
}

export default function PriceMetaBadge({ source, updatedAt, compact }: PriceMetaBadgeProps) {
  if (!source && !updatedAt) return null;
  const src = source ? (SOURCE_LABELS[source] ?? SOURCE_LABELS.unknown) : SOURCE_LABELS.unknown;
  const isMock = source === 'mock' || source === 'unknown' || !source;

  return (
    <div className={compact ? 'inline-flex items-center gap-1.5 text-[10px]' : 'inline-flex items-center gap-2 text-xs'}>
      {source && (
        <span
          className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded font-medium"
          style={{
            backgroundColor: `${src.color}1F`,
            color: src.color,
            border: `1px solid ${src.color}33`,
          }}
          title={isMock ? 'モックデータ：実勢価格を反映していません' : `データソース: ${src.label}`}
        >
          <Wifi className="w-3 h-3" />
          {src.label}
        </span>
      )}
      {updatedAt && (
        <span className="inline-flex items-center gap-1 text-text-muted">
          <Clock className="w-3 h-3" />
          {formatRelative(updatedAt)}
        </span>
      )}
    </div>
  );
}
