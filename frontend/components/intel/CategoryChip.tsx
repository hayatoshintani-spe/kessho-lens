import {
  type IntelCategory,
  CATEGORY_COLORS,
  CATEGORY_ICONS,
  CATEGORY_LABELS_JA,
} from '@/lib/intel-types';

interface Props {
  category: IntelCategory;
  size?: 'sm' | 'md';
}

export default function CategoryChip({ category, size = 'md' }: Props) {
  const color = CATEGORY_COLORS[category];
  const icon = CATEGORY_ICONS[category];
  const label = CATEGORY_LABELS_JA[category];
  const padding = size === 'sm' ? 'px-1.5 py-0.5' : 'px-2 py-1';
  const text = size === 'sm' ? 'text-[10px]' : 'text-xs';
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full ${padding} ${text}`}
      style={{
        color: color,
        backgroundColor: `${color}12`,
        border: `1px solid ${color}30`,
      }}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  );
}
