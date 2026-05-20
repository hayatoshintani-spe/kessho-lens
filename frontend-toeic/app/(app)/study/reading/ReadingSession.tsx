"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { StudyPageShell } from "@/components/study/StudyPageShell";
import { SessionTimer } from "@/components/study/SessionTimer";
import { SelfRatingStars } from "@/components/study/SelfRatingStars";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { finishSession } from "@/lib/study/session";
import { safeWpm } from "@/lib/utils/format";
import type { ContentItem } from "@/lib/types/db";

interface ReadingBody {
  passage: string;
  word_count?: number;
  questions?: { q: string; a: string }[];
}

export function ReadingSession({ items }: { items: ContentItem[] }) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();

  const [startedAt] = useState(Date.now());
  const [index, setIndex] = useState(0);
  const [phase, setPhase] = useState<"reading" | "review">("reading");
  const [readStart, setReadStart] = useState<number>(Date.now());
  const [readSeconds, setReadSeconds] = useState(0);
  const [comprehension, setComprehension] = useState(3);
  const [note, setNote] = useState("");
  const [savedItems, setSavedItems] = useState(0);
  const [done, setDone] = useState(false);

  const current = items[index];
  const total = items.length;

  const body = useMemo<ReadingBody | null>(() => {
    if (!current) return null;
    return current.body as unknown as ReadingBody;
  }, [current]);

  const wordCount =
    body?.word_count ??
    (body?.passage ? body.passage.trim().split(/\s+/).length : 0);

  const wpm = safeWpm(wordCount, readSeconds);

  useEffect(() => {
    if (phase === "reading") setReadStart(Date.now());
  }, [phase, index]);

  function finishReading() {
    const secs = Math.max(1, Math.floor((Date.now() - readStart) / 1000));
    setReadSeconds(secs);
    setPhase("review");
  }

  async function save() {
    const { data: userData } = await supabase.auth.getUser();
    const user = userData.user;
    if (user && current) {
      await supabase.from("reading_attempts").insert({
        user_id: user.id,
        content_item_id: current.id,
        read_seconds: readSeconds,
        word_count: wordCount,
        wpm,
        comprehension,
      });
    }
    setSavedItems((n) => n + 1);

    if (index + 1 >= total) {
      await finalize();
    } else {
      setIndex((i) => i + 1);
      setComprehension(3);
      setPhase("reading");
      setReadSeconds(0);
    }
  }

  async function finalize() {
    const duration = Math.floor((Date.now() - startedAt) / 1000);
    const { data: userData } = await supabase.auth.getUser();
    const user = userData.user;
    if (user) {
      await finishSession(supabase, {
        user_id: user.id,
        skill_code: "reading",
        started_at: new Date(startedAt),
        duration_seconds: duration,
        item_count: savedItems + 1,
        correct_count: 0,
        note: note || null,
      });
    }
    setDone(true);
  }

  if (total === 0) {
    return (
      <StudyPageShell
        title="英読"
        description="まだ教材がありません。/admin から追加してください。"
        skillLabel="英読"
        skillBadgeClass="skill-reading"
      />
    );
  }

  if (done) {
    return (
      <StudyPageShell title="英読セッション終了" skillLabel="英読" skillBadgeClass="skill-reading">
        <Card>
          <CardContent className="space-y-3 p-6">
            <p>お疲れさまでした！ {savedItems + 1} 本の文章を読みました。</p>
            <div className="flex gap-2">
              <Button onClick={() => router.replace("/dashboard")}>ダッシュボードへ</Button>
              <Button variant="outline" onClick={() => router.refresh()}>
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
      title="英読"
      description="集中して読み、最後に理解度を自己評価。"
      skillLabel="英読"
      skillBadgeClass="skill-reading"
      right={<SessionTimer running startedAt={startedAt} />}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle>{current.title}</CardTitle>
          <Badge variant="outline">難易度 {current.difficulty}</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <article className="prose prose-slate max-w-none rounded-md border bg-slate-50 p-4 leading-relaxed">
            {body?.passage}
          </article>

          {phase === "reading" ? (
            <Button onClick={finishReading} className="w-full">
              読み終わった → 理解度を入力
            </Button>
          ) : (
            <div className="space-y-4 rounded-md border p-4">
              <div className="grid grid-cols-3 gap-3 text-center">
                <Stat label="読了時間" value={`${readSeconds}秒`} />
                <Stat label="語数" value={`${wordCount}`} />
                <Stat label="WPM" value={`${wpm}`} />
              </div>

              <div>
                <div className="mb-2 text-sm font-medium">理解度（自己評価）</div>
                <SelfRatingStars value={comprehension} onChange={setComprehension} />
              </div>

              {body?.questions && body.questions.length > 0 && (
                <div>
                  <div className="mb-1 text-sm font-medium">確認用</div>
                  <ul className="space-y-2 text-sm">
                    {body.questions.map((q, i) => (
                      <details key={i} className="rounded-md border p-2">
                        <summary className="cursor-pointer">{q.q}</summary>
                        <div className="mt-1 text-slate-600">参考: {q.a}</div>
                      </details>
                    ))}
                  </ul>
                </div>
              )}

              <Button onClick={save} className="w-full">
                {index + 1 >= total ? "保存してセッション終了" : "保存して次へ"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">セッションメモ（任意）</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="知らなかった語彙・構文など"
          />
        </CardContent>
      </Card>
    </StudyPageShell>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-white p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
