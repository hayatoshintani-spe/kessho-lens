import { addDays, format, startOfWeek } from "date-fns";

export interface HeatCell {
  /** ISO date (yyyy-MM-dd). Empty string for padding cells before the range. */
  date: string;
  minutes: number;
  /** Intensity bucket 0..4 (0 = no study). */
  level: 0 | 1 | 2 | 3 | 4;
  /** True for days after `today` (rendered faint / non-interactive). */
  inFuture: boolean;
}

export interface HeatmapModel {
  /** Column-major: weeks[col][row], row 0 = Monday .. row 6 = Sunday. */
  weeks: HeatCell[][];
  /** Month labels aligned to the first column of each month. */
  monthLabels: { col: number; label: string }[];
  totalMinutes: number;
  activeDays: number;
}

/** Minutes → intensity bucket. */
export function levelFor(minutes: number): 0 | 1 | 2 | 3 | 4 {
  if (minutes <= 0) return 0;
  if (minutes < 15) return 1;
  if (minutes < 30) return 2;
  if (minutes < 60) return 3;
  return 4;
}

/**
 * Build a GitHub-style contribution grid ending on the week that contains
 * `today`. Weeks start on Monday.
 *
 * @param minutesByDate map of yyyy-MM-dd → studied minutes
 * @param today         reference date (defaults to now; injectable for tests)
 * @param weeks         number of week columns to render
 */
export function buildHeatmap(
  minutesByDate: Record<string, number>,
  today: Date,
  weeks = 17,
): HeatmapModel {
  const thisWeekStart = startOfWeek(today, { weekStartsOn: 1 });
  const firstColStart = addDays(thisWeekStart, -(weeks - 1) * 7);

  const grid: HeatCell[][] = [];
  const monthLabels: { col: number; label: string }[] = [];
  let lastMonth = -1;
  let totalMinutes = 0;
  let activeDays = 0;

  for (let col = 0; col < weeks; col += 1) {
    const week: HeatCell[] = [];
    for (let row = 0; row < 7; row += 1) {
      const d = addDays(firstColStart, col * 7 + row);
      const iso = format(d, "yyyy-MM-dd");
      const inFuture = d.getTime() > today.getTime();
      const minutes = inFuture ? 0 : minutesByDate[iso] ?? 0;
      if (!inFuture && minutes > 0) {
        totalMinutes += minutes;
        activeDays += 1;
      }
      week.push({
        date: iso,
        minutes,
        level: levelFor(minutes),
        inFuture,
      });

      // Record a month label at the top cell (row 0) when the month rolls over.
      if (row === 0) {
        const m = d.getMonth();
        if (m !== lastMonth) {
          monthLabels.push({ col, label: format(d, "M月") });
          lastMonth = m;
        }
      }
    }
    grid.push(week);
  }

  return { weeks: grid, monthLabels, totalMinutes, activeDays };
}
