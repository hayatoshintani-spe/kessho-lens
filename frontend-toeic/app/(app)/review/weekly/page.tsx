import { redirect } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { SKILL_CODES, SKILL_LABEL, type SkillCode } from "@/lib/types/db";
import { formatDate, formatISO, weekRange } from "@/lib/utils/date";

export default async function WeeklyReviewPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { start, end } = weekRange(new Date());
  const startISO = formatISO(start, { representation: "date" });
  const endISO = formatISO(end, { representation: "date" });

  const { data: sessions } = await supabase
    .from("learning_sessions")
    .select("skill_code, duration_seconds, accuracy")
    .eq("user_id", user.id)
    .gte("started_at", `${startISO}T00:00:00`)
    .lte("started_at", `${endISO}T23:59:59`);

  const totalSeconds = (sessions ?? []).reduce((a, s) => a + s.duration_seconds, 0);
  const totalMinutes = Math.round(totalSeconds / 60);

  const bySkill: Record<SkillCode, { minutes: number; accSum: number; accCount: number }> = {
    vocabulary: { minutes: 0, accSum: 0, accCount: 0 },
    grammar: { minutes: 0, accSum: 0, accCount: 0 },
    listening: { minutes: 0, accSum: 0, accCount: 0 },
    shadowing: { minutes: 0, accSum: 0, accCount: 0 },
    reading: { minutes: 0, accSum: 0, accCount: 0 },
    speaking: { minutes: 0, accSum: 0, accCount: 0 },
  };
  for (const s of sessions ?? []) {
    const code = s.skill_code as SkillCode;
    bySkill[code].minutes += Math.round(s.duration_seconds / 60);
    if (s.accuracy != null) {
      bySkill[code].accSum += Number(s.accuracy);
      bySkill[code].accCount += 1;
    }
  }

  // Identify weakest = lowest minutes (excluding zero); fallback any zero.
  const skillsByMinutes = SKILL_CODES.map((s) => ({ s, m: bySkill[s].minutes }));
  const studied = skillsByMinutes.filter((x) => x.m > 0);
  const weakest = studied.length
    ? studied.sort((a, b) => a.m - b.m)[0].s
    : skillsByMinutes[0].s;
  const top = studied.length
    ? studied.sort((a, b) => b.m - a.m)[0].s
    : skillsByMinutes[0].s;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">週次レビュー</h1>
        <p className="text-sm text-slate-600">
          {formatDate(start)} 〜 {formatDate(end)} の学習サマリー
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>今週の合計</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-3 gap-3">
          <div className="rounded-md border p-3 text-center">
            <div className="text-xs text-slate-500">合計</div>
            <div className="text-2xl font-semibold">{totalMinutes}<span className="text-sm">分</span></div>
          </div>
          <div className="rounded-md border p-3 text-center">
            <div className="text-xs text-slate-500">最も時間を割いた</div>
            <div className="text-base font-medium">{SKILL_LABEL[top]}</div>
          </div>
          <div className="rounded-md border p-3 text-center">
            <div className="text-xs text-slate-500">最も少なかった</div>
            <div className="text-base font-medium">{SKILL_LABEL[weakest]}</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>スキル別</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="divide-y">
            {SKILL_CODES.map((s) => {
              const d = bySkill[s];
              const avgAcc = d.accCount > 0 ? d.accSum / d.accCount : null;
              return (
                <li key={s} className="flex items-center justify-between py-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{SKILL_LABEL[s]}</Badge>
                  </div>
                  <div className="flex items-center gap-3 text-slate-600">
                    <span>{d.minutes} 分</span>
                    {avgAcc != null && <span>正答 {Math.round(avgAcc * 100)}%</span>}
                  </div>
                </li>
              );
            })}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>次週の重点</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-700">
          時間配分が少なかった <strong>{SKILL_LABEL[weakest]}</strong> を 1日あたり 5〜10分 多めに割り当てるのがおすすめです。
          <br />
          オンボーディング画面の「苦手分野」に追加すると、自動でタスク配分に反映されます。
        </CardContent>
      </Card>
    </div>
  );
}
