"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { StudyPageShell } from "@/components/study/StudyPageShell";
import { SessionTimer } from "@/components/study/SessionTimer";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { finishSession } from "@/lib/study/session";
import { cn } from "@/lib/utils/cn";
import type { QuizQuestion, SkillCode } from "@/lib/types/db";
import { CheckCircle2, XCircle } from "lucide-react";

interface Props {
  items: QuizQuestion[];
  skillCode: SkillCode;
  title: string;
  description: string;
  skillLabel: string;
  skillBadgeClass: string;
}

export function QuizSession({
  items,
  skillCode,
  title,
  description,
  skillLabel,
  skillBadgeClass,
}: Props) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();
  const [startedAt] = useState(Date.now());
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);
  const [note, setNote] = useState("");
  const [questionStart, setQuestionStart] = useState(Date.now());

  const current = items[index];
  const total = items.length;

  async function answer() {
    if (selected == null || !current) return;
    const isCorrect = selected === current.answer_index;
    setRevealed(true);
    if (isCorrect) setCorrect((c) => c + 1);

    const elapsed = Math.floor((Date.now() - questionStart) / 1000);
    const { data: userData } = await supabase.auth.getUser();
    const user = userData.user;
    if (user) {
      await supabase.from("quiz_attempts").insert({
        user_id: user.id,
        quiz_question_id: current.id,
        selected_index: selected,
        is_correct: isCorrect,
        elapsed_seconds: elapsed,
      });
    }
  }

  function next() {
    if (index + 1 >= total) {
      finishAll();
      return;
    }
    setIndex((i) => i + 1);
    setSelected(null);
    setRevealed(false);
    setQuestionStart(Date.now());
  }

  async function finishAll() {
    const duration = Math.floor((Date.now() - startedAt) / 1000);
    const { data: userData } = await supabase.auth.getUser();
    const user = userData.user;
    if (user) {
      await finishSession(supabase, {
        user_id: user.id,
        skill_code: skillCode,
        started_at: new Date(startedAt),
        duration_seconds: duration,
        item_count: total,
        correct_count: correct,
        note: note || null,
      });
    }
    setDone(true);
  }

  if (total === 0) {
    return (
      <StudyPageShell
        title={title}
        description="まだ問題がありません。/admin から追加してください。"
        skillLabel={skillLabel}
        skillBadgeClass={skillBadgeClass}
      />
    );
  }

  if (done) {
    const minutes = Math.round((Date.now() - startedAt) / 1000 / 60);
    return (
      <StudyPageShell title={`${title} セッション終了`} skillLabel={skillLabel} skillBadgeClass={skillBadgeClass}>
        <Card>
          <CardContent className="space-y-3 p-6">
            <p>
              {correct} / {total} 問正解 ・ {minutes} 分
            </p>
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
      title={title}
      description={description}
      skillLabel={skillLabel}
      skillBadgeClass={skillBadgeClass}
      right={<SessionTimer running startedAt={startedAt} />}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-sm text-slate-500">
            {index + 1} / {total}
          </CardTitle>
          <Badge variant="outline">難易度 {current.difficulty}</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          {current.passage && skillCode === "reading" && (
            <div className="rounded-md border bg-slate-50 p-3 text-sm leading-relaxed">
              {current.passage}
            </div>
          )}
          {current.passage && skillCode === "listening" && (
            <details className="rounded-md border bg-slate-50 p-3 text-sm">
              <summary className="cursor-pointer select-none text-slate-700">
                スクリプトを表示（理解できなかった場合）
              </summary>
              <div className="mt-2 leading-relaxed">{current.passage}</div>
            </details>
          )}

          <div className="text-base font-medium">{current.prompt}</div>

          <ul className="space-y-2">
            {current.choices.map((choice, i) => {
              const isCorrect = i === current.answer_index;
              const isSelected = selected === i;
              return (
                <li key={i}>
                  <button
                    type="button"
                    onClick={() => !revealed && setSelected(i)}
                    disabled={revealed}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-md border bg-white p-3 text-left text-sm transition hover:bg-slate-50",
                      isSelected && !revealed && "border-blue-500 ring-2 ring-blue-200",
                      revealed && isCorrect && "border-emerald-500 bg-emerald-50",
                      revealed && isSelected && !isCorrect && "border-rose-500 bg-rose-50",
                    )}
                  >
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border text-xs font-semibold">
                      {String.fromCharCode(65 + i)}
                    </span>
                    <span className="flex-1">{choice}</span>
                    {revealed && isCorrect && (
                      <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    )}
                    {revealed && isSelected && !isCorrect && (
                      <XCircle className="h-4 w-4 text-rose-600" />
                    )}
                  </button>
                </li>
              );
            })}
          </ul>

          {revealed && current.explanation && (
            <div className="rounded-md border bg-blue-50 p-3 text-sm text-blue-900">
              <div className="mb-1 font-medium">解説</div>
              {current.explanation}
            </div>
          )}

          <div className="flex justify-end gap-2">
            {!revealed ? (
              <Button onClick={answer} disabled={selected == null}>
                回答する
              </Button>
            ) : (
              <Button onClick={next}>{index + 1 >= total ? "結果を見る" : "次の問題"}</Button>
            )}
          </div>
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
            placeholder="気づき・苦手だった文法など"
          />
          <p className="mt-2 text-xs text-slate-500">
            正答数: {correct} / {index + (revealed ? 1 : 0)}
          </p>
        </CardContent>
      </Card>
    </StudyPageShell>
  );
}
