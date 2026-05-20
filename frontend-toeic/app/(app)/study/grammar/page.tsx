import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { QuizSession } from "../../../../components/study/QuizSession";
import type { QuizQuestion } from "@/lib/types/db";

export default async function GrammarPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data } = await supabase
    .from("quiz_questions")
    .select("*")
    .eq("skill_code", "grammar")
    .order("difficulty", { ascending: true })
    .limit(10);

  const items: QuizQuestion[] = (data ?? []) as QuizQuestion[];

  return (
    <QuizSession
      items={items}
      skillCode="grammar"
      title="文法"
      description="4択で素早く回答 → 解説で復習。"
      skillLabel="文法"
      skillBadgeClass="skill-grammar"
    />
  );
}
