"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle2, RefreshCcw, ThumbsUp, XCircle } from "lucide-react";
import { StudyPageShell } from "@/components/study/StudyPageShell";
import { SessionTimer } from "@/components/study/SessionTimer";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { finishSession } from "@/lib/study/session";
import { nextReview } from "@/lib/tasks/reviewScheduler";
import type { VocabularyItem } from "@/lib/types/db";

export function VocabularySession({ items }: { items: VocabularyItem[] }) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();

  const [startedAt] = useState(Date.now());
  const [running, setRunning] = useState(true);
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [note, setNote] = useState("");
  const [stats, setStats] = useState({ known: 0, hard: 0, forgot: 0 });
  const [saving, setSaving] = useState(false);
  const [doneMessage, setDoneMessage] = useState<string | null>(null);

  const current = items[index];
  const total = items.length;
  const remaining = total - index;

  useEffect(() => {
    setRevealed(false);
  }, [index]);

  async function rate(rating: "known" | "hard" | "forgot") {
    if (!current) return;
    setStats((s) => ({ ...s, [rating]: s[rating] + 1 }));

    // Update review row (upsert).
    const { data: existing } = await supabase
      .from("user_vocabulary_reviews")
      .select("repetition, interval_days, ease")
      .eq("vocabulary_item_id", current.id)
      .maybeSingle();

    const sched = nextReview(
      {
        repetition: existing?.repetition ?? 0,
        interval_days: existing?.interval_days ?? 0,
        ease: existing?.ease ?? 2.5,
      },
      rating,
    );

    const { data: userData } = await supabase.auth.getUser();
    const user = userData.user;
    if (user) {
      await supabase.from("user_vocabulary_reviews").upsert(
        {
          user_id: user.id,
          vocabulary_item_id: current.id,
          rating,
          repetition: sched.repetition,
          interval_days: sched.interval_days,
          ease: sched.ease,
          next_review_on: sched.next_review_on,
          last_reviewed_at: new Date().toISOString(),
        },
        { onConflict: "user_id,vocabulary_item_id" },
      );
    }

    if (index + 1 >= total) {
      // Finish.
      await endSession();
    } else {
      setIndex((i) => i + 1);
    }
  }

  async function endSession() {
    setRunning(false);
    setSaving(true);
    const duration = Math.floor((Date.now() - startedAt) / 1000);
    try {
      const { data: userData } = await supabase.auth.getUser();
      const user = userData.user;
      if (user) {
        await finishSession(supabase, {
          user_id: user.id,
          skill_code: "vocabulary",
          started_at: new Date(startedAt),
          duration_seconds: duration,
          item_count: stats.known + stats.hard + stats.forgot,
          correct_count: stats.known,
          note: note || null,
        });
      }
      setDoneMessage(
        `お疲れさまでした！ ${stats.known + stats.hard + stats.forgot} 語、${Math.round(duration / 60)} 分。`,
      );
    } finally {
      setSaving(false);
    }
  }

  const summary = useMemo(() => stats, [stats]);

  if (total === 0) {
    return (
      <StudyPageShell
        title="単語"
        description="表示できる単語がありません。/admin から教材を追加してください。"
        skillLabel="単語"
        skillBadgeClass="skill-vocabulary"
      />
    );
  }

  if (doneMessage) {
    return (
      <StudyPageShell
        title="単語セッション終了"
        skillLabel="単語"
        skillBadgeClass="skill-vocabulary"
      >
        <Card>
          <CardContent className="space-y-3 p-6">
            <p className="text-base">{doneMessage}</p>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="rounded-md bg-emerald-50 p-3">
                <div className="text-xs text-emerald-700">覚えた</div>
                <div className="text-xl font-semibold text-emerald-700">{summary.known}</div>
              </div>
              <div className="rounded-md bg-amber-50 p-3">
                <div className="text-xs text-amber-700">難しい</div>
                <div className="text-xl font-semibold text-amber-700">{summary.hard}</div>
              </div>
              <div className="rounded-md bg-rose-50 p-3">
                <div className="text-xs text-rose-700">忘れた</div>
                <div className="text-xl font-semibold text-rose-700">{summary.forgot}</div>
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <Button onClick={() => router.replace("/dashboard")}>ダッシュボードへ</Button>
              <Button
                variant="outline"
                onClick={() => router.refresh()}
              >
                もう一度
              </Button>
            </div>
          </CardContent>
        </Card>
      </StudyPageShell>
    );
  }

  return (
    <StudyPageShell
      title="単語"
      description="覚えた・難しい・忘れた で素早く判定。"
      skillLabel="単語"
      skillBadgeClass="skill-vocabulary"
      right={<SessionTimer running={running} startedAt={startedAt} />}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-sm text-slate-500">
            {index + 1} / {total}
          </CardTitle>
          <Badge variant="outline">難易度 {current.difficulty}</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <div className="text-3xl font-bold tracking-tight">{current.word}</div>
            {current.part_of_speech && (
              <div className="mt-1 text-xs text-slate-500">{current.part_of_speech}</div>
            )}
          </div>

          {!revealed ? (
            <Button className="w-full" variant="outline" onClick={() => setRevealed(true)}>
              意味を表示
            </Button>
          ) : (
            <div className="space-y-3 rounded-md border bg-slate-50 p-4 text-sm">
              <div>
                <div className="text-xs text-slate-500">意味</div>
                <div className="font-medium">{current.meaning}</div>
              </div>
              {current.example_en && (
                <div>
                  <div className="text-xs text-slate-500">例文</div>
                  <div>{current.example_en}</div>
                  {current.example_ja && (
                    <div className="text-slate-600">{current.example_ja}</div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-3 gap-2 pt-1">
            <Button
              variant="outline"
              className="border-rose-200 text-rose-700 hover:bg-rose-50"
              onClick={() => rate("forgot")}
              disabled={!revealed}
            >
              <XCircle className="h-4 w-4" />
              忘れた
            </Button>
            <Button
              variant="outline"
              className="border-amber-200 text-amber-700 hover:bg-amber-50"
              onClick={() => rate("hard")}
              disabled={!revealed}
            >
              <RefreshCcw className="h-4 w-4" />
              難しい
            </Button>
            <Button
              variant="outline"
              className="border-emerald-200 text-emerald-700 hover:bg-emerald-50"
              onClick={() => rate("known")}
              disabled={!revealed}
            >
              <ThumbsUp className="h-4 w-4" />
              覚えた
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">セッションメモ（任意）</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="例: 派生語を一緒にまとめておく"
          />
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3 text-slate-500">
              <span className="inline-flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                {summary.known}
              </span>
              <span>{summary.hard} 難しい</span>
              <span>{summary.forgot} 忘れた</span>
              <span>残り {remaining}</span>
            </div>
            <Button variant="outline" onClick={endSession} disabled={saving}>
              セッション終了
            </Button>
          </div>
        </CardContent>
      </Card>
    </StudyPageShell>
  );
}
