'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Sparkles, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { createIntelCard, fetchIntelMeta } from '@/lib/intel-api';
import { warmupBackend } from '@/lib/api';
import type {
  IntelCategory,
  Importance,
  IntelMeta,
} from '@/lib/intel-types';
import {
  CATEGORY_ICONS,
  CATEGORY_LABELS_JA,
  IMPORTANCE_LABELS_JA,
  IMPORTANCE_COLORS,
} from '@/lib/intel-types';

const CATEGORIES: IntelCategory[] = [
  'ip_content',
  'ai_agent',
  'device_telecom',
  'global_region',
  'retail_md_license',
  'regulation_ip_law',
  'competitor_capital',
];

const IMPORTANCES: Importance[] = ['A', 'B', 'C', 'D'];

const ACCESS_STATUS_OPTIONS = [
  { value: 'full', label: '本文を確認済み' },
  { value: 'title_only', label: 'タイトルのみ' },
  { value: 'paywalled', label: '有料記事（未読）' },
  { value: 'estimated', label: '推定情報' },
] as const;

export default function NewCardPage() {
  const router = useRouter();
  const today = new Date().toISOString().slice(0, 10);

  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [publisher, setPublisher] = useState('');
  const [summary, setSummary] = useState('');
  const [userNote, setUserNote] = useState('');
  const [accessStatus, setAccessStatus] =
    useState<'full' | 'title_only' | 'paywalled' | 'estimated'>('full');
  const [category, setCategory] = useState<IntelCategory | ''>('');
  const [importance, setImportance] = useState<Importance | ''>('');
  const [date, setDate] = useState(today);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successId, setSuccessId] = useState<string | null>(null);
  const [meta, setMeta] = useState<IntelMeta | null>(null);
  const [hasApiKey, setHasApiKey] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
      const alive = await warmupBackend(70_000);
      if (!alive) return;
      try {
        const m = await fetchIntelMeta();
        setMeta(m);
        // ヘルスエンドポイントから API キー有無を取る
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL ?? 'https://kessho-lens-backend.onrender.com'}/api/health`,
        );
        const h = await res.json();
        setHasApiKey(Boolean(h.has_anthropic_key));
      } catch {
        // meta 取得失敗は無視
      }
    })();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMsg('タイトルは必須です');
      return;
    }
    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessId(null);
    try {
      const card = await createIntelCard({
        title: title.trim(),
        url: url.trim() || undefined,
        publisher: publisher.trim() || undefined,
        summary: summary.trim() || undefined,
        user_note: userNote.trim() || undefined,
        access_status: accessStatus,
        category: category || undefined,
        importance: importance || undefined,
        date,
      });
      setSuccessId(card.id);
      // 3秒後に詳細へ遷移
      setTimeout(() => router.push(`/intel/cards/${card.id}`), 1800);
    } catch (e) {
      setErrorMsg((e as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-5 animate-fade-in max-w-3xl">
      <Link
        href="/intel/cards"
        className="inline-flex items-center gap-1 text-text-muted hover:text-accent-gold text-xs"
      >
        <ArrowLeft className="w-3 h-3" /> カードDBに戻る
      </Link>

      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-5 h-5 text-accent-gold" />
          <h1 className="text-text-primary text-xl font-bold">新規カード生成</h1>
        </div>
        <p className="text-text-muted text-sm">
          ニュースのタイトル・URL・要約を入力すると、円谷向けの IntelCard を自動生成します
        </p>
      </div>

      {hasApiKey === false && (
        <div className="card p-3 border-amber-500/30 bg-amber-500/5">
          <div className="flex items-start gap-2 text-amber-500 text-xs">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold mb-0.5">API キー未設定</div>
              <span className="text-text-secondary">
                ANTHROPIC_API_KEY が未設定のため、ルールベースの fallback で生成します。
                Claude による本格生成にはバックエンド側で API キーを設定してください。
              </span>
            </div>
          </div>
        </div>
      )}

      {successId && (
        <div className="card p-4 border-profit/40 bg-profit/5">
          <div className="flex items-center gap-2 text-profit text-sm">
            <CheckCircle2 className="w-4 h-4" />
            <span>カードを生成しました（{successId}）— 詳細ページへ遷移中...</span>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="card p-4 border-loss/40 bg-loss/5">
          <div className="flex items-center gap-2 text-loss text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span>{errorMsg}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card p-5 space-y-4">
        <FormField label="タイトル *" required>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="例: Pop Mart、北米でLabubu収益が前年比4倍超に拡大"
            className="form-input"
            required
          />
        </FormField>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="URL">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="form-input"
            />
          </FormField>

          <FormField label="出典">
            <input
              type="text"
              value={publisher}
              onChange={(e) => setPublisher(e.target.value)}
              placeholder="例: Bloomberg / 日経 / 業界レポート"
              className="form-input"
            />
          </FormField>
        </div>

        <FormField label="要約・本文（任意）">
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="記事の要約や引用部分を貼り付け。空欄でもタイトルから推定します。"
            rows={4}
            className="form-input resize-y"
          />
        </FormField>

        <FormField label="編集者メモ（任意）" hint="円谷の文脈で気になった視点を書くと、生成品質が上がります">
          <textarea
            value={userNote}
            onChange={(e) => setUserNote(e.target.value)}
            placeholder="例: ウルトラマンの大人向けMD展開に直接関係しそう"
            rows={2}
            className="form-input resize-y"
          />
        </FormField>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="アクセス状況">
            <select
              value={accessStatus}
              onChange={(e) => setAccessStatus(e.target.value as typeof accessStatus)}
              className="form-input"
            >
              {ACCESS_STATUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </FormField>

          <FormField label="日付">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="form-input"
            />
          </FormField>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="カテゴリ" hint="未指定なら自動判定">
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as IntelCategory | '')}
              className="form-input"
            >
              <option value="">自動判定</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {CATEGORY_ICONS[c]} {CATEGORY_LABELS_JA[c]}
                </option>
              ))}
            </select>
          </FormField>

          <FormField label="重要度" hint="未指定なら自動判定">
            <select
              value={importance}
              onChange={(e) => setImportance(e.target.value as Importance | '')}
              className="form-input"
            >
              <option value="">自動判定</option>
              {IMPORTANCES.map((i) => (
                <option key={i} value={i}>
                  [{i}] {IMPORTANCE_LABELS_JA[i]}
                </option>
              ))}
            </select>
          </FormField>
        </div>

        <div className="flex items-center justify-end gap-2 pt-2">
          <Link
            href="/intel/cards"
            className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary"
          >
            キャンセル
          </Link>
          <button
            type="submit"
            disabled={isSubmitting || !title.trim()}
            className="px-4 py-2 rounded bg-accent-gold/10 border border-accent-gold/40 text-accent-gold text-sm font-medium hover:bg-accent-gold/20 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? '生成中...' : 'カードを生成'}
          </button>
        </div>
      </form>

      <style jsx global>{`
        .form-input {
          width: 100%;
          background-color: var(--bg-elevated);
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 8px 12px;
          color: var(--text-primary);
          font-size: 13px;
          outline: none;
          transition: border-color 0.15s;
        }
        .form-input:focus {
          border-color: rgba(200, 134, 10, 0.4);
        }
        .form-input::placeholder {
          color: var(--text-secondary);
          opacity: 0.6;
        }
      `}</style>
    </div>
  );
}

function FormField({
  label,
  hint,
  required,
  children,
}: {
  label: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-text-secondary text-xs font-medium mb-1.5">
        {label}
        {required && <span className="text-loss ml-1">*</span>}
      </label>
      {children}
      {hint && <div className="text-text-muted text-[10px] mt-1">{hint}</div>}
    </div>
  );
}
