import type { ManagementImpact } from '@/lib/reform-types';
import { RECOMMENDED_ACTION_LABELS } from '@/lib/reform-types';

interface Props {
  impact: ManagementImpact;
  size?: 'sm' | 'md' | 'lg';
  showRecommendation?: boolean;
}

function scoreColor(score: number): string {
  if (score >= 80) return '#D85A30';   // red - 即対応
  if (score >= 65) return '#C8860A';   // gold - 高
  if (score >= 50) return '#2196F3';   // blue - 中
  return '#7B7F8C';                    // gray - 低
}

export default function ImpactScoreBadge({
  impact,
  size = 'md',
  showRecommendation = false,
}: Props) {
  const color = scoreColor(impact.score);
  const sizes = {
    sm: { ring: 36, font: 'text-xs', label: 'text-[9px]' },
    md: { ring: 48, font: 'text-base', label: 'text-[10px]' },
    lg: { ring: 64, font: 'text-xl', label: 'text-xs' },
  }[size];

  return (
    <div className="flex items-center gap-2">
      <div
        className="rounded-full flex flex-col items-center justify-center border-2 flex-shrink-0"
        style={{
          width: sizes.ring,
          height: sizes.ring,
          borderColor: color,
          background: `${color}1A`,
        }}
        title={impact.rationale}
      >
        <div className={`font-bold tabular-nums leading-none ${sizes.font}`} style={{ color }}>
          {impact.score}
        </div>
        <div className={`${sizes.label} text-text-muted leading-none mt-0.5`}>点</div>
      </div>
      {showRecommendation && (
        <div className="min-w-0">
          <div className="text-[9px] text-text-muted uppercase tracking-wider">
            経営インパクト
          </div>
          <div className="text-xs text-text-primary font-medium truncate">
            {RECOMMENDED_ACTION_LABELS[impact.recommendation]}
          </div>
        </div>
      )}
    </div>
  );
}
