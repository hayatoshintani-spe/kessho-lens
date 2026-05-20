"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Headphones,
  LayoutDashboard,
  Mic2,
  Volume2,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";

const NAV = [
  { href: "/dashboard", label: "今日", icon: LayoutDashboard },
  { href: "/study/vocabulary", label: "単語", icon: BookOpen },
  { href: "/study/listening", label: "聴く", icon: Headphones },
  { href: "/study/shadowing", label: "シャドー", icon: Volume2 },
  { href: "/study/speaking", label: "話す", icon: Mic2 },
];

export function MobileNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 border-t bg-white md:hidden">
      <ul className="grid grid-cols-5">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  "flex flex-col items-center gap-1 py-2 text-[11px]",
                  active ? "text-blue-600" : "text-slate-600",
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
