import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'profit' | 'loss' | 'gold' | 'neutral' | 'custom';
  color?: string; // used when variant='custom'
  size?: 'sm' | 'md';
  className?: string;
}

export default function Badge({
  children,
  variant = 'default',
  color,
  size = 'sm',
  className,
}: BadgeProps) {
  const base = cn(
    'inline-flex items-center font-medium rounded-sm leading-none',
    size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2 py-1',
  );

  if (variant === 'custom' && color) {
    return (
      <span
        className={cn(base, className)}
        style={{ color, backgroundColor: `${color}22`, border: `1px solid ${color}44` }}
      >
        {children}
      </span>
    );
  }

  const variants: Record<string, string> = {
    default: 'bg-bg-elevated text-text-secondary border border-border',
    profit: 'bg-profit/10 text-profit border border-profit/30',
    loss: 'bg-loss/10 text-loss border border-loss/30',
    gold: 'bg-accent-gold/10 text-accent-gold border border-accent-gold/30',
    neutral: 'bg-text-secondary/10 text-text-secondary border border-text-secondary/20',
  };

  return (
    <span className={cn(base, variants[variant], className)}>
      {children}
    </span>
  );
}
