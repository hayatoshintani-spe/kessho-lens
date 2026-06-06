import type { IPLensId } from '@/lib/reform-types';
import { IP_LENSES } from '@/lib/reform-taxonomies';

interface Props {
  lensId: IPLensId;
  size?: 'sm' | 'md';
}

export default function LensChip({ lensId, size = 'sm' }: Props) {
  const meta = IP_LENSES[lensId];
  if (!meta) return null;
  const pad = size === 'sm' ? 'px-1.5 py-0.5' : 'px-2 py-1';
  const font = size === 'sm' ? 'text-[10px]' : 'text-xs';
  return (
    <span
      className={`inline-flex items-center gap-1 rounded ${pad} ${font} bg-accent-gold/10 text-accent-gold border border-accent-gold/30`}
      title={`${meta.label}: ${meta.description}`}
    >
      <span>{meta.icon}</span>
      <span>{meta.short}</span>
    </span>
  );
}
