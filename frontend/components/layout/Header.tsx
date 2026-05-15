'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, Bell, Menu, X, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { formatDatetime } from '@/lib/utils';

const ROUTE_LABELS: Record<string, string> = {
  '/': 'ダッシュボード',
  '/agents': 'AIエージェント一覧',
  '/meetings': '投資会議ログ',
  '/reports': '日次レポート',
  '/discovery': '銘柄探索ログ',
  '/advisor': '個人資産アドバイス',
  '/settings': '設定',
};

export default function Header() {
  const pathname = usePathname();
  const [now, setNow] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const tick = () => setNow(formatDatetime(new Date().toISOString()));
    tick();
    const t = setInterval(tick, 30_000);
    return () => clearInterval(t);
  }, []);

  const routeLabel =
    ROUTE_LABELS[pathname] ??
    (pathname.startsWith('/agents/') ? 'エージェント詳細' :
      pathname.startsWith('/meetings/') ? '会議詳細' :
        pathname.startsWith('/reports/') ? 'レポート詳細' :
          'ページ');

  return (
    <>
      <header className="sticky top-0 z-30 bg-bg-primary/80 backdrop-blur border-b border-border px-4 md:px-6 h-14 flex items-center justify-between flex-shrink-0">
        {/* Left: mobile menu + breadcrumb */}
        <div className="flex items-center gap-3">
          {/* Mobile menu toggle */}
          <button
            className="md:hidden text-text-secondary hover:text-text-primary"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label="メニュー"
          >
            {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="text-text-secondary text-sm">
            <span className="text-text-primary font-medium">{routeLabel}</span>
          </div>
        </div>

        {/* Right: time + actions */}
        <div className="flex items-center gap-3">
          {now && (
            <span className="hidden sm:block text-text-muted text-xs font-mono">
              {now}
            </span>
          )}
          <button
            className="text-text-muted hover:text-text-secondary transition-colors"
            title="更新"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button className="text-text-muted hover:text-text-secondary transition-colors">
            <Bell className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Mobile nav overlay — outside <header> to avoid backdrop-filter containing block */}
      {menuOpen && (
        <div className="md:hidden fixed inset-0 top-14 z-50 bg-bg-sidebar border-t border-border">
          <nav className="p-4 space-y-1">
            {[
              { href: '/', label: 'ダッシュボード' },
              { href: '/agents', label: 'AIエージェント' },
              { href: '/meetings', label: '投資会議ログ' },
              { href: '/reports', label: '日次レポート' },
              { href: '/discovery', label: '銘柄探索' },
              { href: '/advisor', label: '個人アドバイス' },
              { href: '/settings', label: '設定' },
            ].map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMenuOpen(false)}
                className={cn(
                  'block px-4 py-3 rounded-md text-sm transition-colors',
                  pathname === href
                    ? 'bg-accent-gold/10 text-accent-gold'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated',
                )}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </>
  );
}
