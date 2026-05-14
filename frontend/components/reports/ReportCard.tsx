import Link from 'next/link';
import type { DailyReport } from '@/lib/types';
import { formatDate, formatPct, cn } from '@/lib/utils';
import { ArrowRight, TrendingUp, TrendingDown, FileText } from 'lucide-react';

interface ReportCardProps {
  report: DailyReport;
}

export default function ReportCard({ report }: ReportCardProps) {
  const isProfit = report.totalFundReturn >= 0;

  return (
    <Link href={`/reports/${report.date}`}>
      <div className="card p-5 hover:border-border-light transition-all duration-200 group cursor-pointer">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-accent-gold/10 border border-accent-gold/20 flex items-center justify-center flex-shrink-0">
              <FileText className="w-4 h-4 text-accent-gold" />
            </div>
            <div>
              <div className="text-text-primary font-semibold text-sm">
                {formatDate(report.date)}
              </div>
              <div className="text-text-muted text-xs mt-0.5 line-clamp-1">
                {report.title}
              </div>
            </div>
          </div>

          {/* Fund return */}
          <div
            className={cn(
              'flex items-center gap-1 text-sm font-bold font-tabular',
              isProfit ? 'text-profit' : 'text-loss',
            )}
          >
            {isProfit ? (
              <TrendingUp className="w-3.5 h-3.5" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5" />
            )}
            {formatPct(report.totalFundReturn)}
          </div>
        </div>

        {/* Market theme */}
        {report.marketTheme && (
          <p className="text-text-muted text-xs mb-2 truncate">
            📊 {report.marketTheme}
          </p>
        )}

        {/* Content excerpt */}
        <p className="text-text-secondary text-sm leading-relaxed line-clamp-3">
          {report.content.slice(0, 200).replace(/[#*`]/g, '')}...
        </p>

        {/* Footer */}
        <div className="mt-4 flex items-center text-text-muted text-xs group-hover:text-accent-gold transition-colors">
          <span>レポートを読む</span>
          <ArrowRight className="w-3 h-3 ml-1" />
        </div>
      </div>
    </Link>
  );
}
