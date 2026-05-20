import { redirect } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { AdminAddVocabulary } from "./AdminAddVocabulary";
import { AdminAddGrammar } from "./AdminAddGrammar";
import { AdminAddContent } from "./AdminAddContent";

export default async function AdminPage() {
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: profile } = await supabase
    .from("user_profiles")
    .select("role")
    .eq("id", user.id)
    .maybeSingle();

  const isAdmin = profile?.role === "admin";

  const [vocab, quizzes, contents] = await Promise.all([
    supabase.from("vocabulary_items").select("*").order("created_at", { ascending: false }).limit(50),
    supabase.from("quiz_questions").select("*").order("created_at", { ascending: false }).limit(50),
    supabase.from("content_items").select("*").order("created_at", { ascending: false }).limit(50),
  ]);

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">教材管理</h1>
        <p className="text-sm text-slate-600">
          単語・文法/リスニング/英読の選択問題・シャドーイング/スピーキング/英読の教材を追加します。
        </p>
        {!isAdmin && (
          <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
            あなたのアカウントには <code className="rounded bg-amber-100 px-1">role = admin</code> が設定されていません。
            閲覧のみ可能です。Supabase ダッシュボードから <code>user_profiles.role</code> を <code>admin</code> に更新してください。
          </div>
        )}
      </div>

      <Tabs defaultValue="vocab">
        <TabsList>
          <TabsTrigger value="vocab">単語</TabsTrigger>
          <TabsTrigger value="quiz">選択問題</TabsTrigger>
          <TabsTrigger value="content">シャドーイング/英読/SP</TabsTrigger>
        </TabsList>

        <TabsContent value="vocab" className="space-y-4">
          <AdminAddVocabulary disabled={!isAdmin} />
          <Card>
            <CardHeader>
              <CardTitle className="text-base">単語一覧（最新50件）</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="divide-y text-sm">
                {(vocab.data ?? []).map((v: any) => (
                  <li key={v.id} className="flex items-center justify-between py-2">
                    <div>
                      <span className="font-medium">{v.word}</span>
                      <span className="ml-2 text-slate-500">— {v.meaning}</span>
                    </div>
                    <Badge variant="outline">難 {v.difficulty}</Badge>
                  </li>
                ))}
                {(vocab.data ?? []).length === 0 && (
                  <li className="py-4 text-slate-500">まだ単語がありません。</li>
                )}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quiz" className="space-y-4">
          <AdminAddGrammar disabled={!isAdmin} />
          <Card>
            <CardHeader>
              <CardTitle className="text-base">問題一覧（最新50件）</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="divide-y text-sm">
                {(quizzes.data ?? []).map((q: any) => (
                  <li key={q.id} className="py-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">{q.skill_code}</Badge>
                      <Badge variant="outline">難 {q.difficulty}</Badge>
                    </div>
                    <div className="mt-1">{q.prompt}</div>
                  </li>
                ))}
                {(quizzes.data ?? []).length === 0 && (
                  <li className="py-4 text-slate-500">まだ問題がありません。</li>
                )}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="content" className="space-y-4">
          <AdminAddContent disabled={!isAdmin} />
          <Card>
            <CardHeader>
              <CardTitle className="text-base">教材一覧（最新50件）</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="divide-y text-sm">
                {(contents.data ?? []).map((c: any) => (
                  <li key={c.id} className="py-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline">{c.skill_code}</Badge>
                      <Badge variant="outline">難 {c.difficulty}</Badge>
                    </div>
                    <div className="mt-1 font-medium">{c.title}</div>
                  </li>
                ))}
                {(contents.data ?? []).length === 0 && (
                  <li className="py-4 text-slate-500">まだ教材がありません。</li>
                )}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
