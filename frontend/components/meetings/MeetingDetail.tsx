import type { MeetingLog } from '@/lib/types';
import { formatDate } from '@/lib/utils';
import { AGENT_COLORS, AGENT_NAMES } from '@/lib/utils';
import ChatBubble from './ChatBubble';
import Badge from '@/components/ui/Badge';
import { CheckCircle2, Clock, Users, BookOpen } from 'lucide-react';

interface MeetingDetailProps {
  meeting: MeetingLog;
}

export default function MeetingDetail({ meeting }: MeetingDetailProps) {
  return (
    <div className="space-y-6">
      {/* Header card */}
      <div className="card p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="text-text-muted text-xs uppercase tracking-wider mb-1">会議日</div>
            <h1 className="text-text-primary text-2xl font-bold">
              {formatDate(meeting.date)}
            </h1>
            {meeting.duration && (
              <div className="flex items-center gap-1.5 mt-1 text-text-muted text-sm">
                <Clock className="w-3.5 h-3.5" />
                <span>会議時間: {meeting.duration}</span>
              </div>
            )}
          </div>

          {/* Participants */}
          <div>
            <div className="text-text-muted text-xs uppercase tracking-wider mb-2 flex items-center gap-1">
              <Users className="w-3 h-3" />
              参加者
            </div>
            <div className="flex gap-2 flex-wrap">
              {meeting.participants.map((id) => (
                <div
                  key={id}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: `${AGENT_COLORS[id]}22`,
                    border: `1px solid ${AGENT_COLORS[id]}44`,
                    color: AGENT_COLORS[id],
                  }}
                >
                  {AGENT_NAMES[id]?.ja ?? id}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Market theme */}
        {meeting.marketTheme && (
          <div className="mt-4 pt-4 border-t border-border">
            <div className="text-text-muted text-xs uppercase tracking-wider mb-1.5">
              市場テーマ
            </div>
            <p className="text-accent-gold font-medium text-sm">{meeting.marketTheme}</p>
          </div>
        )}

        {/* Summary */}
        <div className="mt-4 pt-4 border-t border-border">
          <div className="text-text-muted text-xs uppercase tracking-wider mb-1.5">
            サマリー
          </div>
          <p className="text-text-secondary text-sm leading-relaxed">{meeting.summary}</p>
        </div>
      </div>

      {/* Key decisions */}
      {meeting.keyDecisions.length > 0 && (
        <div className="card p-5">
          <h3 className="text-text-primary font-semibold text-sm mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-profit" />
            主要決定事項
          </h3>
          <ul className="space-y-2">
            {meeting.keyDecisions.map((decision, i) => (
              <li key={i} className="flex items-start gap-3">
                <div className="w-5 h-5 rounded-full bg-profit/20 border border-profit/40 flex items-center justify-center text-[10px] font-bold text-profit flex-shrink-0 mt-0.5">
                  {i + 1}
                </div>
                <span className="text-text-secondary text-sm leading-relaxed">
                  {decision}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Chat log */}
      <div className="card p-5">
        <h3 className="text-text-primary font-semibold text-sm mb-5 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-accent-gold" />
          会議ログ ({meeting.messages.length}件)
        </h3>
        <div className="space-y-4">
          {meeting.messages.map((msg, i) => (
            <ChatBubble key={i} message={msg} />
          ))}
        </div>
      </div>
    </div>
  );
}
