'use client';

import { useState, useEffect } from 'react';
import { fetchMeetings } from '@/lib/api';
import MeetingCard from '@/components/meetings/MeetingCard';
import EmptyState from '@/components/ui/EmptyState';
import type { MeetingLog } from '@/lib/types';
import { MessageSquare } from 'lucide-react';

const MOCK_MEETINGS: MeetingLog[] = [
  {
    date: '2026-05-14',
    participants: ['buffett', 'soros', 'lynch', 'flat'],
    summary: '米連邦準備制度の利上げ示唆を受けた市場反応と、日本株の底堅さについて議論。輸出関連株のウェイト引き上げで合意。',
    keyDecisions: [
      '輸出関連株のウェイトを5%増加',
      'テクノロジーセクターは現状維持',
      '次回会議まで新規購入を慎重に検討',
    ],
    marketTheme: '米金利動向と日本株への影響',
    messages: [
      {
        agent: 'soros',
        time: '09:00:00',
        content: '本日の議題は米FOMC議事録の内容と日本市場への影響です。昨夜発表された内容を踏まえ、各エージェントの見解を聞かせてください。',
        type: 'opening',
      },
      {
        agent: 'buffett',
        time: '09:02:00',
        content: 'FOMCの内容は短期的なノイズに過ぎません。私が注目しているのは企業の本質的な収益力です。トヨタやホンダは円安恩恵で業績が改善しており、長期的な価値が高まっています。',
        type: 'debate',
      },
      {
        agent: 'soros',
        time: '09:05:00',
        content: 'バフェットAIの意見に半分同意しますが、マクロの観点では米金利の高止まりがドル円に与える影響を無視できません。輸出株への投資比率を引き上げることを提案します。',
        type: 'proposal',
      },
      {
        agent: 'lynch',
        time: '09:08:00',
        content: 'グロース株の観点からは、金利上昇はバリュエーションに影響します。ただし成長率の高いAI関連企業は例外で、先日発掘した銘柄は四半期成長率45%を達成しています。',
        type: 'analysis',
      },
      {
        agent: 'flat',
        time: '09:11:00',
        content: 'インデックス観点では、全体的な市場は横ばいです。個別銘柄の選択より、セクター全体のトレンドに注目すべきです。',
        type: 'rebuttal',
      },
      {
        agent: 'soros',
        time: '09:15:00',
        content: '議論の結果、輸出関連株の比率を5%引き上げることで合意します。テクノロジーセクターは現状維持。フラットAIの意見も踏まえ、新規購入は慎重に進めます。',
        type: 'decision',
      },
    ],
    duration: '25分',
  },
  {
    date: '2026-05-13',
    participants: ['buffett', 'soros', 'lynch', 'flat'],
    summary: '決算発表シーズンの総括と今後のポートフォリオ調整について討議。ソニーの好決算を受け保有比率の見直しを行う。',
    keyDecisions: [
      'ソニーグループの保有比率を2%増加',
      'エネルギーセクターへの新規投資を検討開始',
      '小型成長株3銘柄をウォッチリストに追加',
    ],
    marketTheme: '決算シーズン総括とセクターローテーション',
    messages: [],
    duration: '35分',
  },
  {
    date: '2026-05-12',
    participants: ['buffett', 'soros', 'lynch', 'flat'],
    summary: '地政学リスクの高まりとディフェンシブ株への資金流入について分析。各エージェントのリスク許容度の違いが鮮明に。',
    keyDecisions: [
      'ディフェンシブ株（食品・医薬品）の比率を検討',
      'キャッシュ比率を10%以上維持することで合意',
      '地政学リスク動向を毎日モニタリング',
    ],
    marketTheme: '地政学リスクとディフェンシブ戦略',
    messages: [],
    duration: '40分',
  },
];

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<MeetingLog[]>(MOCK_MEETINGS);

  useEffect(() => {
    fetchMeetings(1, 20).then(data => { if (data && data.items.length > 0) setMeetings(data.items); }).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-text-primary text-xl font-bold flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-accent-gold" />
          投資会議ログ
        </h1>
        <p className="text-text-muted text-sm mt-0.5">
          AIエージェント間の議論と意思決定プロセスを記録
        </p>
      </div>

      {/* Meeting list */}
      {meetings.length === 0 ? (
        <EmptyState
          icon={MessageSquare}
          title="会議ログがありません"
          description="シミュレーションを実行すると会議ログが記録されます"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {meetings.map((meeting) => (
            <MeetingCard key={meeting.date} meeting={meeting} />
          ))}
        </div>
      )}
    </div>
  );
}
