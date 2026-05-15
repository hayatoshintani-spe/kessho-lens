'use client';

import { useState } from 'react';
import { Lightbulb, Play, CheckCircle2, BookOpen, AlertTriangle } from 'lucide-react';
import { fetchAdvisorDebate } from '@/lib/api';
import type { AdvisorPeriod, AdvisorRisk } from '@/lib/api';
import ChatBubble from '@/components/meetings/ChatBubble';
import { cn, AGENT_COLORS, AGENT_NAMES } from '@/lib/utils';
import type { MeetingLog } from '@/lib/types';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const PERIOD_OPTIONS: { value: AdvisorPeriod; label: string; sub: string }[] = [
  { value: 'short', label: '1〜3年', sub: '短期' },
  { value: 'medium', label: '5〜10年', sub: '中期' },
  { value: 'long', label: '10年以上', sub: '長期' },
];

const RISK_OPTIONS: { value: AdvisorRisk; label: string; sub: string; color: string }[] = [
  { value: 'low', label: '低リスク', sub: '元本重視・安定運用', color: '#1D9E75' },
  { value: 'medium', label: '中リスク', sub: 'バランス型・市場平均', color: '#C8860A' },
  { value: 'high', label: '高リスク', sub: '積極運用・最大化狙い', color: '#D85A30' },
];

export default function AdvisorPage() {
  const [amount, setAmount] = useState<string>('400');
  const [period, setPeriod] = useState<AdvisorPeriod>('medium');
  const [risk, setRisk] = useState<AdvisorRisk>('medium');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MeetingLog | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    const n = parseInt(amount, 10);
    if (!n || n <= 0) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await fetchAdvisorDebate(n, period, risk);
      setResult(data);
    } catch {
      setError('バックエンドに接続できませんでした。設定ページでAPIを確認してください。');
    } finally {
      setLoading(false);
    }
  };

  const selectedRisk = RISK_OPTIONS.find((r) => r.value === risk)!;

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-text-primary text-xl font-bold flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-accent-gold" />
          個人資産アドバイザー
        </h1>
        <p className="text-text-muted text-sm mt-0.5">
          実際の資産額を入力すると、4つのAIが最適な運用戦略を議論します
        </p>
      </div>

      {/* Input form */}
      <div className="card p-6 space-y-6">
        {/* Asset amount */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            運用資産額
          </label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              max="100000"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-40 bg-bg-elevated border border-border rounded-md px-3 py-2.5 text-text-primary text-base font-tabular font-bold focus:outline-none focus:border-accent-gold/60 transition-colors text-right"
              placeholder="400"
            />
            <span className="text-text-secondary text-base font-medium">万円</span>
            {amount && parseInt(amount) > 0 && (
              <span className="text-text-muted text-sm">
                （{(parseInt(amount) * 10000).toLocaleString('ja-JP')}円）
              </span>
            )}
          </div>
        </div>

        {/* Investment period */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            投資期間
          </label>
          <div className="flex gap-2 flex-wrap">
            {PERIOD_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setPeriod(opt.value)}
                className={cn(
                  'px-4 py-2.5 rounded-md border text-sm font-medium transition-all',
                  period === opt.value
                    ? 'bg-accent-gold/15 border-accent-gold/50 text-accent-gold'
                    : 'bg-transparent border-border text-text-secondary hover:border-border-light hover:text-text-primary',
                )}
              >
                <div className="font-semibold">{opt.label}</div>
                <div className="text-[10px] opacity-70 mt-0.5">{opt.sub}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Risk tolerance */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            リスク許容度
          </label>
          <div className="space-y-2">
            {RISK_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className={cn(
                  'flex items-center gap-3 p-3.5 rounded-md border cursor-pointer transition-all',
                  risk === opt.value
                    ? 'border-opacity-50 bg-opacity-5'
                    : 'border-border hover:border-border-light',
                )}
                style={
                  risk === opt.value
                    ? { borderColor: opt.color + '55', backgroundColor: opt.color + '0D' }
                    : {}
                }
              >
                <div
                  className={cn(
                    'w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all',
                  )}
                  style={
                    risk === opt.value
                      ? { borderColor: opt.color, backgroundColor: opt.color }
                      : { borderColor: '#1E2535' }
                  }
                >
                  {risk === opt.value && (
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                  )}
                </div>
                <input
                  type="radio"
                  name="risk"
                  value={opt.value}
                  checked={risk === opt.value}
                  onChange={() => setRisk(opt.value)}
                  className="sr-only"
                />
                <div className="flex-1">
                  <div
                    className="text-sm font-semibold"
                    style={{ color: risk === opt.value ? opt.color : undefined }}
                  >
                    {opt.label}
                  </div>
                  <div className="text-text-muted text-xs">{opt.sub}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading || !amount || parseInt(amount) <= 0}
          className="flex items-center gap-2 bg-accent-gold hover:bg-accent-gold-light disabled:opacity-50 disabled:cursor-not-allowed text-bg-primary px-5 py-2.5 rounded-md text-sm font-semibold transition-all"
        >
          {loading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {loading ? '4AIが議論中...' : '4AIに相談する'}
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="card p-8 text-center space-y-3">
          <LoadingSpinner size="lg" />
          <p className="text-text-secondary text-sm">
            4つのAIが{amount}万円の最適運用戦略を議論しています...
          </p>
          <p className="text-text-muted text-xs">
            Claude APIを使用している場合は10〜20秒かかることがあります
          </p>
          {/* Agent avatars */}
          <div className="flex justify-center gap-3 pt-2">
            {(['soros', 'buffett', 'lynch', 'flat'] as const).map((id) => (
              <div
                key={id}
                className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white animate-pulse"
                style={{ backgroundColor: AGENT_COLORS[id] }}
              >
                {AGENT_NAMES[id].en.charAt(0)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="card p-4 border-loss/30 bg-loss/5 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-loss flex-shrink-0 mt-0.5" />
          <p className="text-loss text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-4 animate-fade-in">
          {/* Summary card */}
          <div className="card p-6">
            <div className="flex items-start justify-between gap-4 flex-wrap mb-4">
              <div>
                <div className="text-text-muted text-xs uppercase tracking-wider mb-1">議論テーマ</div>
                <h2 className="text-text-primary text-lg font-bold">
                  {result.marketTheme}
                </h2>
              </div>
              {/* Participants */}
              <div className="flex -space-x-2">
                {result.participants.map((id) => (
                  <div
                    key={id}
                    className="w-8 h-8 rounded-full border-2 border-bg-card flex items-center justify-center text-[11px] font-bold text-white"
                    style={{ backgroundColor: AGENT_COLORS[id] }}
                    title={AGENT_NAMES[id]?.ja}
                  >
                    {AGENT_NAMES[id]?.en.charAt(0)}
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-border mb-4">
              <div className="text-text-muted text-xs uppercase tracking-wider mb-1.5">サマリー</div>
              <p className="text-text-secondary text-sm leading-relaxed">{result.summary}</p>
            </div>

            {/* Key decisions */}
            {result.keyDecisions.length > 0 && (
              <div className="pt-4 border-t border-border">
                <div className="text-text-muted text-xs uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-profit" />
                  推奨配分
                </div>
                <ul className="space-y-2">
                  {result.keyDecisions.map((d, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-profit/20 border border-profit/40 flex items-center justify-center text-[10px] font-bold text-profit flex-shrink-0 mt-0.5">
                        {i + 1}
                      </div>
                      <span className="text-text-secondary text-sm leading-relaxed">{d}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Chat log */}
          <div className="card p-5">
            <h3 className="text-text-primary font-semibold text-sm mb-5 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-accent-gold" />
              議論ログ ({result.messages.length}件)
            </h3>
            <div className="space-y-4">
              {result.messages.map((msg, i) => (
                <ChatBubble key={i} message={msg} />
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="flex items-start gap-2 px-1">
            <AlertTriangle className="w-3.5 h-3.5 text-text-muted flex-shrink-0 mt-0.5" />
            <p className="text-text-muted text-xs leading-relaxed">
              本機能はAIシミュレーションです。実際の投資判断には専門家（FP・証券アドバイザー等）に
              ご相談ください。投資にはリスクが伴い、元本割れの可能性があります。
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
