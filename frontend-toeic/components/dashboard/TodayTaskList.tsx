import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, PlayCircle } from "lucide-react";
import { SKILL_LABEL, SKILL_ROUTE, type DailyTask } from "@/lib/types/db";

interface Props {
  tasks: DailyTask[];
}

export function TodayTaskList({ tasks }: Props) {
  if (tasks.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>今日のタスク</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-600">
            まだ今日のタスクがありません。ダッシュボードの「今日のタスクを生成」を押してください。
          </p>
        </CardContent>
      </Card>
    );
  }

  const total = tasks.reduce((a, t) => a + t.target_minutes, 0);
  const doneMinutes = tasks
    .filter((t) => t.status === "done")
    .reduce((a, t) => a + t.target_minutes, 0);
  const progress = total === 0 ? 0 : Math.round((doneMinutes / total) * 100);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>今日のタスク</CardTitle>
        <Badge variant="secondary">
          {doneMinutes}/{total}分
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={progress} />
        <ul className="space-y-2">
          {tasks.map((t) => {
            const done = t.status === "done";
            return (
              <li
                key={t.id}
                className="flex items-center justify-between rounded-lg border bg-white p-3"
              >
                <div className="flex items-center gap-3">
                  {done ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                  ) : (
                    <Circle className="h-5 w-5 text-slate-300" />
                  )}
                  <div>
                    <div className="text-sm font-medium">
                      {SKILL_LABEL[t.skill_code]}
                    </div>
                    <div className="text-xs text-slate-500">
                      目安 {t.target_minutes} 分
                    </div>
                  </div>
                </div>
                <Button asChild size="sm" variant={done ? "outline" : "default"}>
                  <Link href={SKILL_ROUTE[t.skill_code]}>
                    <PlayCircle className="h-4 w-4" />
                    {done ? "もう一度" : "開始"}
                  </Link>
                </Button>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
