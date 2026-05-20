"use client";

import { Star } from "lucide-react";
import { cn } from "@/lib/utils/cn";

interface Props {
  value: number;
  onChange: (v: number) => void;
  size?: "sm" | "md" | "lg";
}

export function SelfRatingStars({ value, onChange, size = "md" }: Props) {
  const sizeClass = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-7 w-7" : "h-5 w-5";
  return (
    <div className="inline-flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          aria-label={`${n} stars`}
          className="rounded p-0.5 hover:bg-slate-100"
        >
          <Star
            className={cn(
              sizeClass,
              n <= value ? "fill-amber-400 stroke-amber-500" : "stroke-slate-300",
            )}
          />
        </button>
      ))}
    </div>
  );
}
