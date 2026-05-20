"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils/cn";

interface Props {
  title: string;
  description?: string;
  skillBadgeClass?: string;
  skillLabel?: string;
  right?: React.ReactNode;
  children?: React.ReactNode;
}

export function StudyPageShell({
  title,
  description,
  skillBadgeClass,
  skillLabel,
  right,
  children,
}: Props) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex h-9 w-9 items-center justify-center rounded-md border bg-white text-slate-700 hover:bg-slate-50"
            aria-label="ダッシュボードへ戻る"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            {skillLabel && (
              <span className={cn("inline-block rounded-full px-2 py-0.5 text-xs font-medium", skillBadgeClass)}>
                {skillLabel}
              </span>
            )}
            <h1 className="mt-1 text-xl font-bold tracking-tight md:text-2xl">{title}</h1>
            {description && (
              <p className="text-sm text-slate-600">{description}</p>
            )}
          </div>
        </div>
        {right}
      </div>
      {children}
    </div>
  );
}
