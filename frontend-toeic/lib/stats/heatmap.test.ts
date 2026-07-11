import { describe, expect, it } from "vitest";
import { buildHeatmap, levelFor } from "./heatmap";

describe("levelFor", () => {
  it("returns 0 for no study", () => {
    expect(levelFor(0)).toBe(0);
    expect(levelFor(-5)).toBe(0);
  });

  it("buckets minutes into 1..4", () => {
    expect(levelFor(1)).toBe(1);
    expect(levelFor(14)).toBe(1);
    expect(levelFor(15)).toBe(2);
    expect(levelFor(29)).toBe(2);
    expect(levelFor(30)).toBe(3);
    expect(levelFor(59)).toBe(3);
    expect(levelFor(60)).toBe(4);
    expect(levelFor(200)).toBe(4);
  });
});

describe("buildHeatmap", () => {
  // Wednesday 2026-06-10.
  const today = new Date("2026-06-10T12:00:00Z");

  it("produces the requested number of week columns", () => {
    const model = buildHeatmap({}, today, 17);
    expect(model.weeks).toHaveLength(17);
    model.weeks.forEach((w) => expect(w).toHaveLength(7));
  });

  it("places today in the last column", () => {
    const model = buildHeatmap({ "2026-06-10": 30 }, today, 4);
    const lastCol = model.weeks[model.weeks.length - 1];
    const todayCell = lastCol.find((c) => c.date === "2026-06-10");
    expect(todayCell).toBeDefined();
    expect(todayCell?.minutes).toBe(30);
    expect(todayCell?.level).toBe(3);
  });

  it("marks days after today as future", () => {
    const model = buildHeatmap({}, today, 4);
    const lastCol = model.weeks[model.weeks.length - 1];
    // Wed is row 2 (Mon=0). Thu..Sun are future.
    const future = lastCol.filter((c) => c.inFuture);
    expect(future.length).toBe(4); // Thu, Fri, Sat, Sun
    future.forEach((c) => expect(c.minutes).toBe(0));
  });

  it("ignores minutes recorded on future dates", () => {
    // 2026-06-14 (Sun) is in the future relative to Wed the 10th.
    const model = buildHeatmap({ "2026-06-14": 99 }, today, 4);
    const cell = model.weeks
      .flat()
      .find((c) => c.date === "2026-06-14");
    expect(cell?.inFuture).toBe(true);
    expect(cell?.minutes).toBe(0);
  });

  it("aggregates totals and active-day counts over past cells only", () => {
    const model = buildHeatmap(
      { "2026-06-08": 20, "2026-06-09": 40, "2026-06-10": 5, "2026-06-14": 99 },
      today,
      4,
    );
    expect(model.totalMinutes).toBe(65); // 20 + 40 + 5, future 99 excluded
    expect(model.activeDays).toBe(3);
  });

  it("weeks start on Monday", () => {
    const model = buildHeatmap({}, today, 2);
    // First cell of any column is a Monday.
    const firstCellDate = new Date(`${model.weeks[0][0].date}T00:00:00Z`);
    expect(firstCellDate.getUTCDay()).toBe(1); // Monday
  });

  it("emits at least one month label", () => {
    const model = buildHeatmap({}, today, 17);
    expect(model.monthLabels.length).toBeGreaterThan(0);
    model.monthLabels.forEach((l) => {
      expect(l.label).toMatch(/^\d{1,2}月$/);
      expect(l.col).toBeGreaterThanOrEqual(0);
    });
  });
});
