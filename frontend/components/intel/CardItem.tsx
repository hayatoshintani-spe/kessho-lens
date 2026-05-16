import Link from 'next/link';
import { ArrowRight, AlertTriangle } from 'lucide-react';
import type { IntelCard } from '@/lib/intel-types';
import { EXPERT_ICONS, EXPERT_LABELS_JA } from '@/lib/intel-types';
import ImportanceBadge from './ImportanceBadge';
import CategoryChip from './CategoryChip';

interface Props {
  card: IntelCard;
  compact?: boolean;
}

export default function CardItem({ card, compact = false }: Props) {
  const hasSpeculation = !!card.speculation_notes;
  const lowConfidence = card.confidence === 'low';

  return (
    <Link
      href={`/intel/cards/${card.id}`}
      className="block card p-4 hover:border-accent-gold/40 transition-colors"
    >
      <div className="flex items-start gap-2 mb-2 flex-wrap">
        <ImportanceBadge importance={card.importance} size="sm" />
        <CategoryChip category={card.category} size="sm" />
        <span className="text-text-muted text-[10px] ml-auto font-mono">{card.date}</span>
      </div>

      <h3 className="text-text-primary font-semibold text-sm leading-snug mb-1.5">
        {card.title}
      </h3>

      <p className="text-text-secondary text-xs leading-relaxed mb-3 line-clamp-2">
        {card.one_liner}
      </p>

      {!compact && (
        <>
          {card.insight?.what_it_means && (
            <div className="bg-bg-elevated/40 border-l-2 border-accent-gold/40 px-3 py-2 mb-3">
              <div className="text-[10px] text-accent-gold font-semibold mb-0.5">
                円谷への示唆
              </div>
              <p className="text-text-secondary text-xs leading-relaxed line-clamp-2">
                {card.insight.what_it_means}
              </p>
            </div>
          )}

          <div className="flex items-center justify-between text-[10px]">
            <div className="flex items-center gap-1.5 text-text-muted">
              {card.related_agents.slice(0, 3).map((e) => (
                <span key={e} title={EXPERT_LABELS_JA[e]}>
                  {EXPERT_ICONS[e]}
                </span>
              ))}
              {card.actions.length > 0 && (
                <span className="ml-2 text-text-secondary">
                  {card.actions.length}件のアクション
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {(hasSpeculation || lowConfidence) && (
                <span className="flex items-center gap-1 text-amber-500" title="推測注記あり">
                  <AlertTriangle className="w-3 h-3" />
                </span>
              )}
              <span className="text-accent-gold flex items-center gap-1 font-medium">
                詳細 <ArrowRight className="w-3 h-3" />
              </span>
            </div>
          </div>
        </>
      )}
    </Link>
  );
}
