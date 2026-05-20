"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { StudyPageShell } from "@/components/study/StudyPageShell";
import { SessionTimer } from "@/components/study/SessionTimer";
import { SelfRatingStars } from "@/components/study/SelfRatingStars";
import { AudioRecorder } from "@/components/study/AudioRecorder";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { finishSession } from "@/lib/study/session";
import type { ContentItem } from "@/lib/types/db";

interface SpeakingBody {
  prompt: string;
  tips?: string;
}

export function SpeakingSession({ items }: { items: ContentItem[] }) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();

  const [startedAt] = useState(Date.now());
  const [index, setIndex] = useState(0);
  const [rating, setRating] = useState(3);
  const [note, setNote] = useState("");
  const [blob, setBlob] = useState<Blob | null>(null);
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);

  const current = items[index];
  const total = items.length;
  const body = current ? (current.body as unknown as SpeakingBody) : null;

  async function saveAttempt() {
    if (!current || !body) return;
    setSaving(true);
    try {
      const { data: userData } = await supabase.auth.getUser();
      const user = userData.user;
      if (!user) return;

      let recordingPath: string | null = null;
      if (blob) {
        const fileName = `${user.id}/speaking/${Date.now()}.webm`;
        const { error: uploadErr } = await supabase.storage
          .from("recordings")
          .upload(fileName, blob, { contentType: blob.type, upsert: false });
        if (!uploadErr) recordingPath = fileName;
      }

      await supabase.from("speaking_attempts").insert({
        user_id: user.id,
        prompt: body.prompt,
        recording_path: recordingPath,
        self_rating: rating,
        note: note || null,
      });

      if (index + 1 >= total) {
        await finalize();
      } else {
        setIndex((i) => i + 1);
        setRating(3);
        setNote("");
        setBlob(null);
      }
    } finally {
      setSaving(false);
    }
  }

  async function finalize() {
    const duration = Math.floor((Date.now() - startedAt) / 1000);
    const { data: userData } = await supabase.auth.getUser();
    const user = userData.user;
    if (user) {
      await finishSession(supabase, {
        user_id: user.id,
        skill_code: "speaking",
        started_at: new Date(startedAt),
        duration_seconds: duration,
        item_count: index + 1,
        correct_count: 0,
        note: note || null,
      });
    }
    setDone(true);
  }

  if (total === 0) {
    return (
      <StudyPageShell
        title="スピーキング"
        description="お題がありません。/admin から追加してください。"
        skillLabel="スピーキング"
        skillBadgeClass="skill-speaking"
      />
    );
  }

  if (done) {
    return (
      <StudyPageShell title="スピーキング セッション終了" skillLabel="スピーキング" skillBadgeClass="skill-speaking">
        <Card>
          <CardContent className="space-y-3 p-6">
            <p>お疲れさまでした！ {index + 1} 本のお題に取り組みました。</p>
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
      title="スピーキング"
      description="お題を読み、30〜60秒で口頭回答 → 録音 → 自己評価。"
      skillLabel="スピーキング"
      skillBadgeClass="skill-speaking"
      right={<SessionTimer running startedAt={startedAt} />}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle>{current.title}</CardTitle>
          <Badge variant="outline">難易度 {current.difficulty}</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-md border bg-amber-50 p-4 leading-relaxed text-amber-900">
            <div className="text-xs font-medium uppercase tracking-wide">prompt</div>
            <div className="mt-1">{body?.prompt}</div>
          </div>
          {body?.tips && (
            <div className="rounded-md border bg-blue-50 p-3 text-sm text-blue-900">
              <span className="font-medium">Tips:</span> {body.tips}
            </div>
          )}

          <AudioRecorder onRecorded={setBlob} />

          <div>
            <div className="mb-2 text-sm font-medium">自己評価</div>
            <SelfRatingStars value={rating} onChange={setRating} />
          </div>

          <div>
            <div className="mb-1 text-sm font-medium">メモ（任意）</div>
            <Textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="言えなかった表現・次回のリベンジ"
            />
          </div>

          <Button onClick={saveAttempt} disabled={saving} className="w-full">
            {saving ? "保存中…" : index + 1 >= total ? "保存してセッション終了" : "保存して次へ"}
          </Button>
        </CardContent>
      </Card>
    </StudyPageShell>
  );
}
