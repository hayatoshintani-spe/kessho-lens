"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

const SKILLS = ["grammar", "listening", "reading"] as const;

export function AdminAddGrammar({ disabled }: { disabled?: boolean }) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();
  const [skill, setSkill] = useState<(typeof SKILLS)[number]>("grammar");
  const [prompt, setPrompt] = useState("");
  const [choices, setChoices] = useState<string[]>(["", "", "", ""]);
  const [answerIndex, setAnswerIndex] = useState(0);
  const [explanation, setExplanation] = useState("");
  const [passage, setPassage] = useState("");
  const [difficulty, setDifficulty] = useState(3);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const cleaned = choices.map((c) => c.trim()).filter(Boolean);
      if (cleaned.length < 2) throw new Error("選択肢は2つ以上必要です");
      if (answerIndex >= cleaned.length) throw new Error("正解インデックスが選択肢を超えています");
      const { error } = await supabase.from("quiz_questions").insert({
        skill_code: skill,
        prompt: prompt.trim(),
        choices: cleaned,
        answer_index: answerIndex,
        explanation: explanation || null,
        passage: passage || null,
        difficulty,
      });
      if (error) throw error;
      setPrompt(""); setChoices(["", "", "", ""]); setAnswerIndex(0); setExplanation(""); setPassage("");
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
        <CardTitle className="text-base">選択問題を追加（文法 / リスニング / 英読）</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-3" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>スキル</Label>
              <Select value={skill} onValueChange={(v) => setSkill(v as any)} disabled={disabled}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SKILLS.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>難易度 (1-5)</Label>
              <Input type="number" min={1} max={5} value={difficulty} onChange={(e) => setDifficulty(Number(e.target.value))} disabled={disabled} />
            </div>
          </div>

          <div className="space-y-1">
            <Label>設問</Label>
            <Textarea required value={prompt} onChange={(e) => setPrompt(e.target.value)} disabled={disabled} />
          </div>

          <div className="space-y-2">
            <Label>選択肢（空欄は無視）</Label>
            {choices.map((c, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="answer"
                  checked={answerIndex === i}
                  onChange={() => setAnswerIndex(i)}
                  disabled={disabled}
                />
                <Input
                  value={c}
                  onChange={(e) =>
                    setChoices((prev) => prev.map((v, idx) => (idx === i ? e.target.value : v)))
                  }
                  placeholder={`選択肢 ${String.fromCharCode(65 + i)}`}
                  disabled={disabled}
                />
              </div>
            ))}
            <p className="text-xs text-slate-500">ラジオボタンで正解を選択。</p>
          </div>

          <div className="space-y-1">
            <Label>解説</Label>
            <Textarea value={explanation} onChange={(e) => setExplanation(e.target.value)} disabled={disabled} />
          </div>

          <div className="space-y-1">
            <Label>パッセージ（リスニングのスクリプト / 英読の本文）</Label>
            <Textarea value={passage} onChange={(e) => setPassage(e.target.value)} disabled={disabled} />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={saving || disabled}>
            {saving ? "保存中…" : "追加"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
