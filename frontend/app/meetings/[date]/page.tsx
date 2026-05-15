'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { fetchMeeting } from '@/lib/api';
import MeetingDetail from '@/components/meetings/MeetingDetail';
import { ChevronLeft } from 'lucide-react';
import type { MeetingLog } from '@/lib/types';

const MOCK_MEETING: MeetingLog = {
  date: '2026-05-14',
  participants: ['buffett', 'soros', 'lynch', 'flat'],
  summary: '米連邦準備制度の利上げ示唆を受けた市場反応と、日本株の底堅さについて議論。輸出関連株のウェイト引き上げで合意。',
  keyDecisions: [
    '輸出関連株のウェイトを5%増加',
    'テクノロジーセクターは現状維持',
    '次回会議まで新規購入を慎重に検討',
    'リスク管理のためキャッシュ比率10%を維持',
  ],
  marketTheme: '米金利動向と日本株への影響',
  duration: '25分',
  messages: [
    {
      agent: 'soros',
      time: '09:00:00',
      content: '本日の議題は米FOMC議事録の内容と日本市場への影響です。昨夜発表された内容では、年内2回の追加利上げが示唆されました。これが日本株にどう影響するか、各エージェントの見解を聞かせてください。',
      type: 'opening',
    },
    {
      agent: 'buffett',
      time: '09:02:33',
      content: 'FOMCの内容は短期的なノイズに過ぎません。私が注目しているのは企業の本質的な収益力です。トヨタやホンダは円安恩恵で業績が改善しており、長期的な価値は揺るぎません。金利動向に一喜一憂するより、5年後の企業価値を考えるべきです。',
      type: 'debate',
    },
    {
      agent: 'lynch',
      time: '09:04:12',
      content: '興味深い点があります。この金利環境でも高成長を維持しているAI関連企業がいくつかあります。先日スキャンした中に、四半期成長率45%の中型SaaS企業がありました。金利敏感度が低い高成長企業は例外的な存在です。',
      type: 'analysis',
    },
    {
      agent: 'soros',
      time: '09:06:55',
      content: 'バフェットAIの意見に半分同意しますが、反射性理論の観点では、市場参加者の「金利上昇 = 株安」という認識が自己実現的に機能します。ただし、その認識の歪みを利用できます。米金利高止まりによる円安継続が輸出企業に恩恵をもたらすと判断し、輸出株への投資比率を5%引き上げることを提案します。',
      type: 'proposal',
    },
    {
      agent: 'flat',
      time: '09:09:20',
      content: 'インデックス観点では、TOPIX全体は金利感応度が中程度です。個別銘柄の選択より、セクター全体のトレンドに注目すべきです。輸出比率の引き上げには賛成しますが、過度な集中は避けるべきです。',
      type: 'rebuttal',
    },
    {
      agent: 'buffett',
      time: '09:11:45',
      content: 'ソロスAIの提案は理解できます。ただし、私のポートフォリオでは既にトヨタとホンダで輸出関連株が35%を占めています。追加購入は本質的価値に対して割安な銘柄に限定すべきと考えます。三菱商事の現在の価格は興味深い水準にあります。',
      type: 'debate',
    },
    {
      agent: 'lynch',
      time: '09:14:08',
      content: '輸出関連に加えて、国内消費の底堅さも注目すべきです。インバウンド恩恵を受ける観光・小売セクターも円安メリットがあります。ウォッチリストに追加することを提案します。',
      type: 'proposal',
    },
    {
      agent: 'soros',
      time: '09:15:30',
      content: '議論の結果をまとめます。①輸出関連株の比率を5%引き上げることで全員合意。②テクノロジーセクターは現状維持。③リンチAIが提案した小売・観光株はウォッチリストへ。④キャッシュ比率は10%を維持。これで本日の会議を締めくくります。',
      type: 'decision',
    },
    {
      agent: 'flat',
      time: '09:16:00',
      content: '以上の決定に基づき、次の定期リバランスで調整を実施します。規律ある投資継続が重要です。',
      type: 'closing',
    },
  ],
};

export default function MeetingDetailPage({
  params,
}: {
  params: { date: string };
}) {
  const { date } = params;
  const [meeting, setMeeting] = useState<MeetingLog>({
    ...MOCK_MEETING,
    date,
  });

  useEffect(() => {
    fetchMeeting(date).then(data => { if (data) setMeeting(data); }).catch(() => {});
  }, [date]);

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      {/* Back */}
      <Link
        href="/meetings"
        className="inline-flex items-center gap-1.5 text-text-muted hover:text-text-primary text-sm transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        会議ログ一覧
      </Link>

      <MeetingDetail meeting={meeting} />
    </div>
  );
}
