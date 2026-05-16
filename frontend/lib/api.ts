// Backend health / warm-up helper
//
// Render の無料プランはコールドスタートに ~50 秒かかるため、
// 各ページの初回ロードで /api/health を叩いて起動を待つ。

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'https://kessho-lens-backend.onrender.com';

/**
 * /api/health を maxMs ミリ秒まで繰り返し叩き、200が返ったら true。
 * バックエンドのコールドスタートを待つために各ページの先頭で使う。
 */
export async function warmupBackend(maxMs = 70_000): Promise<boolean> {
  const deadline = Date.now() + maxMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
      if (res.ok) return true;
    } catch {
      // network error — keep waiting
    }
    const remaining = deadline - Date.now();
    if (remaining <= 0) break;
    await new Promise(r => setTimeout(r, Math.min(5_000, remaining)));
  }
  return false;
}
