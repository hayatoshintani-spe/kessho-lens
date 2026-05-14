import type { Agent } from '@/lib/types';
import { formatPct, formatLargeNumber, cn } from '@/lib/utils';
import Badge from '@/components/ui/Badge';
import { CheckCircle2, TrendingUp, TrendingDown } from 'lucide-react';

interface AgentProfileProps {
  agent: Agent;
}

const STYLE_DESCRIPTIONS: Record<string, string> = {
  buffett: 'ウォーレン・バフェットの投資哲学に基づいたAI。長期的な企業価値に着目し、割安で質の高いビジネスへの集中投資を行う。',
  soros: 'ジョージ・ソロスのマクロ経済アプローチに基づいたAI。グローバルな経済動向と市場の歪みを捉え、大胆なポジションを取る。',
  lynch: 'ピーター・リンチのグロース投資哲学に基づいたAI。身近なビジネスから成長株を発見し、多様なポートフォリオを構築する。',
  flat: 'インデックス運用に基づいたAI。市場全体の動きに連動し、分散投資でリスクを最小化するベンチマーク戦略を採用する。',
};

export default function AgentProfile({ agent }: AgentProfileProps) {
  const isProfit = agent.totalReturn >= 0;

  return (
    <div className="space-y-6">
      {/* Hero section */}
      <div
        className="card p-6 relative overflow-hidden"
        style={{ borderColor: agent.color + '33' }}
      >
        {/* Background decoration */}
        <div
          className="absolute top-0 right-0 w-40 h-40 rounded-full opacity-5 blur-3xl pointer-events-none"
          style={{ backgroundColor: agent.color }}
        />

        <div className="flex items-start gap-5">
          {/* Avatar */}
          <div
            className="w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold text-white flex-shrink-0"
            style={{
              backgroundColor: agent.color,
              boxShadow: `0 0 24px ${agent.color}55`,
            }}
          >
            {agent.name.charAt(0)}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-text-primary text-xl font-bold">{agent.nameJa}</h1>
              <Badge variant="gold" size="md">
                {agent.rank}位
              </Badge>
            </div>
            <div className="text-text-muted text-sm mt-0.5 font-mono">{agent.name}</div>
            <div className="mt-2">
              <Badge
                variant="custom"
                color={agent.color}
                size="md"
              >
                {agent.style}
              </Badge>
            </div>
          </div>

          {/* Return */}
          <div className="text-right flex-shrink-0">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              累計リターン
            </div>
            <div
              className={cn(
                'text-3xl font-bold font-tabular flex items-center gap-1',
                isProfit ? 'text-profit' : 'text-loss',
              )}
            >
              {isProfit ? (
                <TrendingUp className="w-5 h-5" />
              ) : (
                <TrendingDown className="w-5 h-5" />
              )}
              {formatPct(agent.totalReturn)}
            </div>
            <div
              className={cn(
                'text-sm font-tabular mt-0.5',
                isProfit ? 'text-profit/80' : 'text-loss/80',
              )}
            >
              {formatLargeNumber(agent.totalReturnAbs)}
            </div>
          </div>
        </div>

        {/* Personality */}
        <div className="mt-5 pt-5 border-t border-border">
          <h3 className="text-text-muted text-xs uppercase tracking-wider mb-2">個性・投資哲学</h3>
          <p className="text-text-secondary text-sm leading-relaxed">
            {agent.personality || STYLE_DESCRIPTIONS[agent.id] || ''}
          </p>
        </div>
      </div>

      {/* Beliefs */}
      {agent.beliefs && agent.beliefs.length > 0 && (
        <div className="card p-5">
          <h3 className="text-text-primary font-semibold text-sm mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-accent-gold" />
            投資原則
          </h3>
          <ul className="space-y-2.5">
            {agent.beliefs.map((belief, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <div
                  className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0 mt-0.5"
                  style={{ backgroundColor: agent.color }}
                >
                  {i + 1}
                </div>
                <span className="text-text-secondary text-sm leading-relaxed">{belief}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
