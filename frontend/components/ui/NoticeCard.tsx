import { cn } from '@/lib/utils';

export default function NoticeCard({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('card p-8 text-center text-text-muted text-sm', className)}>
      {children}
    </div>
  );
}
