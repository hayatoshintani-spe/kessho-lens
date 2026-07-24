'use client';

import { useEffect, useState } from 'react';
import {
  ExternalLink,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Database,
} from 'lucide-react';
import Alert from '@/components/ui/Alert';
import BackLink from '@/components/ui/BackLink';
import Button from '@/components/ui/Button';
import PageHeader from '@/components/ui/PageHeader';
import {
  fetchNotionStatus,
  syncAllCardsToNotion,
  setupNotionDatabase,
} from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import type { NotionStatus } from '@/lib/intel-api';

export default function NotionSettingsPage() {
  const [status, setStatus] = useState<NotionStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Setup
  const [parentPageId, setParentPageId] = useState('');
  const [setupResult, setSetupResult] = useState<{
    database_id?: string;
    url?: string;
    message?: string;
    error?: string;
  } | null>(null);
  const [isSettingUp, setIsSettingUp] = useState(false);

  // Sync
  const [syncResult, setSyncResult] = useState<{
    created: number;
    updated: number;
    skipped: number;
    errors: unknown[];
  } | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  async function reload() {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const s = await fetchNotionStatus();
      setStatus(s);
    } catch (e) {
      setErrorMsg((e as Error).message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) {
        setErrorMsg('バックエンドに接続できません');
        setIsLoading(false);
        return;
      }
      await reload();
    })();
  }, []);

  async function handleSetup() {
    if (!parentPageId.trim()) {
      setSetupResult({ error: '親ページID（または共有URL末尾のID）を入力してください' });
      return;
    }
    setIsSettingUp(true);
    setSetupResult(null);
    try {
      const r = await setupNotionDatabase(parentPageId.trim());
      setSetupResult(r);
      if (r.database_id) await reload();
    } catch (e) {
      setSetupResult({ error: (e as Error).message });
    } finally {
      setIsSettingUp(false);
    }
  }

  async function handleSyncAll() {
    setIsSyncing(true);
    setSyncResult(null);
    try {
      const r = await syncAllCardsToNotion();
      setSyncResult(r.result);
    } catch (e) {
      setErrorMsg((e as Error).message);
    } finally {
      setIsSyncing(false);
    }
  }

  return (
    <div className="space-y-5 animate-fade-in max-w-3xl">
      <BackLink href="/intel">Intelligence Brief に戻る</BackLink>

      <PageHeader
        icon={Database}
        title="Notion 連携"
        description="IntelCard を Notion DB に push 同期。社内編集・共有ワークフローを統合"
      />

      {errorMsg && <Alert>{errorMsg}</Alert>}

      {/* 接続状況 */}
      <section className="card p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-text-primary font-semibold text-sm">接続状況</h2>
          <button
            onClick={reload}
            disabled={isLoading}
            className="text-text-muted hover:text-accent-gold text-xs flex items-center gap-1"
          >
            <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
            更新
          </button>
        </div>

        {isLoading ? (
          <div className="text-text-muted text-sm">読み込み中...</div>
        ) : status ? (
          <div className="space-y-2">
            <StatusRow
              label="NOTION_API_KEY"
              ok={status.has_api_key}
              detail={status.has_api_key ? '設定済み' : '未設定'}
            />
            <StatusRow
              label="NOTION_CARDS_DB_ID"
              ok={status.has_db_id}
              detail={
                status.db_id ? (
                  <span className="font-mono text-[10px] break-all">{status.db_id}</span>
                ) : (
                  '未設定'
                )
              }
            />
            <StatusRow
              label="同期"
              ok={status.enabled}
              detail={status.enabled ? '有効' : '無効'}
            />
            {status.db?.title && (
              <div className="mt-3 pt-3 border-t border-border space-y-1.5">
                <div className="text-text-secondary text-xs">
                  <strong>接続先 DB:</strong> {status.db.title}
                </div>
                {status.db.url && (
                  <a
                    href={status.db.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent-gold text-xs inline-flex items-center gap-1 hover:underline"
                  >
                    Notion で開く <ExternalLink className="w-3 h-3" />
                  </a>
                )}
                {status.db.properties && (
                  <div className="text-text-muted text-[10px]">
                    プロパティ: {status.db.properties.join(' / ')}
                  </div>
                )}
              </div>
            )}
            {status.db?.error && <Alert className="mt-3">{status.db.error}</Alert>}
          </div>
        ) : null}
      </section>

      {/* セットアップ */}
      {!status?.enabled && (
        <section className="card p-5">
          <h2 className="text-text-primary font-semibold text-sm mb-3">
            🛠️ 初期セットアップ
          </h2>

          <ol className="text-text-secondary text-xs space-y-2 mb-4 list-decimal list-inside">
            <li>
              <a
                href="https://www.notion.so/my-integrations"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-gold underline"
              >
                Notion Integration を作成
              </a>{' '}
              → Internal Integration Token を取得し、バックエンドの環境変数
              <code className="font-mono text-accent-gold mx-1">NOTION_API_KEY</code>
              に設定
            </li>
            <li>
              Notion で IntelCards DB を置きたい親ページを開き、右上の「…」→「Connections」から
              作成した Integration を招待
            </li>
            <li>
              親ページのURL（例: <code className="font-mono text-[10px]">notion.so/abc123...</code>）から
              ページIDをコピーし、下のフォームに貼り付け
            </li>
            <li>「DB作成」ボタンで自動的にスキーマ付きDBが生成される</li>
            <li>
              出力された <code className="font-mono text-accent-gold">database_id</code> を
              <code className="font-mono text-accent-gold mx-1">NOTION_CARDS_DB_ID</code>
              として環境変数に設定し、バックエンドを再起動
            </li>
          </ol>

          <div className="space-y-2">
            <input
              type="text"
              value={parentPageId}
              onChange={(e) => setParentPageId(e.target.value)}
              placeholder="親ページID（例: 123abc456def... または URL末尾）"
              className="form-input"
            />
            <Button
              onClick={handleSetup}
              disabled={isSettingUp || !parentPageId.trim() || !status?.has_api_key}
            >
              {isSettingUp ? 'DB作成中...' : 'DB作成'}
            </Button>
            {!status?.has_api_key && (
              <div className="text-text-muted text-[10px]">
                NOTION_API_KEY を先に設定してください
              </div>
            )}
          </div>

          {setupResult &&
            (setupResult.error ? (
              <Alert className="mt-3">{setupResult.error}</Alert>
            ) : (
              <Alert variant="success" title="DB を作成しました" className="mt-3">
                <div className="space-y-1.5">
                  <div className="font-mono text-[10px] break-all">
                    NOTION_CARDS_DB_ID={setupResult.database_id}
                  </div>
                  {setupResult.url && (
                    <a
                      href={setupResult.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent-gold inline-flex items-center gap-1"
                    >
                      Notion で開く <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  <div className="text-text-muted">
                    この database_id を環境変数に設定 → バックエンド再起動 → このページを更新
                  </div>
                </div>
              </Alert>
            ))}
        </section>
      )}

      {/* 一括同期 */}
      {status?.enabled && (
        <section className="card p-5">
          <h2 className="text-text-primary font-semibold text-sm mb-2">📤 一括同期</h2>
          <p className="text-text-secondary text-xs mb-3">
            全てのカードを Notion DB に push します（既存ページは Card ID で upsert）
          </p>
          <Button onClick={handleSyncAll} disabled={isSyncing}>
            {isSyncing ? '同期中...' : '全カードを同期'}
          </Button>

          {syncResult && (
            <div className="mt-3 p-3 rounded bg-bg-elevated border border-border">
              <div className="grid grid-cols-3 gap-2 text-center">
                <SyncStat label="新規" value={syncResult.created} color="#1D9E75" />
                <SyncStat label="更新" value={syncResult.updated} color="#C8860A" />
                <SyncStat label="エラー" value={syncResult.errors.length} color="#D85A30" />
              </div>
              {syncResult.errors.length > 0 && (
                <div className="mt-3 text-xs text-loss space-y-1">
                  {syncResult.errors.slice(0, 5).map((err, i) => (
                    <div key={i} className="font-mono text-[10px]">
                      {typeof err === 'string' ? err : JSON.stringify(err)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function StatusRow({
  label,
  ok,
  detail,
}: {
  label: string;
  ok: boolean;
  detail: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-2 text-xs">
      {ok ? (
        <CheckCircle2 className="w-4 h-4 text-profit flex-shrink-0" />
      ) : (
        <XCircle className="w-4 h-4 text-text-muted flex-shrink-0" />
      )}
      <span className="text-text-secondary font-mono">{label}</span>
      <span className="text-text-primary ml-auto text-right">{detail}</span>
    </div>
  );
}

function SyncStat({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div>
      <div className="text-2xl font-bold font-tabular" style={{ color }}>
        {value}
      </div>
      <div className="text-text-muted text-[10px] mt-0.5">{label}</div>
    </div>
  );
}
