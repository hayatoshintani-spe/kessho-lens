import type { ConsistencyWarning } from '@/lib/types';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

const STYLES = {
  error:   { color: '#D85A30', icon: AlertCircle,    label: 'エラー' },
  warning: { color: '#C8860A', icon: AlertTriangle,  label: '警告' },
  info:    { color: '#5B9BD5', icon: Info,           label: '情報' },
} as const;

interface ConsistencyBannerProps {
  warnings: ConsistencyWarning[];
  className?: string;
}

export default function ConsistencyBanner({ warnings, className }: ConsistencyBannerProps) {
  if (!warnings || warnings.length === 0) return null;
  // Highest severity wins for the outer card border color
  const severity = warnings.some((w) => w.level === 'error')
    ? 'error'
    : warnings.some((w) => w.level === 'warning')
      ? 'warning'
      : 'info';
  const outer = STYLES[severity];

  return (
    <div
      className={`rounded-lg border p-3 ${className ?? ''}`}
      style={{ borderColor: `${outer.color}55`, backgroundColor: `${outer.color}0D` }}
    >
      <div className="flex items-center gap-2 mb-2" style={{ color: outer.color }}>
        <outer.icon className="w-4 h-4" />
        <span className="text-xs font-semibold uppercase tracking-wider">
          データ整合性 {warnings.length}件の指摘
        </span>
      </div>
      <ul className="space-y-1.5">
        {warnings.map((w, i) => {
          const s = STYLES[w.level] ?? STYLES.info;
          return (
            <li key={i} className="flex items-start gap-2 text-xs">
              <s.icon className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: s.color }} />
              <span className="text-text-secondary leading-relaxed">{w.message}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
