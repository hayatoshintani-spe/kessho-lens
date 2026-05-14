import { fetchReports } from '@/lib/api';
import ReportCard from '@/components/reports/ReportCard';
import EmptyState from '@/components/ui/EmptyState';
import type { DailyReport } from '@/lib/types';
import { FileText } from 'lucide-react';

const MOCK_REPORTS: DailyReport[] = [
  {
    date: '2026-05-14',
    title: '日次投資レポート — 米金利高止まりと輸出株戦略',
    content: `# AI投資ファンド 日次レポート — 2026年5月14日

## 本日の市場環境

米FOMC議事録により年内2回の追加利上げが示唆され、ドル円は152円台に上昇。日経平均は輸出関連株に支えられ底堅い展開。

## 各AIエージェントの行動

### バフェットAI
本質的価値に基づき、トヨタ自動車を追加購入。円安恩恵と技術競争力を評価。

### ソロスAI
マクロ戦略として輸出関連株を5%引き上げ。ポートフォリオ全体のパフォーマンスをリード。

### リンチAI
AI関連中小型株を新規発掘。四半期成長率45%の企業をウォッチリストへ。

### フラットAI
インデックス比率を維持しつつ、定期リバランスを実施。

## ポートフォリオ変更

- 輸出関連株: +5%
- テクノロジー: 変動なし
- キャッシュ: 10%維持

## まとめ

4AIが協力し、市場環境に適応した投資判断を実施。`,
    agentSummaries: {
      buffett: { agentId: 'buffett', summary: 'トヨタ追加購入', decisions: ['トヨタ自動車 +200株'], pnlChange: 0.3 },
      soros: { agentId: 'soros', summary: '輸出株増加', decisions: ['輸出関連株 +5%'], pnlChange: 1.2 },
      lynch: { agentId: 'lynch', summary: '成長株発掘', decisions: ['AI企業ウォッチリスト追加'], pnlChange: 0.1 },
      flat: { agentId: 'flat', summary: 'リバランス実施', decisions: ['ETF定期購入'], pnlChange: 0.2 },
    },
    totalFundReturn: 2.1,
    marketTheme: '米金利動向と日本株への影響',
  },
  {
    date: '2026-05-13',
    title: '日次投資レポート — 決算シーズン総括',
    content: `# AI投資ファンド 日次レポート — 2026年5月13日

## 本日の市場環境

決算発表シーズンが佳境。ソニーグループが市場予想を上回る好決算を発表。

## 各AIエージェントの行動

本日の会議では決算内容の分析と今後の方針を策定した。

## まとめ

決算シーズンの良好な結果を受け、エンターテインメント・電機セクターへの注目が高まっている。`,
    agentSummaries: {
      buffett: { agentId: 'buffett', summary: '好決算評価', decisions: ['ソニー評価継続'], pnlChange: 0.8 },
      soros: { agentId: 'soros', summary: '決算プレー', decisions: ['エンタメ株強化'], pnlChange: 1.5 },
      lynch: { agentId: 'lynch', summary: '成長継続確認', decisions: ['ゲーム関連継続保有'], pnlChange: 0.6 },
      flat: { agentId: 'flat', summary: '市場連動', decisions: ['指数連動維持'], pnlChange: 0.4 },
    },
    totalFundReturn: 0.9,
    marketTheme: '決算シーズン総括とセクターローテーション',
  },
];

export default async function ReportsPage() {
  let reports: DailyReport[] = MOCK_REPORTS;

  try {
    const data = await fetchReports(1, 20);
    if (data.items.length > 0) reports = data.items;
  } catch {
    // fallback
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-text-primary text-xl font-bold flex items-center gap-2">
          <FileText className="w-5 h-5 text-accent-gold" />
          日次レポート
        </h1>
        <p className="text-text-muted text-sm mt-0.5">
          AIエージェントが毎日生成する投資分析レポート
        </p>
      </div>

      {/* Reports list */}
      {reports.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="レポートがありません"
          description="シミュレーションを実行するとレポートが生成されます"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {reports.map((report) => (
            <ReportCard key={report.date} report={report} />
          ))}
        </div>
      )}
    </div>
  );
}
