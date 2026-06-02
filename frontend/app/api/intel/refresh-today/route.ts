// 「今すぐ更新」ボタン用のブラウザ → サーバー間 API。
// バックエンドの /api/intel/cron/daily-brief を CRON_SECRET 付きで叩き、
// 当日のニュース取得 → カード生成 → ブリーフ → メール → Notion 保存 を1回で実行する。
//
// CRON_SECRET は Vercel の環境変数（サーバー側のみ）から読む。ブラウザには出さない。

import { NextRequest, NextResponse } from 'next/server';

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
    const res = await fetch(`${API_BASE}/api/intel/cron/daily-brief`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${CRON_SECRET}`,
      },
      // Render コールドスタート + Anthropic 呼び出しで時間がかかる
      signal: AbortSignal.timeout(120_000),
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
