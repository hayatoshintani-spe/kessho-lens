import { AlertTriangle, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

type AlertVariant = 'error' | 'success' | 'warning';

const VARIANTS = {
  error: {
    icon: AlertTriangle,
    box: 'border-loss/40 bg-loss/5',
    text: 'text-loss',
  },
  success: {
    icon: CheckCircle2,
    box: 'border-profit/40 bg-profit/5',
    text: 'text-profit',
  },
  warning: {
    icon: AlertTriangle,
    box: 'border-amber-500/40 bg-amber-500/5',
    text: 'text-amber-500',
  },
} as const;

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export default function Alert({
  variant = 'error',
  title,
  children,
  className,
}: AlertProps) {
  const v = VARIANTS[variant];
  const Icon = v.icon;
  return (
    <div className={cn('card p-4', v.box, className)}>
      <div className={cn('flex items-start gap-2 text-sm', v.text)}>
        <Icon className="w-4 h-4 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          {title && <div className="font-semibold mb-0.5">{title}</div>}
          <div className={cn(title && 'text-text-secondary text-xs leading-relaxed')}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
