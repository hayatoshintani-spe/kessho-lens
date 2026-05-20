"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  GraduationCap,
  Headphones,
  History,
  LayoutDashboard,
  Mic2,
  NotebookPen,
  Repeat2,
  ScrollText,
  Settings2,
  Sparkles,
  Volume2,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";

const NAV = [
  { href: "/dashboard", label: "ダッシュボード", icon: LayoutDashboard },
  { href: "/study/vocabulary", label: "単語", icon: BookOpen },
  { href: "/study/grammar", label: "文法", icon: NotebookPen },
  { href: "/study/listening", label: "リスニング", icon: Headphones },
  { href: "/study/shadowing", label: "シャドーイング", icon: Volume2 },
  { href: "/study/reading", label: "英読", icon: ScrollText },
  { href: "/study/speaking", label: "スピーキング", icon: Mic2 },
  { href: "/logs", label: "学習履歴", icon: History },
  { href: "/review/weekly", label: "週次レビュー", icon: Repeat2 },
  { href: "/admin", label: "教材管理", icon: Settings2 },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden h-screen w-60 shrink-0 flex-col border-r bg-white md:flex">
      <div className="flex h-14 items-center gap-2 border-b px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-blue-50">
          <Sparkles className="h-4 w-4 text-blue-600" />
        </div>
        <span className="text-sm font-semibold">Kessho Lens English</span>
      </div>
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-0.5">
          {NAV.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-700 transition-colors hover:bg-slate-100",
                    active && "bg-slate-900 text-white hover:bg-slate-900",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="border-t p-3 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <GraduationCap className="h-4 w-4" />
          <span>TOEIC 900 へ。</span>
        </div>
      </div>
    </aside>
  );
}
