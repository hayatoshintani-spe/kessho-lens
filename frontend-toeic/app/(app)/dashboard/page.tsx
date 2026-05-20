import { redirect } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  CalendarCheck2,
  Flame,
  Timer,
  Target,
  Trophy,
} from "lucide-react";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { StatCard } from "@/components/dashboard/StatCard";
import { TodayTaskList } from "@/components/dashboard/TodayTaskList";
import { SkillProgress } from "@/components/dashboard/SkillProgress";
import { WeeklyChart } from "@/components/dashboard/WeeklyChart";
import { GenerateTasksButton } from "@/components/dashboard/GenerateTasksButton";
import { SKILL_CODES, type DailyTask, type SkillCode } from "@/lib/types/db";
import { addDays, formatISO, startOfDay, todayISO, weekRange } from "@/lib/utils/date";
import Link from "next/link";

export default async function DashboardPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: profile } = await supabase
    .from("user_profiles")
    .select("*")
    .eq("id", user.id)
    .maybeSingle();

  if (!profile || !profile.onboarded_at) {
    redirect("/onboarding");
  }

  const today = todayISO();
  const { start, end } = weekRange(new Date());
  const weekStartISO = formatISO(start, { representation: "date" });
  const weekEndISO = formatISO(end, { representation: "date" });

  // Today's tasks
  const { data: tasksData } = await supabase
    .from("daily_tasks")
    .select("*")
    .eq("user_id", user.id)
    .eq("task_date", today);
  const tasks: DailyTask[] = (tasksData ?? []) as DailyTask[];

  // This week's sessions (for time totals and skill breakdown)
  const { data: sessions } = await supabase
    .from("learning_sessions")
    .select("skill_code, started_at, duration_seconds")
    .eq("user_id", user.id)
    .gte("started_at", `${weekStartISO}T00:00:00`)
    .lte("started_at", `${weekEndISO}T23:59:59`);

  const todaySeconds =
    (sessions ?? [])
      .filter((s) => s.started_at.startsWith(today))
      .reduce((a, s) => a + (s.duration_seconds ?? 0), 0);
  const todayMinutes = Math.round(todaySeconds / 60);

  const weeklySeconds = (sessions ?? []).reduce(
    (a, s) => a + (s.duration_seconds ?? 0),
    0,
  );
  const weeklyMinutes = Math.round(weeklySeconds / 60);

  const bySkillMinutes: Partial<Record<SkillCode, number>> = {};
  for (const s of SKILL_CODES) bySkillMinutes[s] = 0;
  for (const s of sessions ?? []) {
    const code = s.skill_code as SkillCode;
    bySkillMinutes[code] = (bySkillMinutes[code] ?? 0) + Math.round(s.duration_seconds / 60);
  }

  // Build per-day bar chart data (Mon..Sun)
  const days: { day: string; minutes: number }[] = [];
  for (let i = 0; i < 7; i += 1) {
    const d = startOfDay(addDays(start, i));
    const iso = formatISO(d, { representation: "date" });
    const totalSec = (sessions ?? [])
      .filter((s) => s.started_at.startsWith(iso))
      .reduce((a, s) => a + (s.duration_seconds ?? 0), 0);
    days.push({
      day: ["月", "火", "水", "木", "金", "土", "日"][i],
      minutes: Math.round(totalSec / 60),
    });
  }

  // Vocabulary reviews due today
  const { count: reviewCount } = await supabase
    .from("user_vocabulary_reviews")
    .select("id", { count: "exact", head: true })
    .eq("user_id", user.id)
    .lte("next_review_on", today);

  const streak = profile.streak_count ?? 0;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            こんにちは、{profile.display_name ?? "学習者"}さん
          </h1>
          <p className="text-sm text-slate-600">
            目標: TOEIC {profile.target_toeic ?? 900} ・ 1日 {profile.daily_minutes}分
          </p>
        </div>
        <GenerateTasksButton />
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatCard
          label="今日の学習"
          value={todayMinutes}
          unit="分"
          icon={<Timer className="h-5 w-5" />}
        />
        <StatCard
          label="連続日数"
          value={streak}
          unit="日"
          icon={<Flame className="h-5 w-5 text-orange-500" />}
        />
        <StatCard
          label="今週合計"
          value={weeklyMinutes}
          unit="分"
          icon={<CalendarCheck2 className="h-5 w-5" />}
        />
        <StatCard
          label="復習予定"
          value={reviewCount ?? 0}
          unit="件"
          icon={<Target className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <TodayTaskList tasks={tasks} />
          <WeeklyChart data={days} />
        </div>
        <div className="space-y-6">
          <SkillProgress bySkillMinutes={bySkillMinutes} weeklyTotal={weeklyMinutes} />
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-amber-500" />
                目標までの道のり
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">現在</span>
                <span className="font-medium">{profile.current_toeic ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">目標</span>
                <span className="font-medium">{profile.target_toeic ?? "-"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">期日</span>
                <span className="font-medium">{profile.target_date ?? "-"}</span>
              </div>
              <Button asChild variant="outline" size="sm" className="mt-3 w-full">
                <Link href="/onboarding">目標を編集</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
