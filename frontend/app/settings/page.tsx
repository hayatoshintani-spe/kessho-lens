'use client';

import { useState, useEffect } from 'react';
import { Settings, Save, Play, Info, Eye, EyeOff } from 'lucide-react';
import type { AppSettings, MarketTarget } from '@/lib/types';
import { cn } from '@/lib/utils';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const SETTINGS_KEY = 'kessho_settings';

const DEFAULT_SETTINGS: AppSettings = {
  apiBaseUrl: 'http://localhost:8000',
  anthropicApiKey: '',
  marketTarget: 'japan',
  autoRunEnabled: true,
  autoRunTime: '10:00',
};

const MARKET_OPTIONS: { value: MarketTarget; label: string; desc: string }[] = [
  { value: 'japan', label: '日本株', desc: '東証上場銘柄を対象' },
  { value: 'us', label: '米国株', desc: 'NYSE/NASDAQ上場銘柄を対象' },
  { value: 'both', label: '日米両方', desc: '日米両方の銘柄を対象' },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [saved, setSaved] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<string | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<AppSettings>;
        setSettings({ ...DEFAULT_SETTINGS, ...parsed });
      }
    } catch {
      // ignore
    }
  }, []);

  const handleSave = () => {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // ignore
    }
  };

  const handleRunSimulation = async () => {
    setRunning(true);
    setRunResult(null);
    try {
      const res = await fetch(`${settings.apiBaseUrl}/api/cron/run-daily`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ secret: 'manual' }),
      });
      const data = await res.json();
      setRunResult(
        res.ok
          ? `シミュレーション開始: ${data.message ?? '成功'}`
          : `エラー: ${data.error ?? res.statusText}`,
      );
    } catch (e) {
      setRunResult(`接続エラー: バックエンドに接続できません (${settings.apiBaseUrl})`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-text-primary text-xl font-bold flex items-center gap-2">
          <Settings className="w-5 h-5 text-accent-gold" />
          設定
        </h1>
        <p className="text-text-muted text-sm mt-0.5">
          APIとシミュレーションの設定を管理する
        </p>
      </div>

      {/* API Settings */}
      <div className="card p-6 space-y-5">
        <h2 className="text-text-primary font-semibold text-base border-b border-border pb-3">
          API設定
        </h2>

        {/* API Base URL */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-1.5">
            バックエンドAPI URL
          </label>
          <input
            type="url"
            value={settings.apiBaseUrl}
            onChange={(e) => setSettings({ ...settings, apiBaseUrl: e.target.value })}
            className="w-full bg-bg-elevated border border-border rounded-md px-3 py-2.5 text-text-primary text-sm placeholder:text-text-muted focus:outline-none focus:border-accent-gold/60 font-mono transition-colors"
            placeholder="http://localhost:8000"
          />
          <p className="text-text-muted text-xs mt-1">
            FastAPIバックエンドのベースURL
          </p>
        </div>

        {/* Anthropic API Key */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-1.5">
            Anthropic APIキー
          </label>
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={settings.anthropicApiKey}
              onChange={(e) => setSettings({ ...settings, anthropicApiKey: e.target.value })}
              className="w-full bg-bg-elevated border border-border rounded-md px-3 py-2.5 pr-10 text-text-primary text-sm placeholder:text-text-muted focus:outline-none focus:border-accent-gold/60 font-mono transition-colors"
              placeholder="sk-ant-..."
            />
            <button
              type="button"
              onClick={() => setShowKey((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary transition-colors"
            >
              {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <p className="text-text-muted text-xs mt-1">
            Claude APIアクセスに必要（バックエンドで使用）
          </p>
        </div>
      </div>

      {/* Market Target */}
      <div className="card p-6 space-y-4">
        <h2 className="text-text-primary font-semibold text-base border-b border-border pb-3">
          対象市場
        </h2>
        <div className="space-y-2">
          {MARKET_OPTIONS.map(({ value, label, desc }) => (
            <label
              key={value}
              className={cn(
                'flex items-center gap-3 p-3.5 rounded-md border cursor-pointer transition-all',
                settings.marketTarget === value
                  ? 'border-accent-gold/40 bg-accent-gold/5'
                  : 'border-border hover:border-border-light',
              )}
            >
              <div
                className={cn(
                  'w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all',
                  settings.marketTarget === value
                    ? 'border-accent-gold bg-accent-gold'
                    : 'border-border',
                )}
              >
                {settings.marketTarget === value && (
                  <div className="w-1.5 h-1.5 rounded-full bg-white" />
                )}
              </div>
              <input
                type="radio"
                name="marketTarget"
                value={value}
                checked={settings.marketTarget === value}
                onChange={() => setSettings({ ...settings, marketTarget: value })}
                className="sr-only"
              />
              <div>
                <div className="text-text-primary text-sm font-medium">{label}</div>
                <div className="text-text-muted text-xs">{desc}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Auto Run Settings */}
      <div className="card p-6 space-y-4">
        <h2 className="text-text-primary font-semibold text-base border-b border-border pb-3">
          自動実行設定
        </h2>

        <label className="flex items-center justify-between gap-4">
          <div>
            <div className="text-text-secondary text-sm font-medium">自動実行を有効化</div>
            <div className="text-text-muted text-xs mt-0.5">
              Vercel Cronによる毎日の自動シミュレーション
            </div>
          </div>
          <button
            type="button"
            onClick={() =>
              setSettings({ ...settings, autoRunEnabled: !settings.autoRunEnabled })
            }
            className={cn(
              'w-11 h-6 rounded-full transition-all relative flex-shrink-0',
              settings.autoRunEnabled ? 'bg-accent-gold' : 'bg-bg-elevated border border-border',
            )}
          >
            <div
              className={cn(
                'absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-all',
                settings.autoRunEnabled ? 'left-5' : 'left-0.5',
              )}
            />
          </button>
        </label>

        <div>
          <label className="block text-text-secondary text-sm font-medium mb-1.5">
            実行時刻 (JST)
          </label>
          <input
            type="time"
            value={settings.autoRunTime}
            onChange={(e) => setSettings({ ...settings, autoRunTime: e.target.value })}
            className="bg-bg-elevated border border-border rounded-md px-3 py-2.5 text-text-primary text-sm focus:outline-none focus:border-accent-gold/60 font-mono transition-colors"
          />
        </div>

        {/* Cron info */}
        <div className="bg-bg-elevated rounded-md p-3.5 border border-border">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-text-muted mt-0.5 flex-shrink-0" />
            <div className="text-text-muted text-xs leading-relaxed">
              <strong className="text-text-secondary">Vercel Cron設定:</strong>{' '}
              <code className="font-mono text-accent-gold bg-bg-primary px-1 py-0.5 rounded text-[11px]">
                0 1 * * *
              </code>{' '}
              (UTC 01:00 = JST 10:00)。
              デプロイ後、vercel.jsonのcron設定が自動的に有効になります。
            </div>
          </div>
        </div>
      </div>

      {/* Manual Run */}
      <div className="card p-6 space-y-4">
        <h2 className="text-text-primary font-semibold text-base border-b border-border pb-3">
          手動実行
        </h2>
        <p className="text-text-secondary text-sm">
          今すぐ日次シミュレーションを手動で実行します。バックエンドが起動している必要があります。
        </p>

        {runResult && (
          <div
            className={cn(
              'rounded-md p-3 text-sm',
              runResult.startsWith('エラー') || runResult.startsWith('接続')
                ? 'bg-loss/10 border border-loss/30 text-loss'
                : 'bg-profit/10 border border-profit/30 text-profit',
            )}
          >
            {runResult}
          </div>
        )}

        <button
          type="button"
          onClick={handleRunSimulation}
          disabled={running}
          className="flex items-center gap-2 bg-accent-gold/20 hover:bg-accent-gold/30 border border-accent-gold/40 text-accent-gold px-4 py-2.5 rounded-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? (
            <LoadingSpinner size="sm" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {running ? '実行中...' : '日次シミュレーションを実行'}
        </button>
      </div>

      {/* Save button */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          className={cn(
            'flex items-center gap-2 px-5 py-2.5 rounded-md text-sm font-medium transition-all',
            saved
              ? 'bg-profit/20 border border-profit/40 text-profit'
              : 'bg-accent-gold hover:bg-accent-gold-light text-bg-primary',
          )}
        >
          <Save className="w-4 h-4" />
          {saved ? '保存しました ✓' : '設定を保存'}
        </button>
        <p className="text-text-muted text-xs">
          設定はブラウザのlocalStorageに保存されます
        </p>
      </div>
    </div>
  );
}
