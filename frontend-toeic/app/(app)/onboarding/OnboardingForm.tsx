"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2 } from "lucide-react";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { SKILL_CODES, SKILL_LABEL, type SkillCode } from "@/lib/types/db";
import { planDailyTasks } from "@/lib/tasks/generateDailyTasks";

interface Initial {
  display_name: string;
  current_toeic: number;
  target_toeic: number;
  target_date: string;
  daily_minutes: number;
  weak_areas: SkillCode[];
}

export function OnboardingForm({ initial }: { initial: Initial }) {
  const router = useRouter();
  const supabase = createSupabaseBrowserClient();

  const [displayName, setDisplayName] = useState(initial.display_name);
  const [currentToeic, setCurrentToeic] = useState(initial.current_toeic);
  const [targetToeic, setTargetToeic] = useState(initial.target_toeic);
  const [targetDate, setTargetDate] = useState(initial.target_date);
  const [dailyMinutes, setDailyMinutes] = useState(initial.daily_minutes);
  const [weakAreas, setWeakAreas] = useState<SkillCode[]>(initial.weak_areas);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const plan = planDailyTasks(dailyMinutes, weakAreas);

  function toggleWeak(s: SkillCode) {
    setWeakAreas((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s],
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const { data: userData } = await supabase.auth.getUser();
      const user = userData.user;
      if (!user) throw new Error("ユーザーが見つかりません");

      const { error } = await supabase
        .from("user_profiles")
        .upsert({
          id: user.id,
          display_name: displayName || null,
          current_toeic: currentToeic,
          target_toeic: targetToeic,
          target_date: targetDate || null,
          daily_minutes: dailyMinutes,
          weak_areas: weakAreas,
          onboarded_at: new Date().toISOString(),
        })
        .select()
        .single();
      if (error) throw error;

      router.replace("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存に失敗しました");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>あなたについて</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="display_name">表示名</Label>
            <Input
              id="display_name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="例: Hayato"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="current">現在のTOEICスコア</Label>
              <Input
                id="current"
                type="number"
                min={0}
                max={990}
                value={currentToeic}
                onChange={(e) => setCurrentToeic(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="target">目標スコア</Label>
              <Input
                id="target"
                type="number"
                min={0}
                max={990}
                value={targetToeic}
                onChange={(e) => setTargetToeic(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="date">目標達成日</Label>
            <Input
              id="date"
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>1日の学習可能時間</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">合計</span>
            <span className="text-xl font-semibold">{dailyMinutes}分</span>
          </div>
          <Slider
            value={[dailyMinutes]}
            min={15}
            max={240}
            step={5}
            onValueChange={(v) => setDailyMinutes(v[0])}
          />
          <div className="grid grid-cols-2 gap-2 pt-2 sm:grid-cols-3">
            {plan.map((p) => (
              <div
                key={p.skill_code}
                className="rounded-md border bg-white px-3 py-2 text-sm"
              >
                <div className="text-slate-500">{SKILL_LABEL[p.skill_code]}</div>
                <div className="font-medium">{p.target_minutes}分</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>苦手分野（複数選択可）</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {SKILL_CODES.map((s) => (
              <Checkbox
                key={s}
                checked={weakAreas.includes(s)}
                onChange={() => toggleWeak(s)}
                label={SKILL_LABEL[s]}
              />
            ))}
          </div>
          <p className="mt-2 text-xs text-slate-500">
            選んだスキルは1日の配分が +5% され、他から自動で按分されます。
          </p>
        </CardContent>
      </Card>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex justify-end">
        <Button type="submit" disabled={saving} size="lg">
          {saving && <Loader2 className="h-4 w-4 animate-spin" />}
          設定を保存して開始
        </Button>
      </div>
    </form>
  );
}
