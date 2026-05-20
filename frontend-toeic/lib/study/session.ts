import type { SupabaseClient } from "@supabase/supabase-js";
import type { SkillCode } from "@/lib/types/db";

export async function finishSession(
  supabase: SupabaseClient,
  params: {
    user_id: string;
    skill_code: SkillCode;
    started_at: Date;
    duration_seconds: number;
    item_count?: number;
    correct_count?: number;
    note?: string | null;
    difficulty_avg?: number;
  },
) {
  const accuracy =
    params.item_count && params.item_count > 0
      ? (params.correct_count ?? 0) / params.item_count
      : null;

  const { data: session, error: sessErr } = await supabase
    .from("learning_sessions")
    .insert({
      user_id: params.user_id,
      skill_code: params.skill_code,
      started_at: params.started_at.toISOString(),
      ended_at: new Date().toISOString(),
      duration_seconds: params.duration_seconds,
      item_count: params.item_count ?? 0,
      correct_count: params.correct_count ?? 0,
      accuracy,
      difficulty_avg: params.difficulty_avg ?? null,
      note: params.note ?? null,
    })
    .select()
    .single();
  if (sessErr) throw sessErr;

  // Try to mark today's daily_task for this skill as done.
  const today = new Date().toISOString().slice(0, 10);
  await supabase
    .from("daily_tasks")
    .update({ status: "done" })
    .eq("user_id", params.user_id)
    .eq("task_date", today)
    .eq("skill_code", params.skill_code);

  // Update streak (lightweight, client-side).
  const { data: profile } = await supabase
    .from("user_profiles")
    .select("last_studied_on, streak_count")
    .eq("id", params.user_id)
    .maybeSingle();
  if (profile) {
    const last = profile.last_studied_on as string | null;
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    let streak = profile.streak_count ?? 0;
    if (last === today) {
      // already counted
    } else if (last === yesterday) {
      streak = streak + 1;
    } else {
      streak = 1;
    }
    await supabase
      .from("user_profiles")
      .update({ last_studied_on: today, streak_count: streak })
      .eq("id", params.user_id);
  }

  return session;
}

export const isoNow = () => new Date();
