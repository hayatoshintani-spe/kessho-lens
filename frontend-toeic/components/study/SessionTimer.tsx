"use client";

import { useEffect, useState } from "react";
import { Timer } from "lucide-react";

interface Props {
  running: boolean;
  startedAt: number | null;
  className?: string;
}

export function SessionTimer({ running, startedAt, className }: Props) {
  const [now, setNow] = useState<number>(Date.now());

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [running]);

  const elapsedSeconds = startedAt ? Math.floor((now - startedAt) / 1000) : 0;
  const mm = String(Math.floor(elapsedSeconds / 60)).padStart(2, "0");
  const ss = String(elapsedSeconds % 60).padStart(2, "0");

  return (
    <div className={`inline-flex items-center gap-2 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white tabular-nums ${className ?? ""}`}>
      <Timer className="h-4 w-4" />
      {mm}:{ss}
    </div>
  );
}
