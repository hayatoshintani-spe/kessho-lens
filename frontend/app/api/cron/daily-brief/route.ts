// Vercel Cron からの呼び出しを受けてバックエンドの
// /api/intel/cron/daily-brief に転送する。
//
// Vercel Cron は GET で `Authorization: Bearer ${CRON_SECRET}` を付与する。
// CRON_SECRET 環境変数は Vercel プロジェクトとバックエンドの両方に
// 同じ値を設定しておく必要がある。

import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
const CRON_SECRET = process.env.CRON_SECRET ?? '';

async function handle(req: NextRequest) {
  if (CRON_SECRET) {
    const auth = req.headers.get('authorization');
    if (auth !== `Bearer ${CRON_SECRET}`) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
  }

  try {
    const res = await fetch(`${API_BASE}/api/intel/cron/daily-brief`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${CRON_SECRET}`,
      },
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      console.error('[cron/daily-brief] Backend error:', res.status, data);
      return NextResponse.json(
        { error: 'Backend error', status: res.status, details: data },
        { status: res.status },
      );
    }

    console.log('[cron/daily-brief]', JSON.stringify(data));
    return NextResponse.json({
      success: true,
      triggeredAt: new Date().toISOString(),
      ...data,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('[cron/daily-brief] Fetch error:', message);
    return NextResponse.json(
      { error: 'Failed to reach backend', details: message },
      { status: 500 },
    );
  }
}

export async function GET(req: NextRequest) {
  return handle(req);
}

export async function POST(req: NextRequest) {
  return handle(req);
}
