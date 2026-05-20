import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { QuizSession } from "@/components/study/QuizSession";
import type { QuizQuestion } from "@/lib/types/db";

export default async function ListeningPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data } = await supabase
    .from("quiz_questions")
    .select("*")
    .eq("skill_code", "listening")
    .order("difficulty", { ascending: true })
    .limit(10);

  const items: QuizQuestion[] = (data ?? []) as QuizQuestion[];

  return (
    <QuizSession
      items={items}
      skillCode="listening"
      title="リスニング"
      description="スクリプトはあとから確認できます。まずは耳で。"
      skillLabel="リスニング"
      skillBadgeClass="skill-listening"
    />
  );
}
