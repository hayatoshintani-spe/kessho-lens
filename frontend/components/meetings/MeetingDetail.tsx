import type { MeetingLog, MeetingScenario } from '@/lib/types';
import { formatDate } from '@/lib/utils';
import { AGENT_COLORS, AGENT_NAMES } from '@/lib/utils';
import ChatBubble from './ChatBubble';
import Badge from '@/components/ui/Badge';
import { CheckCircle2, Clock, Users, BookOpen, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MeetingDetailProps {
  meeting: MeetingLog;
}

const SCENARIO_STYLES: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  'ベース': {
    icon: <Minus className="w-3.5 h-3.5" />,
    color: '#C8860A',
    bg: '#C8860A',
  },
  'ブル': {
    icon: <TrendingUp className="w-3.5 h-3.5" />,
    color: '#1D9E75',
    bg: '#1D9E75',
  },
  'ベア': {
    icon: <TrendingDown className="w-3.5 h-3.5" />,
    color: '#D85A30',
    bg: '#D85A30',
  },
};

function ScenarioBar({ scenario }: { scenario: MeetingScenario }) {
  const style = SCENARIO_STYLES[scenario.name] ?? {
    icon: <Minus className="w-3.5 h-3.5" />,
    color: '#7B7F8C',
    bg: '#7B7F8C',
  };

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: `${style.color}33`, backgroundColor: `${style.color}08` }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div
          className="w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0"
          style={{ backgroundColor: style.color }}
        >
          {style.icon}
        </div>
        <span className="font-semibold text-sm" style={{ color: style.color }}>
          {scenario.name}シナリオ
        </span>
        <span
          className="ml-auto text-xs font-bold px-2 py-0.5 rounded-full"
          style={{ color: style.color, backgroundColor: `${style.color}18` }}
        >
          確率 {scenario.probability}%
        </span>
      </div>

      {/* Probability bar */}
      <div className="h-1 bg-bg-elevated rounded-full mb-3 overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${scenario.probability}%`, backgroundColor: style.color }}
        />
      </div>

      <p className="text-text-secondary text-xs leading-relaxed mb-2">{scenario.description}</p>
      {scenario.portfolio_action && (
        <div
          className="text-[11px] px-2.5 py-1.5 rounded font-medium"
          style={{ color: style.color, backgroundColor: `${style.color}12` }}
        >
          対応方針: {scenario.portfolio_action}
        </div>
      )}
    </div>
  );
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
              参加者 ({meeting.participants.length}名)
            </div>
            <div className="flex gap-2 flex-wrap">
              {meeting.participants.map((id) => (
                <div
                  key={id}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: `${AGENT_COLORS[id] ?? '#7B7F8C'}22`,
                    border: `1px solid ${AGENT_COLORS[id] ?? '#7B7F8C'}44`,
                    color: AGENT_COLORS[id] ?? '#7B7F8C',
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
            主要決定事項・執行ルール
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

      {/* Scenario analysis */}
      {meeting.scenarios && meeting.scenarios.length > 0 && (
        <div className="card p-5">
          <h3 className="text-text-primary font-semibold text-sm mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-accent-gold" />
            3シナリオ分析
          </h3>
          <div className="grid gap-3 sm:grid-cols-3">
            {meeting.scenarios.map((s, i) => (
              <ScenarioBar key={i} scenario={s} />
            ))}
          </div>
        </div>
      )}

      {/* Chat log */}
      <div className="card p-5">
        <h3 className="text-text-primary font-semibold text-sm mb-5 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-accent-gold" />
          会議ログ {meeting.messages.length > 0 && `(${meeting.messages.length}件)`}
        </h3>
        {meeting.messages.length === 0 ? (
          <div className="py-10 text-center">
            <BookOpen className="w-8 h-8 text-text-muted mx-auto mb-3 opacity-40" />
            <p className="text-text-muted text-sm">会議ログはまだ記録されていません</p>
            <p className="text-text-muted text-xs mt-1">シミュレーション実行後に表示されます</p>
          </div>
        ) : (
          <div className="space-y-4">
            {meeting.messages.map((msg, i) => (
              <ChatBubble key={i} message={msg} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
