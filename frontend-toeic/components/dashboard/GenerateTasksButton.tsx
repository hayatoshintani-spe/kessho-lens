"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Loader2, Wand2 } from "lucide-react";

export function GenerateTasksButton({ size = "sm" }: { size?: "sm" | "default" }) {
  const [pending, start] = useTransition();
  const router = useRouter();

  function go() {
    start(async () => {
      const res = await fetch("/api/tasks/generate", { method: "POST" });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        alert(body.error ?? "タスク生成に失敗しました");
        return;
      }
      router.refresh();
    });
  }

  return (
    <Button size={size} onClick={go} disabled={pending}>
      {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
      今日のタスクを生成
    </Button>
  );
}
