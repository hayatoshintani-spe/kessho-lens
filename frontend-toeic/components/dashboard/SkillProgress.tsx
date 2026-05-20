import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { SKILL_CODES, SKILL_LABEL, type SkillCode } from "@/lib/types/db";

interface Props {
  bySkillMinutes: Partial<Record<SkillCode, number>>;
  weeklyTotal: number;
}

export function SkillProgress({ bySkillMinutes, weeklyTotal }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>スキル別進捗（今週）</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {SKILL_CODES.map((s) => {
          const v = bySkillMinutes[s] ?? 0;
          const pct = weeklyTotal === 0 ? 0 : Math.round((v / weeklyTotal) * 100);
          return (
            <div key={s} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-700">{SKILL_LABEL[s]}</span>
                <span className="text-slate-500">
                  {v}分 ・ {pct}%
                </span>
              </div>
              <Progress value={pct} />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
