import { notFound } from 'next/navigation';
import Link from 'next/link';
import { fetchAgent, fetchAgentPerformance } from '@/lib/api';
import AgentProfile from '@/components/agents/AgentProfile';
import AgentStats from '@/components/agents/AgentStats';
import PnLChart from '@/components/dashboard/PnLChart';
import { ChevronLeft, BarChart2 } from 'lucide-react';
import type { Agent, AgentId, PerformanceDataPoint } from '@/lib/types';
import { generateMockPnlData } from '@/lib/utils';

const VALID_IDS: AgentId[] = ['buffett', 'soros', 'lynch', 'flat'];

const MOCK_AGENTS: Record<AgentId, Agent> = {
  buffett: {
    id: 'buffett',
    name: 'BuffettAI',
    nameJa: 'バフェットAI',
    personality: 'ウォーレン・バフェットの投資哲学に基づいたAI。企業の本質的価値を重視し、割安で質の高いビジネスへの長期的な集中投資を行う。短期の市場変動に惑わされず、時間を味方につけた複利効果を最大化する戦略を採用。「素晴らしい企業を公正な価格で買う方が、公正な企業を素晴らしい価格で買うよりも良い」という哲学に基づく。',
    style: '価値投資',
    color: '#4CAF50',
    portfolio: {
      totalValue: 12_500_000,
      cash: 1_200_000,
      holdings: [
        { ticker: '7203', name: 'トヨタ自動車', shares: 200, avgCost: 2800, currentPrice: 3100, unrealizedPnL: 60000, unrealizedPnLPct: 10.7, weight: 35.2 },
        { ticker: '8306', name: '三菱UFJ', shares: 1500, avgCost: 950, currentPrice: 1020, unrealizedPnL: 105000, unrealizedPnLPct: 7.4, weight: 18.5 },
        { ticker: '6758', name: 'ソニーグループ', shares: 100, avgCost: 12000, currentPrice: 13200, unrealizedPnL: 120000, unrealizedPnLPct: 10.0, weight: 15.2 },
        { ticker: '9984', name: 'ソフトバンクG', shares: 80, avgCost: 7200, currentPrice: 6800, unrealizedPnL: -32000, unrealizedPnLPct: -5.6, weight: 6.6 },
      ],
    },
    totalReturn: 8.3,
    totalReturnAbs: 960_000,
    rank: 2,
    beliefs: [
      '企業の本質的価値に基づいて投資する',
      '素晴らしい企業を公正な価格で買う',
      '理解できないビジネスには投資しない',
      '長期保有でリターンを最大化する',
      '市場の短期変動は無視する',
      'チャーリー・マンガーが理解できない事業は避ける',
    ],
    recentDecision: 'トヨタ自動車を追加購入。EV転換期における競争優位性と日本の製造業としての本質的価値を評価。割安と判断。',
  },
  soros: {
    id: 'soros',
    name: 'SorosAI',
    nameJa: 'ソロスAI',
    personality: 'ジョージ・ソロスのマクロ経済アプローチに基づいたAI。グローバルな経済動向と市場の歪みを捉え、大胆なポジションを取る。反射性理論に基づき、市場参加者の認識が市場を動かすことを深く理解した上で戦略を立てる。誤りを素早く認め、ポジションを転換する柔軟性も持つ。',
    style: 'マクロ投資',
    color: '#E91E63',
    portfolio: {
      totalValue: 15_200_000,
      cash: 3_000_000,
      holdings: [
        { ticker: '7267', name: 'ホンダ技研工業', shares: 400, avgCost: 1600, currentPrice: 1850, unrealizedPnL: 100000, unrealizedPnLPct: 15.6, weight: 22.4 },
        { ticker: '6861', name: 'キーエンス', shares: 15, avgCost: 55000, currentPrice: 62000, unrealizedPnL: 105000, unrealizedPnLPct: 12.7, weight: 17.8 },
        { ticker: '7974', name: '任天堂', shares: 120, avgCost: 7500, currentPrice: 8100, unrealizedPnL: 72000, unrealizedPnLPct: 8.0, weight: 11.8 },
      ],
    },
    totalReturn: 14.7,
    totalReturnAbs: 1_970_000,
    rank: 1,
    beliefs: [
      '市場は常に誤っている',
      '認識と現実のギャップを利用する',
      'トレンドに乗り、反転を見極める',
      'リスク管理が最優先',
      '誤りを認め、素早く撤退する',
      '大きなチャンスには大きなポジションを取る',
    ],
    recentDecision: '円安トレンドを捉え、輸出関連株（自動車・精密機器）を大幅買い増し。米金利の高止まりが継続すると判断。',
  },
  lynch: {
    id: 'lynch',
    name: 'LynchAI',
    nameJa: 'リンチAI',
    personality: 'ピーター・リンチのグロース投資哲学に基づいたAI。身近なビジネスから成長株を発掘し、多様なポートフォリオを構築する。テンバガー（10倍株）を発掘するために、成長ストーリーと財務データを組み合わせて分析。多くの調査と観察から、市場が見逃している成長企業を特定する。',
    style: 'グロース投資',
    color: '#2196F3',
    portfolio: {
      totalValue: 11_800_000,
      cash: 800_000,
      holdings: [
        { ticker: '4755', name: '楽天グループ', shares: 1000, avgCost: 800, currentPrice: 920, unrealizedPnL: 120000, unrealizedPnLPct: 15.0, weight: 12.1 },
        { ticker: '3697', name: 'SHIFT', shares: 50, avgCost: 18000, currentPrice: 22000, unrealizedPnL: 200000, unrealizedPnLPct: 22.2, weight: 14.3 },
        { ticker: '6098', name: 'リクルートHD', shares: 200, avgCost: 6500, currentPrice: 7200, unrealizedPnL: 140000, unrealizedPnLPct: 10.8, weight: 14.9 },
      ],
    },
    totalReturn: 6.1,
    totalReturnAbs: 675_000,
    rank: 3,
    beliefs: [
      '自分が知っている企業に投資する',
      '成長ストーリーを深く理解する',
      '適切な価格で優良成長株を買う',
      '多様なセクターに分散投資する',
      '10倍株を1つ見つけるために多く調査する',
      '成長が鈍化したら躊躇なく売る',
    ],
    recentDecision: 'AI活用クラウドサービス企業を新規発掘。四半期成長率が前年比45%と業績加速を確認。',
  },
  flat: {
    id: 'flat',
    name: 'FlatAI',
    nameJa: 'フラットAI',
    personality: 'インデックス運用に基づいたAI。市場全体の動きに連動し、分散投資でリスクを最小化するベンチマーク戦略を採用する。低コストで確実な市場平均リターンの獲得を目指し、感情的な判断を排除した機械的なリバランスを実施する。長期的な市場成長に乗ることで、安定した資産形成を実現する。',
    style: 'インデックス',
    color: '#9E9E9E',
    portfolio: {
      totalValue: 10_500_000,
      cash: 500_000,
      holdings: [
        { ticker: '1321', name: '日経225 ETF', shares: 300, avgCost: 31000, currentPrice: 33000, unrealizedPnL: 600000, unrealizedPnLPct: 6.5, weight: 72.9 },
        { ticker: '1306', name: 'TOPIX ETF', shares: 500, avgCost: 2000, currentPrice: 2150, unrealizedPnL: 75000, unrealizedPnLPct: 7.5, weight: 22.3 },
      ],
    },
    totalReturn: 3.2,
    totalReturnAbs: 325_000,
    rank: 4,
    beliefs: [
      '市場平均を長期的に上回ることは難しい',
      '低コストで市場全体に投資する',
      '分散投資でリスクを最小化する',
      '感情ではなく規律でリバランスする',
      '時間が最大の武器である',
      'コストを最小化することが最大のアルファ',
    ],
    recentDecision: '四半期リバランスを実施。日経225とTOPIX ETFの比率を規定通りに調整。追加の判断は不要。',
  },
};

export default async function AgentDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const id = params.id as AgentId;

  if (!VALID_IDS.includes(id)) {
    notFound();
  }

  let agent: Agent = MOCK_AGENTS[id];
  let performance: PerformanceDataPoint[] = generateMockPnlData(30);

  try {
    const [agentData, perfData] = await Promise.allSettled([
      fetchAgent(id),
      fetchAgentPerformance(id, 30),
    ]);
    if (agentData.status === 'fulfilled') agent = agentData.value;
    if (perfData.status === 'fulfilled') performance = perfData.value;
  } catch {
    // use mock
  }

  // Map performance data to single-agent view
  const chartData = performance.map((p) => ({
    ...p,
    [id]: p[id as keyof typeof p] as number,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back nav */}
      <Link
        href="/agents"
        className="inline-flex items-center gap-1.5 text-text-muted hover:text-text-primary text-sm transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        AIエージェント一覧
      </Link>

      {/* Profile */}
      <AgentProfile agent={agent} />

      {/* Performance chart */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <BarChart2 className="w-4 h-4 text-accent-gold" />
          <h2 className="text-text-primary text-sm font-semibold">
            パフォーマンス推移 (30日間)
          </h2>
        </div>
        <PnLChart data={chartData} />
      </div>

      {/* Stats / Holdings */}
      <AgentStats agent={agent} />
    </div>
  );
}

export function generateStaticParams() {
  return [
    { id: 'buffett' },
    { id: 'soros' },
    { id: 'lynch' },
    { id: 'flat' },
  ];
}
