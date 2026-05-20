import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

interface Props {
  label: string;
  value: React.ReactNode;
  unit?: string;
  hint?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatCard({ label, value, unit, hint, icon, className }: Props) {
  return (
    <Card className={cn("h-full", className)}>
      <CardContent className="flex h-full items-center gap-4 p-5">
        {icon && (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700">
            {icon}
          </div>
        )}
        <div className="flex-1">
          <div className="text-xs text-slate-500">{label}</div>
          <div className="mt-0.5 flex items-baseline gap-1">
            <span className="text-2xl font-semibold tracking-tight">{value}</span>
            {unit && <span className="text-xs text-slate-500">{unit}</span>}
          </div>
          {hint && <div className="mt-0.5 text-xs text-slate-500">{hint}</div>}
        </div>
      </CardContent>
    </Card>
  );
}
