import type { CouncilSession } from '@/lib/intel-types';
import {
  EXPERT_ICONS,
  EXPERT_COLORS,
  STANCE_LABELS_JA,
  STANCE_COLORS,
} from '@/lib/intel-types';

interface Props {
  session: CouncilSession;
}

export default function CouncilDebate({ session }: Props) {
  return (
    <div className="space-y-4">
      <div className="card p-5">
        <div className="text-text-muted text-[10px] font-mono mb-1">{session.date}</div>
        <h2 className="text-text-primary font-bold text-lg leading-snug mb-2">
          {session.topic}
        </h2>
        <p className="text-text-secondary text-sm leading-relaxed">{session.summary}</p>
      </div>

      <div className="card p-5">
        <h3 className="text-text-primary text-sm font-semibold mb-4">議論ログ</h3>
        <div className="space-y-3">
          {session.messages.map((m, idx) => {
            const color = EXPERT_COLORS[m.expert_id];
            const stanceColor = STANCE_COLORS[m.stance];
            return (
              <div key={idx} className="flex gap-3">
                <div
                  className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-base"
                  style={{
                    backgroundColor: `${color}20`,
                    border: `1px solid ${color}50`,
                  }}
                >
                  {EXPERT_ICONS[m.expert_id]}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2 mb-1 flex-wrap">
                    <span
                      className="font-semibold text-xs"
                      style={{ color }}
                    >
                      {m.expert_name}
                    </span>
                    <span className="text-text-muted text-[10px] font-mono">{m.time}</span>
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded"
                      style={{
                        color: stanceColor,
                        backgroundColor: `${stanceColor}15`,
                        border: `1px solid ${stanceColor}30`,
                      }}
                    >
                      {STANCE_LABELS_JA[m.stance]}
                    </span>
                  </div>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    {m.content}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card p-5 border-accent-gold/30 bg-accent-gold/5">
        <h3 className="text-accent-gold font-bold text-sm mb-4">📝 編集長としての結論</h3>

        <ConclusionSection
          title="✅ 採用すべき論点"
          items={session.editor_conclusion.adopt}
          color="#1D9E75"
        />
        <ConclusionSection
          title="⏸ 保留すべき論点"
          items={session.editor_conclusion.hold}
          color="#FF9800"
        />
        <ConclusionSection
          title="🔍 追加調査"
          items={session.editor_conclusion.research}
          color="#2196F3"
        />
      </div>
    </div>
  );
}

function ConclusionSection({
  title,
  items,
  color,
}: {
  title: string;
  items: string[];
  color: string;
}) {
  if (!items || items.length === 0) return null;
  return (
    <div className="mb-4 last:mb-0">
      <div className="text-xs font-semibold mb-2" style={{ color }}>
        {title}
      </div>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li
            key={i}
            className="text-text-secondary text-xs leading-relaxed pl-3 relative"
          >
            <span
              className="absolute left-0 top-1.5 w-1 h-1 rounded-full"
              style={{ backgroundColor: color }}
            />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
