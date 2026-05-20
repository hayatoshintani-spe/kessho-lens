"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export function AdminAddVocabulary({ disabled }: { disabled?: boolean }) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();
  const [word, setWord] = useState("");
  const [meaning, setMeaning] = useState("");
  const [pos, setPos] = useState("");
  const [example, setExample] = useState("");
  const [exampleJa, setExampleJa] = useState("");
  const [difficulty, setDifficulty] = useState(3);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const { error } = await supabase.from("vocabulary_items").insert({
        word: word.trim(),
        meaning: meaning.trim(),
        part_of_speech: pos || null,
        example_en: example || null,
        example_ja: exampleJa || null,
        difficulty,
      });
      if (error) throw error;
      setWord(""); setMeaning(""); setPos(""); setExample(""); setExampleJa(""); setDifficulty(3);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存に失敗しました");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">単語を追加</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="grid grid-cols-1 gap-3 md:grid-cols-2" onSubmit={handleSubmit}>
          <div className="space-y-1">
            <Label htmlFor="v_word">単語</Label>
            <Input id="v_word" required value={word} onChange={(e) => setWord(e.target.value)} disabled={disabled} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="v_meaning">意味</Label>
            <Input id="v_meaning" required value={meaning} onChange={(e) => setMeaning(e.target.value)} disabled={disabled} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="v_pos">品詞</Label>
            <Input id="v_pos" value={pos} onChange={(e) => setPos(e.target.value)} disabled={disabled} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="v_diff">難易度 (1-5)</Label>
            <Input id="v_diff" type="number" min={1} max={5} value={difficulty} onChange={(e) => setDifficulty(Number(e.target.value))} disabled={disabled} />
          </div>
          <div className="space-y-1 md:col-span-2">
            <Label htmlFor="v_ex">例文 (英)</Label>
            <Textarea id="v_ex" value={example} onChange={(e) => setExample(e.target.value)} disabled={disabled} />
          </div>
          <div className="space-y-1 md:col-span-2">
            <Label htmlFor="v_exj">例文 (日)</Label>
            <Textarea id="v_exj" value={exampleJa} onChange={(e) => setExampleJa(e.target.value)} disabled={disabled} />
          </div>
          {error && <p className="text-sm text-red-600 md:col-span-2">{error}</p>}
          <div className="md:col-span-2">
            <Button type="submit" disabled={saving || disabled}>
              {saving ? "保存中…" : "追加"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
