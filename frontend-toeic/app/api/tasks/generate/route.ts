import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { planDailyTasks } from "@/lib/tasks/generateDailyTasks";
import { todayISO } from "@/lib/utils/date";
import type { SkillCode } from "@/lib/types/db";

export async function POST() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "未認証" }, { status: 401 });

  const { data: profile, error: profileErr } = await supabase
    .from("user_profiles")
    .select("daily_minutes, weak_areas")
    .eq("id", user.id)
    .maybeSingle();
  if (profileErr) return NextResponse.json({ error: profileErr.message }, { status: 500 });

  const dailyMinutes = profile?.daily_minutes ?? 60;
  const weak = (profile?.weak_areas ?? []) as SkillCode[];

  const today = todayISO();
  const plan = planDailyTasks(dailyMinutes, weak);

  const rows = plan.map((p) => ({
    user_id: user.id,
    task_date: today,
    skill_code: p.skill_code,
    target_minutes: p.target_minutes,
    status: "pending",
  }));

  const { error } = await supabase
    .from("daily_tasks")
    .upsert(rows, { onConflict: "user_id,task_date,skill_code" });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, count: rows.length });
}
