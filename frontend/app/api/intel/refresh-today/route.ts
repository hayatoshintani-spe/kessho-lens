// 「今すぐ更新」ボタン用のブラウザ → サーバー間 API。
// バックエンドの /api/intel/cron/daily-brief を CRON_SECRET 付きで叩き、
// 当日のニュース取得 → カード生成 → ブリーフ → メール → Notion 保存 を1回で実行する。
//
// CRON_SECRET は Vercel の環境変数（サーバー側のみ）から読む。ブラウザには出さない。

import { NextRequest, NextResponse } from 'next/server';

// Vercel Hobby は最大 60 秒。Render コールドスタート 30〜50 秒を吸収する余地を持つ。
export const maxDuration = 60;

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
const CRON_SECRET = process.env.CRON_SECRET ?? '';

export async function POST(_req: NextRequest) {
  if (!CRON_SECRET) {
    return NextResponse.json(
      { error: 'CRON_SECRET is not configured on the server' },
      { status: 500 },
    );
  }

  try {
    // バックエンドは BackgroundTasks で即時 202 を返す設計に変わったが、
    // Render コールドスタート分は待つ必要があるので 90s で切る
    const res = await fetch(`${API_BASE}/api/intel/cron/daily-brief`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${CRON_SECRET}`,
      },
      signal: AbortSignal.timeout(55_000),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      return NextResponse.json(
        { error: 'Backend error', status: res.status, details: data },
        { status: res.status },
      );
    }
    return NextResponse.json({ ok: true, ...data });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json(
      { error: 'Failed to reach backend', details: message },
      { status: 500 },
    );
  }
}
