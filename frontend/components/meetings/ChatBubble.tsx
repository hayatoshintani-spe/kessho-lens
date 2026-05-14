import type { MeetingMessage } from '@/lib/types';
import { AGENT_COLORS, AGENT_NAMES, MESSAGE_TYPE_LABELS, MESSAGE_TYPE_COLORS } from '@/lib/utils';
import Badge from '@/components/ui/Badge';

interface ChatBubbleProps {
  message: MeetingMessage;
}

export default function ChatBubble({ message }: ChatBubbleProps) {
  const color = AGENT_COLORS[message.agent] ?? '#7B7F8C';
  const agentName = AGENT_NAMES[message.agent]?.ja ?? message.agent;
  const typeLabel = MESSAGE_TYPE_LABELS[message.type] ?? message.type;
  const typeColor = MESSAGE_TYPE_COLORS[message.type] ?? '#7B7F8C';

  return (
    <div className="flex gap-3 group animate-fade-in">
      {/* Avatar */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0 mt-1"
        style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}44` }}
      >
        {agentName.charAt(0)}
      </div>

      {/* Bubble */}
      <div className="flex-1 min-w-0">
        {/* Meta */}
        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
          <span className="text-text-primary font-medium text-sm">{agentName}</span>
          <Badge variant="custom" color={typeColor} size="sm">
            {typeLabel}
          </Badge>
          <span className="text-text-muted text-[10px] font-mono ml-auto">
            {message.time}
          </span>
        </div>

        {/* Content */}
        <div
          className="rounded-lg rounded-tl-sm p-3.5 text-sm text-text-secondary leading-relaxed"
          style={{
            backgroundColor: `${color}0D`,
            border: `1px solid ${color}22`,
          }}
        >
          {message.content}
        </div>
      </div>
    </div>
  );
}
