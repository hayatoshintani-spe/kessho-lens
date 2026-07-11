import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { HeatCell, HeatmapModel } from "@/lib/stats/heatmap";
import { cn } from "@/lib/utils/cn";

const LEVEL_CLASS: Record<HeatCell["level"], string> = {
  0: "bg-slate-100",
  1: "bg-blue-200",
  2: "bg-blue-300",
  3: "bg-blue-500",
  4: "bg-blue-700",
};

const DOW_LABELS = ["月", "", "水", "", "金", "", ""];

function cellTitle(cell: HeatCell): string {
  if (cell.inFuture || !cell.date) return "";
  if (cell.minutes <= 0) return `${cell.date}: 学習なし`;
  return `${cell.date}: ${cell.minutes}分`;
}

export function StudyHeatmap({ model }: { model: HeatmapModel }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>学習ヒートマップ</CardTitle>
        <span className="text-xs text-slate-500">
          直近 {model.weeks.length} 週 ・ {model.activeDays} 日学習
        </span>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="inline-flex min-w-full flex-col gap-1">
            {/* Month labels */}
            <div className="flex gap-1 pl-6 text-[10px] text-slate-400">
              {model.weeks.map((_, col) => {
                const label = model.monthLabels.find((m) => m.col === col);
                return (
                  <div key={col} className="w-3 shrink-0">
                    {label ? <span className="whitespace-nowrap">{label.label}</span> : null}
                  </div>
                );
              })}
            </div>

            {/* Grid: day-of-week label column + week columns */}
            <div className="flex gap-1">
              {/* DOW labels */}
              <div className="flex flex-col gap-1 pr-1 text-[9px] leading-3 text-slate-400">
                {DOW_LABELS.map((d, i) => (
                  <div key={i} className="flex h-3 w-4 items-center justify-end">
                    {d}
                  </div>
                ))}
              </div>

              {model.weeks.map((week, col) => (
                <div key={col} className="flex flex-col gap-1">
                  {week.map((cell, row) => (
                    <div
                      key={row}
                      title={cellTitle(cell)}
                      className={cn(
                        "h-3 w-3 rounded-[3px]",
                        cell.inFuture ? "bg-slate-50" : LEVEL_CLASS[cell.level],
                        !cell.inFuture && cell.level === 0 && "ring-1 ring-inset ring-slate-100",
                      )}
                    />
                  ))}
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="mt-1 flex items-center justify-end gap-1 pl-6 text-[10px] text-slate-400">
              <span>少</span>
              {([0, 1, 2, 3, 4] as const).map((lvl) => (
                <span key={lvl} className={cn("h-3 w-3 rounded-[3px]", LEVEL_CLASS[lvl])} />
              ))}
              <span>多</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
