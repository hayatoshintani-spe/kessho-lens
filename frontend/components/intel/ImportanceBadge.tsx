import { type Importance, IMPORTANCE_COLORS, IMPORTANCE_LABELS_JA } from '@/lib/intel-types';

interface Props {
  importance: Importance;
  size?: 'sm' | 'md';
}

export default function ImportanceBadge({ importance, size = 'md' }: Props) {
  const color = IMPORTANCE_COLORS[importance];
  const label = IMPORTANCE_LABELS_JA[importance];
  const padding = size === 'sm' ? 'px-1.5 py-0.5' : 'px-2 py-1';
  const text = size === 'sm' ? 'text-[10px]' : 'text-xs';
  return (
    <span
      className={`inline-flex items-center gap-1 rounded ${padding} ${text} font-semibold border`}
      style={{
        color: color,
        backgroundColor: `${color}15`,
        borderColor: `${color}40`,
      }}
    >
      <span className="font-mono">[{importance}]</span>
      <span>{label}</span>
    </span>
  );
}
