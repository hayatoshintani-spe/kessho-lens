'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { fetchReport } from '@/lib/api';
import MarkdownReport from '@/components/reports/MarkdownReport';
import type { DailyReport } from '@/lib/types';
import { formatDate, formatPct, AGENT_NAMES, AGENT_COLORS, cn } from '@/lib/utils';
import { ChevronLeft, TrendingUp, TrendingDown, FileText } from 'lucide-react';

const MOCK_REPORT: DailyReport = {
  date: '2026-05-14',
  title: '日次投資レポート — 米金利高止まりと輸出株戦略',
  content: `# AI投資ファンド 日次レポート

**日付:** 2026年5月14日
**市場テーマ:** 米金利動向と日本株への影響

---

## 市場環境サマリー

本日は米FOMC議事録の公開を受け、年内2回の追加利上げが示唆されました。これを受けてドル円は152円台に上昇し、日経平均は輸出関連株に支えられ**前日比+0.8%**の堅調な展開となりました。

主要な市場動向：
- 日経225: +0.8%
- ドル円: 152.30円（円安進行）
- 10年国債利回り: 0.92%

---

## AIエージェント投資判断

### バフェットAI（価値投資）

本質的価値分析に基づき、トヨタ自動車（7203）を追加購入しました。

**判断根拠:**
- 円安による営業利益改善（1円/ドルの円安で約500億円の増益効果）
- EV転換期における技術的競争優位性
- PBR 1.2倍という歴史的低水準のバリュエーション

> 「短期的な金利変動より、企業の10年後の姿を想像することが重要。トヨタの製造技術と強固なキャッシュフローは揺るぎない。」

### ソロスAI（マクロ投資）

反射性理論に基づき、米金利高止まりによる円安継続トレンドを確信し、**輸出関連株のウェイトを5%引き上げ**ました。

**判断根拠:**
- 市場参加者の「利上げ継続」認識が自己強化的に作用
- 日本輸出企業の業績改善サイクルは継続中
- リスク/リワード比が輸出株に有利

### リンチAI（グロース投資）

AI活用クラウドサービス企業を新たに発掘しました。業績の急速な加速を確認しウォッチリストへ追加。

**発掘銘柄の特徴:**
- 四半期売上成長率: **+45% YoY**
- 既存顧客の継続率（NRR）: 128%
- 日本市場でのAI活用需要急増を背景に急成長中

### フラットAI（インデックス）

四半期定期リバランスを実施。規律ある機械的投資を継続。

---

## ポートフォリオ変更サマリー

| エージェント | アクション | 変更内容 |
|---|---|---|
| バフェットAI | 買い増し | トヨタ自動車 +200株 |
| ソロスAI | ウェイト調整 | 輸出関連 +5% |
| リンチAI | ウォッチリスト追加 | AI企業 3銘柄 |
| フラットAI | リバランス | ETF比率調整 |

---

## リスク要因

1. **地政学リスク**: 中東情勢の不安定化が原油価格に影響する可能性
2. **円安加速リスク**: 介入警戒ラインを超えた場合の急反転リスク
3. **決算ミス**: 好業績期待が織り込まれた銘柄の下方修正リスク

---

## 明日の注目ポイント

- 米国CPI発表（予想+3.2% YoY）
- 日銀総裁発言（金融政策変更示唆の有無）
- トヨタグループ月次生産台数

---

*本レポートはAI投資ファンドの教育的シミュレーションです。実際の投資判断には使用しないでください。*`,
  agentSummaries: {
    buffett: {
      agentId: 'buffett',
      summary: '価値投資原則に基づき、円安恩恵を受けるトヨタ自動車を割安と判断し追加購入。長期的な企業価値向上を確信。',
      decisions: ['トヨタ自動車 +200株', 'キャッシュ比率 9.6%に低下'],
      pnlChange: 0.3,
    },
    soros: {
      agentId: 'soros',
      summary: 'マクロ分析から円安継続を確信。輸出関連株を中心にポジション拡大。本日最大の積極的行動。',
      decisions: ['輸出関連株ウェイト +5%', 'ホンダ技研工業 +100株', 'キーエンス +5株'],
      pnlChange: 1.2,
    },
    lynch: {
      agentId: 'lynch',
      summary: 'AI活用SaaS企業3社を新規発掘。高成長率と市場浸透余地を評価。次回会議で購入判断へ。',
      decisions: ['AI企業3社をウォッチリストへ追加', '既存ポジション変更なし'],
      pnlChange: 0.1,
    },
    flat: {
      agentId: 'flat',
      summary: '規律あるインデックス投資を継続。四半期リバランスで比率調整。感情的判断ゼロ。',
      decisions: ['日経225 ETF 定期購入', 'TOPIX ETF リバランス'],
      pnlChange: 0.2,
    },
  },
  totalFundReturn: 2.1,
  marketTheme: '米金利動向と日本株への影響',
};

export default function ReportDetailPage({
  params,
}: {
  params: { date: string };
}) {
  const { date } = params;
  const [report, setReport] = useState<DailyReport>({ ...MOCK_REPORT, date });

  useEffect(() => {
    fetchReport(date).then(data => { if (data) setReport(data); }).catch(() => {});
  }, [date]);

  const isFundProfit = report.totalFundReturn >= 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back */}
      <Link
        href="/reports"
        className="inline-flex items-center gap-1.5 text-text-muted hover:text-text-primary text-sm transition-colors"
      >
        <ChevronLeft className="w-4 h-4" />
        レポート一覧
      </Link>

      {/* Report header */}
      <div className="card p-6">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-accent-gold/15 border border-accent-gold/30 flex items-center justify-center flex-shrink-0">
            <FileText className="w-5 h-5 text-accent-gold" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-text-muted text-xs mb-1">{formatDate(report.date)}</div>
            <h1 className="text-text-primary text-xl font-bold leading-tight">
              {report.title}
            </h1>
            {report.marketTheme && (
              <p className="text-accent-gold text-sm mt-1.5">{report.marketTheme}</p>
            )}
          </div>
          <div className="flex-shrink-0 text-right">
            <div className="text-text-muted text-[10px] uppercase tracking-wider mb-1">
              ファンドリターン
            </div>
            <div
              className={cn(
                'text-xl font-bold font-tabular flex items-center gap-1',
                isFundProfit ? 'text-profit' : 'text-loss',
              )}
            >
              {isFundProfit ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {formatPct(report.totalFundReturn)}
            </div>
          </div>
        </div>
      </div>

      {/* Agent summaries */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
        {Object.entries(report.agentSummaries).map(([agentId, summary]) => {
          const color = AGENT_COLORS[agentId as keyof typeof AGENT_COLORS] ?? '#7B7F8C';
          const isProfit = summary.pnlChange >= 0;
          return (
            <div
              key={agentId}
              className="card p-4"
              style={{ borderColor: color + '33' }}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                  style={{ backgroundColor: color }}
                >
                  {AGENT_NAMES[agentId as keyof typeof AGENT_NAMES]?.en.charAt(0)}
                </div>
                <div className="min-w-0">
                  <div className="text-text-primary text-xs font-semibold truncate">
                    {AGENT_NAMES[agentId as keyof typeof AGENT_NAMES]?.ja}
                  </div>
                </div>
                <div
                  className={cn(
                    'text-xs font-bold font-tabular ml-auto',
                    isProfit ? 'text-profit' : 'text-loss',
                  )}
                >
                  {formatPct(summary.pnlChange)}
                </div>
              </div>
              <p className="text-text-secondary text-xs leading-relaxed mb-2">
                {summary.summary}
              </p>
              <div className="space-y-0.5">
                {summary.decisions.map((d, i) => (
                  <div key={i} className="flex items-start gap-1.5">
                    <div
                      className="w-1 h-1 rounded-full mt-1.5 flex-shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-text-muted text-[10px] leading-relaxed">{d}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Markdown content */}
      <div className="card p-6 lg:p-8">
        <MarkdownReport content={report.content} />
      </div>
    </div>
  );
}
