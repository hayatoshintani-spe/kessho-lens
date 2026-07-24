'use client';

import { useEffect, useState } from 'react';
import {
  Mail,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Send,
  Eye,
  RefreshCw,
} from 'lucide-react';
import Alert from '@/components/ui/Alert';
import BackLink from '@/components/ui/BackLink';
import Button from '@/components/ui/Button';
import NoticeCard from '@/components/ui/NoticeCard';
import PageHeader from '@/components/ui/PageHeader';
import { warmupBackend } from '@/lib/api';
import {
  fetchEmailStatus,
  sendTestEmail,
  type EmailDeliveryStatus,
  type EmailSendResult,
} from '@/lib/intel-api';

export default function DeliveryPage() {
  const [status, setStatus] = useState<EmailDeliveryStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [isSending, setIsSending] = useState(false);
  const [sendResult, setSendResult] = useState<{
    date: string;
    result: EmailSendResult;
  } | null>(null);

  const [previewDate, setPreviewDate] = useState('');

  async function reload() {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const s = await fetchEmailStatus();
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

  async function handleSend(dryRun: boolean) {
    setIsSending(true);
    setSendResult(null);
    try {
      const r = await sendTestEmail({
        date: previewDate.trim() || undefined,
        dry_run: dryRun,
      });
      setSendResult(r);
    } catch (e) {
      setSendResult({
        date: previewDate || '',
        result: { status: 'error', error: (e as Error).message },
      });
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="space-y-5 animate-fade-in max-w-3xl">
      <BackLink href="/intel">Intelligence Brief に戻る</BackLink>

      <PageHeader
        icon={Mail}
        title="メール配信設定"
        description="毎朝 Daily Brief を経営層に Resend 経由で自動配信します"
      />

      {errorMsg && <Alert>{errorMsg}</Alert>}

      {isLoading ? (
        <NoticeCard>読み込み中...</NoticeCard>
      ) : status ? (
        <>
          {/* 配信ステータス */}
          <section className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-text-primary text-sm font-semibold">配信ステータス</h2>
              <button
                onClick={reload}
                className="text-text-muted hover:text-accent-gold transition-colors"
                title="再読み込み"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <StatusRow
                label="配信機能"
                ok={status.enabled}
                value={status.enabled ? '有効' : '無効 — 必須環境変数が未設定'}
              />
              <StatusRow
                label="Resend API キー"
                ok={status.has_api_key}
                value={status.has_api_key ? '設定済み' : '未設定 (RESEND_API_KEY)'}
              />
              <StatusRow
                label="差出人"
                ok={!!status.from}
                value={status.from || '未設定 (BRIEF_EMAIL_FROM)'}
                isText
              />
              <StatusRow
                label="配信先"
                ok={status.recipient_count > 0}
                value={
                  status.recipient_count > 0
                    ? `${status.recipient_count} 件: ${status.recipients.join(', ')}`
                    : '未設定 (BRIEF_EMAIL_RECIPIENTS)'
                }
                isText
              />
              <StatusRow
                label="フロントエンド URL (本文リンク用)"
                ok={!!status.frontend_url}
                value={status.frontend_url || '未設定 — メール本文にリンクが入りません'}
                isText
                neutralWhenMissing
              />
              <StatusRow label="タイムゾーン" ok value={status.timezone} isText />
            </div>
          </section>

          {/* スケジュール情報 */}
          <section className="card p-5">
            <div className="flex items-center gap-2 mb-3">
              <Clock className="w-4 h-4 text-accent-gold" />
              <h2 className="text-text-primary text-sm font-semibold">スケジュール</h2>
            </div>
            <div className="text-text-secondary text-sm leading-relaxed space-y-2">
              <p>
                <strong className="text-text-primary">毎朝 7:00 JST</strong>
                {' '}(=22:00 UTC 前日) に
                <code className="mx-1 px-1.5 py-0.5 bg-bg-elevated text-accent-gold rounded text-xs">
                  /api/intel/cron/daily-brief
                </code>
                を Vercel Cron / Render Cron が呼び出します。
              </p>
              <ul className="list-disc list-inside text-xs text-text-muted space-y-1 mt-2">
                <li>その日の IntelCard から Daily Brief を生成（既に存在すれば再利用）</li>
                <li>Brief 本文・重要トピックス・次アクション・リスクを整形したメールを送信</li>
                <li>当日カードが 0 件なら配信スキップ（ログのみ）</li>
              </ul>
            </div>
          </section>

          {/* テスト送信 */}
          <section className="card p-5">
            <div className="flex items-center gap-2 mb-3">
              <Send className="w-4 h-4 text-accent-gold" />
              <h2 className="text-text-primary text-sm font-semibold">テスト送信</h2>
            </div>
            <p className="text-text-muted text-xs mb-3">
              指定日（既定: 今日）の Brief をテスト送信。「プレビュー」は実送信せず HTML を確認のみ。
            </p>

            <div className="flex flex-col sm:flex-row gap-2 mb-3">
              <input
                type="text"
                value={previewDate}
                onChange={(e) => setPreviewDate(e.target.value)}
                placeholder="YYYY-MM-DD (空欄=今日)"
                className="form-input flex-1 font-mono"
              />
              <Button variant="ghost" onClick={() => handleSend(true)} disabled={isSending}>
                <Eye className="w-4 h-4" /> プレビュー
              </Button>
              <Button
                onClick={() => handleSend(false)}
                disabled={isSending || !status.enabled}
                title={!status.enabled ? 'メール配信が無効です' : '実際に送信します'}
              >
                <Send className="w-4 h-4" /> 送信
              </Button>
            </div>

            {sendResult && <SendResultPanel result={sendResult} />}
          </section>

          {/* 設定方法 */}
          <section className="card p-5 bg-bg-elevated/40">
            <h2 className="text-text-primary text-sm font-semibold mb-2">設定方法</h2>
            <ol className="text-text-secondary text-xs space-y-1.5 list-decimal list-inside leading-relaxed">
              <li>
                <a
                  href="https://resend.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent-gold underline"
                >
                  Resend
                </a>
                {' '}で API キーを取得し、送信ドメインを認証する
              </li>
              <li>
                バックエンドの環境変数に{' '}
                <code className="bg-bg-elevated px-1.5 py-0.5 rounded text-accent-gold">RESEND_API_KEY</code>
                ／ <code className="bg-bg-elevated px-1.5 py-0.5 rounded text-accent-gold">BRIEF_EMAIL_FROM</code>
                ／ <code className="bg-bg-elevated px-1.5 py-0.5 rounded text-accent-gold">BRIEF_EMAIL_RECIPIENTS</code>
                ／ <code className="bg-bg-elevated px-1.5 py-0.5 rounded text-accent-gold">CRON_SECRET</code>
                {' '}を設定
              </li>
              <li>
                Vercel プロジェクトにも同じ{' '}
                <code className="bg-bg-elevated px-1.5 py-0.5 rounded text-accent-gold">CRON_SECRET</code>
                {' '}を設定（Vercel Cron 認証用）
              </li>
              <li>このページの「送信」ボタンでテスト送信し、配信を確認</li>
            </ol>
          </section>
        </>
      ) : null}
    </div>
  );
}

function StatusRow({
  label,
  ok,
  value,
  isText = false,
  neutralWhenMissing = false,
}: {
  label: string;
  ok: boolean;
  value: string;
  isText?: boolean;
  neutralWhenMissing?: boolean;
}) {
  const Icon = ok ? CheckCircle2 : neutralWhenMissing ? AlertTriangle : XCircle;
  const color = ok
    ? 'text-profit'
    : neutralWhenMissing
      ? 'text-accent-gold'
      : 'text-loss';
  return (
    <div className="flex items-start gap-3 text-sm">
      <Icon className={`w-4 h-4 flex-shrink-0 mt-0.5 ${color}`} />
      <div className="flex-1 min-w-0">
        <div className="text-text-muted text-xs">{label}</div>
        <div
          className={
            isText
              ? 'text-text-primary text-sm break-all'
              : 'text-text-primary text-sm'
          }
        >
          {value}
        </div>
      </div>
    </div>
  );
}

function SendResultPanel({
  result,
}: {
  result: { date: string; result: EmailSendResult };
}) {
  const r = result.result;
  const isOk = r.status === 'sent' || r.status === 'dry_run';
  return (
    <div
      className={`mt-3 p-3 rounded border text-sm ${
        isOk
          ? 'bg-profit/5 border-profit/30 text-text-primary'
          : 'bg-loss/5 border-loss/30 text-text-primary'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        {isOk ? (
          <CheckCircle2 className="w-4 h-4 text-profit" />
        ) : (
          <XCircle className="w-4 h-4 text-loss" />
        )}
        <span className="font-semibold text-xs uppercase tracking-wider">
          {r.status === 'sent' && '送信成功'}
          {r.status === 'dry_run' && 'プレビュー生成'}
          {r.status === 'skipped' && 'スキップ'}
          {r.status === 'error' && 'エラー'}
        </span>
        <span className="text-text-muted text-xs">{result.date}</span>
      </div>
      {r.subject && (
        <div className="text-xs mb-1">
          <span className="text-text-muted">件名: </span>
          <span className="text-text-primary">{r.subject}</span>
        </div>
      )}
      {r.recipients && r.recipients.length > 0 && (
        <div className="text-xs mb-1">
          <span className="text-text-muted">宛先: </span>
          <span className="text-text-primary">{r.recipients.join(', ')}</span>
        </div>
      )}
      {r.message_id && (
        <div className="text-xs mb-1">
          <span className="text-text-muted">message_id: </span>
          <span className="text-text-primary font-mono">{r.message_id}</span>
        </div>
      )}
      {r.reason && <div className="text-xs text-loss">{r.reason}</div>}
      {r.error && <div className="text-xs text-loss break-all">{r.error}</div>}
      {r.html_preview && (
        <details className="mt-2">
          <summary className="text-xs text-text-muted cursor-pointer hover:text-accent-gold">
            HTML プレビュー（先頭500文字）
          </summary>
          <pre className="mt-2 text-[10px] bg-bg-elevated p-2 rounded overflow-auto max-h-64 text-text-secondary">
            {r.html_preview}
          </pre>
        </details>
      )}
    </div>
  );
}
