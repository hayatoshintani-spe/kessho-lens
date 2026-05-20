import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { OnboardingForm } from "./OnboardingForm";

export default async function OnboardingPage() {
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

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">はじめての設定</h1>
        <p className="text-sm text-slate-600">
          目標と1日の学習可能時間を教えてください。これに合わせて毎日のタスクを生成します。
        </p>
      </div>
      <OnboardingForm
        initial={{
          display_name: profile?.display_name ?? "",
          current_toeic: profile?.current_toeic ?? 500,
          target_toeic: profile?.target_toeic ?? 900,
          target_date: profile?.target_date ?? "",
          daily_minutes: profile?.daily_minutes ?? 60,
          weak_areas: profile?.weak_areas ?? [],
        }}
      />
    </div>
  );
}
