import Link from 'next/link';
import { fetchAgents } from '@/lib/api';
import type { Agent } from '@/lib/types';
import { formatPct, formatLargeNumber, cn } from '@/lib/utils';
import Badge from '@/components/ui/Badge';
import { ArrowRight, TrendingUp, TrendingDown, Users } from 'lucide-react';

// Mock data fallback
const MOCK_AGENTS: Agent[] = [
  {
    id: 'buffett',
    name: 'BuffettAI',
    nameJa: 'バフェットAI',
    personality: 'ウォーレン・バフェットの投資哲学に基づいたAI。企業の本質的価値を重視し、割安で質の高いビジネスへの長期的な集中投資を行う。短期の市場変動に惑わされず、時間を味方につけた複利効果を最大化する。',
    style: '価値投資',
    color: '#4CAF50',
    portfolio: { totalValue: 12_500_000, cash: 1_200_000, holdings: [] },
    totalReturn: 8.3,
    totalReturnAbs: 960_000,
    rank: 2,
    beliefs: [
      '企業の本質的価値に基づいて投資する',
      '素晴らしい企業を公正な価格で買う',
      '理解できないビジネスには投資しない',
      '長期保有でリターンを最大化する',
      '市場の短期変動は無視する',
    ],
    recentDecision: 'トヨタ自動車を追加購入。EV転換期における競争優位性を評価。',
  },
  {
    id: 'soros',
    name: 'SorosAI',
    nameJa: 'ソロスAI',
    personality: 'ジョージ・ソロスのマクロ経済アプローチに基づいたAI。グローバルな経済動向と市場の歪みを捉え、大胆なポジションを取る。反射性理論に基づき、市場参加者の認識が市場を動かすことを理解した上で戦略を立てる。',
    style: 'マクロ投資',
    color: '#E91E63',
    portfolio: { totalValue: 15_200_000, cash: 3_000_000, holdings: [] },
    totalReturn: 14.7,
    totalReturnAbs: 1_970_000,
    rank: 1,
    beliefs: [
      '市場は常に誤っている',
      '認識と現実のギャップを利用する',
      'トレンドに乗り、反転を見極める',
      'リスク管理が最優先',
      '誤りを認め、素早く撤退する',
    ],
    recentDecision: '円安トレンドを捉え、輸出関連株を大幅買い増し。',
  },
  {
    id: 'lynch',
    name: 'LynchAI',
    nameJa: 'リンチAI',
    personality: 'ピーター・リンチのグロース投資哲学に基づいたAI。身近なビジネスから成長株を発掘し、多様なポートフォリオを構築する。10倍株（テンバガー）を発掘するために、成長ストーリーと財務データを組み合わせて分析する。',
    style: 'グロース投資',
    color: '#2196F3',
    portfolio: { totalValue: 11_800_000, cash: 800_000, holdings: [] },
    totalReturn: 6.1,
    totalReturnAbs: 675_000,
    rank: 3,
    beliefs: [
      '自分が知っている企業に投資する',
      '成長ストーリーを深く理解する',
      '適切な価格で優良成長株を買う',
      '多様なセクターに分散投資する',
      '10倍株を1つ見つけるために多く調査する',
    ],
    recentDecision: 'AI関連中小型株を新規発掘。業績成長率が市場予想を大幅上回る。',
  },
  {
    id: 'flat',
    name: 'FlatAI',
    nameJa: 'フラットAI',
    personality: 'インデックス運用に基づいたAI。市場全体の動きに連動し、分散投資でリスクを最小化するベンチマーク戦略を採用する。低コストで確実な市場平均リターンの獲得を目指し、感情的な判断を排除した機械的なリバランスを実施する。',
    style: 'インデックス',
    color: '#9E9E9E',
    portfolio: { totalValue: 10_500_000, cash: 500_000, holdings: [] },
    totalReturn: 3.2,
    totalReturnAbs: 325_000,
    rank: 4,
    beliefs: [
      '市場平均を長期的に上回ることは難しい',
      '低コストで市場全体に投資する',
      '分散投資でリスクを最小化する',
      '感情ではなく規律でリバランスする',
      '時間が最大の武器である',
    ],
    recentDecision: '日経225連動ETFを定期購入。ポートフォリオのリバランスを実施。',
  },
];

export default async function AgentsPage() {
  let agents: Agent[] = MOCK_AGENTS;

  try {
    const data = await fetchAgents();
    if (data.length > 0) agents = data;
  } catch {
    // fallback to mock
  }

  const sorted = [...agents].sort((a, b) => a.rank - b.rank);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-text-primary text-xl font-bold flex items-center gap-2">
          <Users className="w-5 h-5 text-accent-gold" />
          AIエージェント
        </h1>
        <p className="text-text-muted text-sm mt-0.5">
          各AIの投資哲学、実績、保有銘柄を確認する
        </p>
      </div>

      {/* Agent grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {sorted.map((agent) => {
          const isProfit = agent.totalReturn >= 0;
          return (
            <Link key={agent.id} href={`/agents/${agent.id}`}>
              <div
                className="card p-6 hover:border-[color:var(--a-color)] transition-all duration-200 cursor-pointer group h-full"
                style={{ '--a-color': agent.color + '55' } as React.CSSProperties}
              >
                {/* Top */}
                <div className="flex items-start gap-4 mb-5">
                  <div
                    className="w-14 h-14 rounded-xl flex items-center justify-center text-xl font-bold text-white flex-shrink-0"
                    style={{
                      backgroundColor: agent.color,
                      boxShadow: `0 0 20px ${agent.color}44`,
                    }}
                  >
                    {agent.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-text-primary font-bold text-base">{agent.nameJa}</h2>
                      <Badge variant="gold" size="sm">{agent.rank}位</Badge>
                    </div>
                    <div className="text-text-muted text-xs mt-0.5 font-mono">{agent.name}</div>
                    <Badge variant="custom" color={agent.color} size="sm" className="mt-1.5">
                      {agent.style}
                    </Badge>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div
                      className={cn(
                        'text-xl font-bold font-tabular flex items-center gap-1',
                        isProfit ? 'text-profit' : 'text-loss',
                      )}
                    >
                      {isProfit ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      {formatPct(agent.totalReturn)}
                    </div>
                    <div className="text-text-muted text-[11px] font-tabular mt-0.5">
                      {isProfit ? '+' : ''}
                      {formatLargeNumber(agent.totalReturnAbs)}
                    </div>
                  </div>
                </div>

                {/* Personality */}
                <p className="text-text-secondary text-sm leading-relaxed mb-4 line-clamp-3">
                  {agent.personality}
                </p>

                {/* Beliefs */}
                <div className="space-y-1.5 mb-4">
                  {(agent.beliefs ?? []).slice(0, 3).map((b, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <div
                        className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
                        style={{ backgroundColor: agent.color }}
                      />
                      <span className="text-text-muted text-xs leading-relaxed">{b}</span>
                    </div>
                  ))}
                </div>

                {/* Portfolio info */}
                <div className="pt-4 border-t border-border flex items-center justify-between">
                  <div className="text-text-muted text-xs">
                    運用資産:{' '}
                    <span className="text-text-secondary font-tabular">
                      {formatLargeNumber(agent.portfolio.totalValue)}
                    </span>
                  </div>
                  <div className="flex items-center text-text-muted text-xs group-hover:text-accent-gold transition-colors">
                    詳細 <ArrowRight className="w-3 h-3 ml-1" />
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
