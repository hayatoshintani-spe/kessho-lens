import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { VocabularySession } from "./VocabularySession";
import type { VocabularyItem } from "@/lib/types/db";

export default async function VocabularyPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const today = new Date().toISOString().slice(0, 10);
  const { data: dueReviews } = await supabase
    .from("user_vocabulary_reviews")
    .select("vocabulary_item_id, next_review_on")
    .eq("user_id", user.id)
    .lte("next_review_on", today)
    .limit(20);

  const dueIds = (dueReviews ?? []).map((r) => r.vocabulary_item_id as string);

  const { data: dueItems } = dueIds.length
    ? await supabase.from("vocabulary_items").select("*").in("id", dueIds)
    : { data: [] as VocabularyItem[] };

  const { data: pool } = await supabase
    .from("vocabulary_items")
    .select("*")
    .order("difficulty", { ascending: true })
    .limit(30);

  const dueSet = new Set(dueIds);
  const newItems = (pool ?? []).filter((it) => !dueSet.has(it.id));

  const items: VocabularyItem[] = [
    ...((dueItems ?? []) as VocabularyItem[]),
    ...newItems.slice(0, 10),
  ];

  return <VocabularySession items={items} />;
}
