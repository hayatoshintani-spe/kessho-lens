'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, Bell, Menu, X } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { formatDatetime } from '@/lib/utils';

const ROUTE_LABELS: Record<string, string> = {
  '/': 'ブリーフ',
  '/intel': 'ブリーフ',
  '/intel/cards': 'カードDB',
  '/intel/cards/new': '新規カード',
  '/intel/council': 'AI会議',
  '/intel/watchlist': 'ウォッチリスト',
  '/intel/delivery': 'メール配信',
  '/intel/notion': 'Notion連携',
};

const MOBILE_NAV_ITEMS = [
  { href: '/intel', label: 'ブリーフ' },
  { href: '/intel/cards', label: 'カードDB' },
  { href: '/intel/cards/new', label: '新規カード' },
  { href: '/intel/council', label: 'AI会議' },
  { href: '/intel/watchlist', label: 'ウォッチリスト' },
  { href: '/intel/delivery', label: 'メール配信' },
  { href: '/intel/notion', label: 'Notion連携' },
];

function deriveLabel(pathname: string): string {
  if (ROUTE_LABELS[pathname]) return ROUTE_LABELS[pathname];
  if (pathname.startsWith('/intel/brief/')) return 'ブリーフ詳細';
  if (pathname.startsWith('/intel/cards/')) return 'カード詳細';
  if (pathname.startsWith('/intel/council/')) return 'AI会議詳細';
  return 'ページ';
}

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

  const routeLabel = deriveLabel(pathname);

  return (
    <>
      <header className="sticky top-0 z-30 bg-bg-primary/80 backdrop-blur border-b border-border px-4 md:px-6 h-14 flex items-center justify-between flex-shrink-0">
        {/* Left: mobile menu + breadcrumb */}
        <div className="flex items-center gap-3">
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

      {menuOpen && (
        <div className="md:hidden fixed inset-0 top-14 z-50 bg-bg-sidebar border-t border-border">
          <nav className="p-4 space-y-1">
            {MOBILE_NAV_ITEMS.map(({ href, label }) => (
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
