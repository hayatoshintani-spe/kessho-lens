export const pct = (n: number, digits = 0) => `${(n * 100).toFixed(digits)}%`;

export const minutesToHm = (mins: number) => {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h === 0) return `${m}分`;
  if (m === 0) return `${h}時間`;
  return `${h}時間${m}分`;
};

export const safeWpm = (words: number, seconds: number) =>
  seconds <= 0 ? 0 : Math.round((words / seconds) * 60);
