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

const SKILLS = ["shadowing", "reading", "speaking", "listening"] as const;

export function AdminAddContent({ disabled }: { disabled?: boolean }) {
  const supabase = createSupabaseBrowserClient();
  const router = useRouter();
  const [skill, setSkill] = useState<(typeof SKILLS)[number]>("shadowing");
  const [title, setTitle] = useState("");
  const [bodyText, setBodyText] = useState("");
  const [tips, setTips] = useState("");
  const [difficulty, setDifficulty] = useState(3);
  const [estMinutes, setEstMinutes] = useState(5);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      let body: Record<string, unknown> = {};
      if (skill === "shadowing") body = { script: bodyText, tips: tips || null };
      else if (skill === "reading") {
        const wc = bodyText.trim().split(/\s+/).filter(Boolean).length;
        body = { passage: bodyText, word_count: wc };
      } else if (skill === "speaking") body = { prompt: bodyText, tips: tips || null };
      else if (skill === "listening") body = { script: bodyText };

      const { error } = await supabase.from("content_items").insert({
        skill_code: skill,
        title: title.trim(),
        body,
        difficulty,
        est_minutes: estMinutes,
        is_active: true,
      });
      if (error) throw error;
      setTitle(""); setBodyText(""); setTips(""); setDifficulty(3); setEstMinutes(5);
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
        <CardTitle className="text-base">教材を追加（シャドーイング / 英読 / スピーキング）</CardTitle>
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
              <Label>難易度 / 推定時間</Label>
              <div className="flex gap-2">
                <Input type="number" min={1} max={5} value={difficulty} onChange={(e) => setDifficulty(Number(e.target.value))} disabled={disabled} />
                <Input type="number" min={1} value={estMinutes} onChange={(e) => setEstMinutes(Number(e.target.value))} disabled={disabled} />
              </div>
            </div>
          </div>

          <div className="space-y-1">
            <Label>タイトル</Label>
            <Input required value={title} onChange={(e) => setTitle(e.target.value)} disabled={disabled} />
          </div>

          <div className="space-y-1">
            <Label>
              本文 ({skill === "speaking" ? "お題プロンプト" : skill === "reading" ? "英語パッセージ" : "スクリプト"})
            </Label>
            <Textarea
              required
              rows={6}
              value={bodyText}
              onChange={(e) => setBodyText(e.target.value)}
              disabled={disabled}
            />
          </div>

          {(skill === "shadowing" || skill === "speaking") && (
            <div className="space-y-1">
              <Label>Tips（任意）</Label>
              <Textarea value={tips} onChange={(e) => setTips(e.target.value)} disabled={disabled} />
            </div>
          )}

          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" disabled={saving || disabled}>
            {saving ? "保存中…" : "追加"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
