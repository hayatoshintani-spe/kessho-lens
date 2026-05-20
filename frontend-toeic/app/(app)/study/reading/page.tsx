import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { ReadingSession } from "./ReadingSession";
import type { ContentItem } from "@/lib/types/db";

export default async function ReadingPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data } = await supabase
    .from("content_items")
    .select("*")
    .eq("skill_code", "reading")
    .eq("is_active", true)
    .order("difficulty", { ascending: true })
    .limit(5);

  return <ReadingSession items={(data ?? []) as ContentItem[]} />;
}
