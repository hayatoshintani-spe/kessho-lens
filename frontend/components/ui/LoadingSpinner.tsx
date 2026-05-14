import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export default function LoadingSpinner({ size = 'md', className, label }: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <div
        className={cn(
          sizes[size],
          'rounded-full border-border border-t-accent-gold animate-spin',
        )}
      />
      {label && (
        <span className="text-text-secondary text-sm">{label}</span>
      )}
    </div>
  );
}

export function FullPageSpinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center justify-center min-h-[400px] w-full">
      <LoadingSpinner size="lg" label={label ?? 'データを読み込み中...'} />
    </div>
  );
}

export function CardSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="card p-5 animate-pulse">
      <div className="h-4 bg-bg-elevated rounded w-1/3 mb-4" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-3 bg-bg-elevated rounded mb-2" style={{ width: `${70 + Math.random() * 30}%` }} />
      ))}
    </div>
  );
}
