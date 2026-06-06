import type { ThemeId } from '@/lib/reform-types';
import { THEMES, THEME_GROUPS } from '@/lib/reform-taxonomies';

interface Props {
  themeId: ThemeId;
  size?: 'sm' | 'md';
}

export default function ThemeChip({ themeId, size = 'sm' }: Props) {
  const meta = THEMES[themeId];
  if (!meta) return null;
  const group = THEME_GROUPS[meta.group];
  const pad = size === 'sm' ? 'px-1.5 py-0.5' : 'px-2 py-1';
  const font = size === 'sm' ? 'text-[10px]' : 'text-xs';
  return (
    <span
      className={`inline-flex items-center gap-1 rounded ${pad} ${font} border`}
      style={{
        background: `${group.color}1A`,
        color: group.color,
        borderColor: `${group.color}40`,
      }}
      title={`${group.label} > ${meta.label}: ${meta.description}`}
    >
      <span>{group.icon}</span>
      <span>{meta.short}</span>
    </span>
  );
}
