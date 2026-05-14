import { NextRequest, NextResponse } from 'next/server';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

const CRON_SECRET = process.env.CRON_SECRET ?? '';

export async function GET(req: NextRequest) {
  // Verify Vercel cron authorization
  const authHeader = req.headers.get('authorization');
  if (
    CRON_SECRET &&
    authHeader !== `Bearer ${CRON_SECRET}`
  ) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const res = await fetch(`${API_BASE}/api/cron/run-daily`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ secret: CRON_SECRET }),
    });

    const data = await res.json();

    if (!res.ok) {
      console.error('[trigger-daily] Backend error:', data);
      return NextResponse.json(
        { error: 'Backend simulation failed', details: data },
        { status: res.status },
      );
    }

    console.log('[trigger-daily] Simulation triggered:', data);
    return NextResponse.json({
      success: true,
      message: data.message ?? 'Simulation started',
      date: data.date,
      triggeredAt: new Date().toISOString(),
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('[trigger-daily] Fetch error:', message);
    return NextResponse.json(
      { error: 'Failed to reach backend', details: message },
      { status: 500 },
    );
  }
}

// Also support POST for manual triggers
export async function POST(req: NextRequest) {
  return GET(req);
}
