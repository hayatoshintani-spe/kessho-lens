'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  fetchAgents,
  fetchFundStats,
  fetchPerformance,
  fetchLatestMeeting,
  fetchLatestReport,
} from '@/lib/api';
import {
  generateMockPnlData,
  formatDate,
} from '@/lib/utils';
import AgentCard from '@/components/dashboard/AgentCard';
import PnLChart from '@/components/dashboard/PnLChart';
import RankingTable from '@/components/dashboard/RankingTable';
import MarketStatus from '@/components/dashboard/MarketStatus';
import { ArrowRight, BarChart2, MessageSquare, FileText } from 'lucide-react';
import type { Agent, FundStats, PerformanceDataPoint, MeetingLog, DailyReport } from '@/lib/types';

// ─── Mock fallback data ────────────────────────────────────────────────────────

const MOCK_AGENTS: Agent[] = [
  {
    id: 'buffett',
    name: 'BuffettAI',
    nameJa: 'バフェットAI',
    personality: '割安優良株への長期投資を信条とする価値投資家AI。企業の本質的価値を重視し、市場の短期的な変動に動じない。',
    style: '価値投資',
    color: '#4CAF50',
    portfolio: { totalValue: 12_500_000, cash: 1_200_000, holdings: [] },
    totalReturn: 8.3,
    totalReturnAbs: 960_000,
    rank: 2,
    beliefs: ['企業の本質的価値に基づいて投資する', '長期保有でリターンを最大化する', '理解できないビジネスには投資しない'],
    recentDecision: 'トヨタ自動車を追加購入。EV転換期における競争優位性を評価。',
  },
  {
    id: 'soros',
    name: 'SorosAI',
    nameJa: 'ソロスAI',
    personality: 'マクロ経済の歪みと市場心理を読むグローバル投資家AI。大胆なポジションと素早い方向転換で市場を攻略する。',
    style: 'マクロ投資',
    color: '#E91E63',
    portfolio: { totalValue: 15_200_000, cash: 3_000_000, holdings: [] },
    totalReturn: 14.7,
    totalReturnAbs: 1_970_000,
    rank: 1,
    beliefs: ['市場は常に誤っている', 'トレンドに乗り、反転を見極める', 'リスク管理が最優先'],
    recentDecision: '円安トレンドを捉え、輸出関連株を大幅買い増し。',
  },
  {
    id: 'lynch',
    name: 'LynchAI',
    nameJa: 'リンチAI',
    personality: '身近なビジネスから成長株を発掘するグロース投資家AI。多様な業種に目を向け、テンバガーを狙う。',
    style: 'グロース投資',
    color: '#2196F3',
    portfolio: { totalValue: 11_800_000, cash: 800_000, holdings: [] },
    totalReturn: 6.1,
    totalReturnAbs: 675_000,
    rank: 3,
    beliefs: ['知っている企業に投資する', '成長ストーリーを理解する', '適切な価格で優良成長株を買う'],
    recentDecision: 'AI関連中小型株を新規発掘。業績成長率が市場予想を大幅上回る。',
  },
  {
    id: 'flat',
    name: 'FlatAI',
    nameJa: 'フラットAI',
    personality: 'インデックス連動の安定運用を目指すベンチマーク型AI。低コストで市場全体のリターンを確実に獲得する。',
    style: 'インデックス',
    color: '#9E9E9E',
    portfolio: { totalValue: 10_500_000, cash: 500_000, holdings: [] },
    totalReturn: 3.2,
    totalReturnAbs: 325_000,
    rank: 4,
    beliefs: ['市場平均を上回ることは難しい', '分散投資でリスクを分散する', '低コストで長期運用する'],
    recentDecision: '日経225連動ETFを定期購入。ポートフォリオのリバランスを実施。',
  },
];

const MOCK_STATS: FundStats = {
  totalAum: 50_000_000,
  inception: '2024-01-01',
  totalReturn: 8.1,
  bestAgent: 'soros',
  worstAgent: 'flat',
  lastUpdated: new Date().toISOString(),
};

const MOCK_MEETING: MeetingLog = {
  date: '2026-05-14',
  participants: ['buffett', 'soros', 'lynch', 'flat'],
  summary: '本日の会議では、米連邦準備制度の利上げ示唆を受けた市場反応と、日本株の底堅さについて議論。各エージェントが異なる視点から現在のポートフォリオ戦略を検討した。',
  keyDecisions: [
    '輸出関連株のウェイトを5%増加',
    'テクノロジーセクターは現状維持',
    '次回会議まで新規購入を慎重に検討',
  ],
  marketTheme: '米金利動向と日本株への影響',
  messages: [],
};

// ─── Dashboard Page ────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [agents, setAgents] = useState<Agent[]>(MOCK_AGENTS);
  const [stats, setStats] = useState<FundStats>(MOCK_STATS);
  const [performance, setPerformance] = useState<PerformanceDataPoint[]>(generateMockPnlData(30));
  const [latestMeeting, setLatestMeeting] = useState<MeetingLog | null>(MOCK_MEETING);
  const [latestReport, setLatestReport] = useState<DailyReport | null>(null);
  const [isLive, setIsLive] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);
  const [debugError, setDebugError] = useState<string | null>(null);

  useEffect(() => {
    const t0 = Date.now();
    Promise.allSettled([
      fetchAgents(),
      fetchFundStats(),
      fetchPerformance(30),
      fetchLatestMeeting(),
      fetchLatestReport(),
    ]).then(([agentsData, statsData, perfData, meetingData, reportData]) => {
      const elapsed = Date.now() - t0;
      if (agentsData.status === 'fulfilled') { setAgents(agentsData.value); setIsLive(true); }
      else { setDebugError(`[${elapsed}ms] ${(agentsData.reason as Error)?.message ?? 'unknown'}`); }
      if (statsData.status === 'fulfilled') { setStats(statsData.value); }
      if (perfData.status === 'fulfilled') { setPerformance(perfData.value); }
      if (meetingData.status === 'fulfilled') { setLatestMeeting(meetingData.value); }
      if (reportData.status === 'fulfilled') { setLatestReport(reportData.value); }
      setIsConnecting(false);
    });
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-text-primary text-xl font-bold">ダッシュボード</h1>
          <p className="text-text-muted text-sm mt-0.5">
            4つのAIエージェントによる日次投資シミュレーション
          </p>
        </div>
        {isConnecting ? (
          <div className="bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs px-3 py-1.5 rounded-md animate-pulse">
            接続中...
          </div>
        ) : !isLive ? (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs px-3 py-1.5 rounded-md max-w-[200px] truncate">
            {debugError ?? 'バックエンド未接続'}
          </div>
        ) : null}
      </div>

      {/* Agent cards grid */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-text-secondary text-sm font-medium">AIエージェント</h2>
          <Link
            href="/agents"
            className="text-text-muted hover:text-accent-gold text-xs flex items-center gap-1 transition-colors"
          >
            すべて見る <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 relative">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </section>

      {/* Chart + Ranking row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 card p-5">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-4 h-4 text-accent-gold" />
            <h2 className="text-text-primary text-sm font-semibold">累積リターン推移 (30日間)</h2>
          </div>
          <PnLChart data={performance} />
        </div>
        <div className="card p-5">
          <h2 className="text-text-primary text-sm font-semibold mb-4">現在ランキング</h2>
          <RankingTable agents={agents} />
        </div>
      </div>

      {/* Market Status + Latest Meeting */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <MarketStatus
          stats={stats}
          marketTheme={latestMeeting?.marketTheme}
        />

        {latestMeeting && (
          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-accent-gold" />
                <h3 className="text-text-primary text-sm font-semibold">最新会議</h3>
              </div>
              <Link
                href={`/meetings/${latestMeeting.date}`}
                className="text-text-muted hover:text-accent-gold text-xs flex items-center gap-1 transition-colors"
              >
                詳細 <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="text-text-muted text-xs mb-2">
              {formatDate(latestMeeting.date)}
            </div>
            {latestMeeting.marketTheme && (
              <div className="text-accent-gold text-xs font-medium mb-3">
                {latestMeeting.marketTheme}
              </div>
            )}
            <p className="text-text-secondary text-sm leading-relaxed mb-4">
              {latestMeeting.summary}
            </p>
            <div className="space-y-2">
              {latestMeeting.keyDecisions.slice(0, 3).map((d, i) => (
                <div key={i} className="flex items-start gap-2">
                  <div className="w-1 h-1 rounded-full bg-accent-gold mt-2 flex-shrink-0" />
                  <span className="text-text-secondary text-xs leading-relaxed">{d}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Latest Report link */}
      {latestReport && (
        <div className="card p-5 border-accent-gold/20 bg-accent-gold/5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-accent-gold" />
              <div>
                <div className="text-text-primary font-semibold text-sm">
                  最新レポート公開
                </div>
                <div className="text-text-muted text-xs mt-0.5">
                  {formatDate(latestReport.date)} — {latestReport.title}
                </div>
              </div>
            </div>
            <Link
              href={`/reports/${latestReport.date}`}
              className="flex items-center gap-1.5 text-accent-gold text-sm font-medium hover:text-accent-gold-light transition-colors"
            >
              読む <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
