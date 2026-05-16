'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Newspaper,
  Database,
  GitMerge,
  Radar,
  Link2,
  Plus,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/intel', label: 'ブリーフ', icon: Newspaper },
  { href: '/intel/cards', label: 'カードDB', icon: Database },
  { href: '/intel/cards/new', label: '新規カード', icon: Plus },
  { href: '/intel/council', label: 'AI会議', icon: GitMerge },
  { href: '/intel/watchlist', label: 'ウォッチリスト', icon: Radar },
  { href: '/intel/notion', label: 'Notion連携', icon: Link2 },
];

function isItemActive(href: string, pathname: string): boolean {
  if (href === '/intel') {
    // 「ブリーフ」は /intel と /intel/brief 配下のみアクティブ。
    // /intel/cards などの兄弟ルートではアクティブにしない。
    return pathname === '/intel' || pathname.startsWith('/intel/brief');
  }
  if (href === '/intel/cards') {
    // /intel/cards/new は別ナビ項目があるので除外
    return (
      (pathname === '/intel/cards' || pathname.startsWith('/intel/cards/')) &&
      pathname !== '/intel/cards/new'
    );
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="w-[240px] h-screen bg-bg-sidebar border-r border-border flex flex-col select-none">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-accent-gold/20 border border-accent-gold/40 flex items-center justify-center flex-shrink-0">
            <Newspaper className="w-4 h-4 text-accent-gold" />
          </div>
          <div>
            <div className="text-text-primary font-bold text-sm leading-tight">
              Tsuburaya Intel
            </div>
            <div className="text-text-muted text-[10px] leading-tight mt-0.5 font-mono uppercase tracking-wider">
              Intelligence Brief
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <div className="flex-1 px-3 py-4 overflow-y-auto">
        <div className="space-y-0.5">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = isItemActive(href, pathname);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all duration-150',
                  isActive
                    ? 'bg-accent-gold/10 text-accent-gold border border-accent-gold/20'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated',
                )}
              >
                <Icon
                  className={cn(
                    'w-4 h-4 flex-shrink-0',
                    isActive ? 'text-accent-gold' : 'text-text-muted',
                  )}
                />
                <span>{label}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-accent-gold" />
                )}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-2 text-text-muted text-[11px]">
          <Clock className="w-3 h-3 flex-shrink-0" />
          <span>日次ブリーフ自動生成</span>
        </div>
        <div className="mt-1.5 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-profit animate-pulse-slow" />
          <span className="text-text-muted text-[11px]">システム稼働中</span>
        </div>
      </div>
    </nav>
  );
}
