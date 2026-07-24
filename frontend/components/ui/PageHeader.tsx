import { LucideIcon } from 'lucide-react';

interface PageHeaderProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  meta?: React.ReactNode;
  actions?: React.ReactNode;
}

export default function PageHeader({
  icon: Icon,
  title,
  description,
  meta,
  actions,
}: PageHeaderProps) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-1 flex-wrap">
        {Icon && <Icon className="w-5 h-5 text-accent-gold" />}
        <h1 className="text-text-primary text-xl font-bold">{title}</h1>
        {meta && <span className="text-text-muted text-sm ml-2">{meta}</span>}
        {actions && <div className="ml-auto">{actions}</div>}
      </div>
      {description && <p className="text-text-muted text-sm">{description}</p>}
    </div>
  );
}
