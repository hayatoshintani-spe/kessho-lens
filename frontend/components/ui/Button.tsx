import { cn } from '@/lib/utils';

export type ButtonVariant = 'gold' | 'ghost';
export type ButtonSize = 'sm' | 'md';

const VARIANTS: Record<ButtonVariant, string> = {
  gold: 'bg-accent-gold/10 border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/20',
  ghost: 'border border-border text-text-secondary hover:border-accent-gold/40 hover:text-accent-gold',
};

const SIZES: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-xs gap-1',
  md: 'px-4 py-2 text-sm gap-1.5',
};

export function buttonClasses(
  variant: ButtonVariant = 'gold',
  size: ButtonSize = 'md',
  className?: string,
) {
  return cn(
    'inline-flex items-center justify-center rounded font-medium transition-colors',
    'disabled:opacity-40 disabled:cursor-not-allowed',
    VARIANTS[variant],
    SIZES[size],
    className,
  );
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

export default function Button({
  variant = 'gold',
  size = 'md',
  className,
  ...props
}: ButtonProps) {
  return <button className={buttonClasses(variant, size, className)} {...props} />;
}
