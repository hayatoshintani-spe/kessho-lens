import {
  addDays,
  differenceInCalendarDays,
  endOfWeek,
  format,
  formatISO,
  startOfDay,
  startOfWeek,
} from "date-fns";

export const todayISO = () =>
  format(startOfDay(new Date()), "yyyy-MM-dd");

export const formatDate = (d: Date | string, fmt = "yyyy/MM/dd") =>
  format(typeof d === "string" ? new Date(d) : d, fmt);

export const formatTime = (d: Date | string, fmt = "HH:mm") =>
  format(typeof d === "string" ? new Date(d) : d, fmt);

export const formatMinutes = (totalSeconds: number) => {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  if (m === 0) return `${s}s`;
  if (s === 0) return `${m}m`;
  return `${m}m ${s}s`;
};

export const weekRange = (d = new Date()) => ({
  start: startOfWeek(d, { weekStartsOn: 1 }),
  end: endOfWeek(d, { weekStartsOn: 1 }),
});

export const daysBetween = (a: Date | string, b: Date | string) =>
  differenceInCalendarDays(
    typeof a === "string" ? new Date(a) : a,
    typeof b === "string" ? new Date(b) : b,
  );

export { addDays, formatISO, startOfDay };
