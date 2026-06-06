import Link from 'next/link';
import { ArrowRight, AlertTriangle } from 'lucide-react';
import type { IntelCard } from '@/lib/intel-types';
import { EXPERT_ICONS, EXPERT_LABELS_JA } from '@/lib/intel-types';
import { computeImpact, classifyThemes, classifyLenses } from '@/lib/impact-score';
import ImportanceBadge from './ImportanceBadge';
import CategoryChip from './CategoryChip';
import ImpactScoreBadge from './ImpactScoreBadge';
import ThemeChip from './ThemeChip';
import LensChip from './LensChip';
import { RECOMMENDED_ACTION_LABELS } from '@/lib/reform-types';

interface Props {
  card: IntelCard;
  compact?: boolean;
}

export default function CardItem({ card, compact = false }: Props) {
  const hasSpeculation = !!card.speculation_notes;
  const lowConfidence = card.confidence === 'low';
  const impact = computeImpact(card);
  const themes = classifyThemes(card).slice(0, 3);
  const lenses = classifyLenses(card).slice(0, 2);

  return (
    <Link
      href={`/intel/cards/${card.id}`}
      className="block card p-4 hover:border-accent-gold/40 transition-colors"
    >
      <div className="flex items-start gap-3">
        <ImpactScoreBadge impact={impact} size={compact ? 'sm' : 'md'} />
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 mb-1.5 flex-wrap">
            <ImportanceBadge importance={card.importance} size="sm" />
            <CategoryChip category={card.category} size="sm" />
            <span className="text-text-muted text-[10px] ml-auto font-mono">
              {card.date}
            </span>
          </div>

          <h3 className="text-text-primary font-semibold text-sm leading-snug mb-1">
            {card.title}
          </h3>

          <p className="text-text-secondary text-xs leading-relaxed mb-2 line-clamp-2">
            {card.one_liner}
          </p>

          {(themes.length > 0 || lenses.length > 0) && (
            <div className="flex flex-wrap gap-1 mb-2">
              {themes.map(t => <ThemeChip key={t} themeId={t} />)}
              {lenses.map(l => <LensChip key={l} lensId={l} />)}
            </div>
          )}
        </div>
      </div>

      {!compact && (
        <>
          {card.insight?.what_it_means && (
            <div className="bg-bg-elevated/40 border-l-2 border-accent-gold/40 px-3 py-2 mt-3 mb-3">
              <div className="text-[10px] text-accent-gold font-semibold mb-0.5">
                円谷への示唆
              </div>
              <p className="text-text-secondary text-xs leading-relaxed line-clamp-2">
                {card.insight.what_it_means}
              </p>
            </div>
          )}

          <div className="flex items-center justify-between text-[10px] gap-2 mt-2">
            <div className="text-text-muted truncate">
              推奨: <span className="text-text-primary">{RECOMMENDED_ACTION_LABELS[impact.recommendation]}</span>
            </div>
            <div className="flex items-center gap-1.5 flex-shrink-0">
              {card.related_agents.slice(0, 3).map((e) => (
                <span key={e} title={EXPERT_LABELS_JA[e]}>
                  {EXPERT_ICONS[e]}
                </span>
              ))}
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
