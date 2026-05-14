import Link from 'next/link';
import type { MeetingLog } from '@/lib/types';
import { formatDate } from '@/lib/utils';
import { AGENT_COLORS, AGENT_NAMES } from '@/lib/utils';
import { ArrowRight, Users, Clock } from 'lucide-react';

interface MeetingCardProps {
  meeting: MeetingLog;
}

export default function MeetingCard({ meeting }: MeetingCardProps) {
  return (
    <Link href={`/meetings/${meeting.date}`}>
      <div className="card p-5 hover:border-border-light transition-all duration-200 group cursor-pointer">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="text-text-primary font-semibold text-sm">
              {formatDate(meeting.date)}
            </div>
            {meeting.duration && (
              <div className="flex items-center gap-1 text-text-muted text-[11px] mt-0.5">
                <Clock className="w-3 h-3" />
                <span>{meeting.duration}</span>
              </div>
            )}
          </div>

          {/* Participant avatars */}
          <div className="flex items-center">
            <div className="flex -space-x-2">
              {meeting.participants.slice(0, 4).map((id) => (
                <div
                  key={id}
                  className="w-7 h-7 rounded-full border-2 border-bg-card flex items-center justify-center text-[10px] font-bold text-white"
                  style={{ backgroundColor: AGENT_COLORS[id] }}
                  title={AGENT_NAMES[id]?.ja}
                >
                  {AGENT_NAMES[id]?.en.charAt(0)}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Market theme */}
        {meeting.marketTheme && (
          <div className="mb-3">
            <span className="text-accent-gold text-xs font-medium">
              📊 {meeting.marketTheme}
            </span>
          </div>
        )}

        {/* Summary */}
        <p className="text-text-secondary text-sm leading-relaxed line-clamp-2 mb-3">
          {meeting.summary}
        </p>

        {/* Key decisions */}
        {meeting.keyDecisions.length > 0 && (
          <div className="space-y-1.5">
            {meeting.keyDecisions.slice(0, 2).map((d, i) => (
              <div key={i} className="flex items-start gap-2">
                <div className="w-1 h-1 rounded-full bg-accent-gold mt-2 flex-shrink-0" />
                <span className="text-text-secondary text-xs leading-relaxed line-clamp-1">
                  {d}
                </span>
              </div>
            ))}
            {meeting.keyDecisions.length > 2 && (
              <div className="text-text-muted text-[11px]">
                +{meeting.keyDecisions.length - 2}件の決定事項
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="mt-4 flex items-center text-text-muted text-xs group-hover:text-accent-gold transition-colors">
          <span>会議ログを見る</span>
          <ArrowRight className="w-3 h-3 ml-1" />
        </div>
      </div>
    </Link>
  );
}
