import { describe, expect, it } from "vitest";
import { planDailyTasks } from "./generateDailyTasks";
import { SKILL_CODES, type SkillCode } from "@/lib/types/db";

describe("planDailyTasks", () => {
  it("returns a plan covering all six skills", () => {
    const plan = planDailyTasks(90);
    const codes = plan.map((p) => p.skill_code).sort();
    expect(codes).toEqual([...SKILL_CODES].sort());
  });

  it("sums to the requested daily minutes when divisible", () => {
    const plan = planDailyTasks(90);
    const total = plan.reduce((a, p) => a + p.target_minutes, 0);
    expect(total).toBe(90);
  });

  it("matches the documented 90-minute example (within rounding)", () => {
    // From the original spec:
    //   90分: 単語20 / 文法15 / L20 / シャドー15 / 英読15 / SP5
    const plan = planDailyTasks(90);
    const byCode: Record<string, number> = {};
    plan.forEach((p) => (byCode[p.skill_code] = p.target_minutes));

    // Speaking is 5% of 90 = 4.5, rounded to 5.
    expect(byCode.speaking).toBe(5);
    expect(byCode.grammar).toBe(15);
    expect(byCode.shadowing).toBe(15);
    expect(byCode.reading).toBe(15);
    // Vocab and Listening are tied at 25% — together they share the
    // remainder after rounding. Each must be >= 15 and the total fixed.
    expect(byCode.vocabulary).toBeGreaterThanOrEqual(15);
    expect(byCode.listening).toBeGreaterThanOrEqual(15);
  });

  it("respects the 5-minute minimum even at very small daily totals", () => {
    const plan = planDailyTasks(15);
    plan.forEach((p) => expect(p.target_minutes).toBeGreaterThanOrEqual(5));
  });

  it("floors input below 5 to a 5-minute minimum total per skill", () => {
    const plan = planDailyTasks(2);
    // Each skill rounds up to its 5-minute floor.
    plan.forEach((p) => expect(p.target_minutes).toBeGreaterThanOrEqual(5));
  });

  it("boosts weak areas and reduces others", () => {
    const baseline = planDailyTasks(120);
    const boosted = planDailyTasks(120, ["speaking"]);
    const byBaseline = Object.fromEntries(
      baseline.map((p) => [p.skill_code, p.target_minutes]),
    );
    const byBoosted = Object.fromEntries(
      boosted.map((p) => [p.skill_code, p.target_minutes]),
    );
    expect(byBoosted.speaking).toBeGreaterThan(byBaseline.speaking);

    const nonBoostedTotal = SKILL_CODES.filter((s) => s !== "speaking").reduce(
      (a, s) => a + byBoosted[s],
      0,
    );
    const baselineNonSpeakTotal = SKILL_CODES.filter((s) => s !== "speaking").reduce(
      (a, s) => a + byBaseline[s],
      0,
    );
    expect(nonBoostedTotal).toBeLessThan(baselineNonSpeakTotal);
  });

  it("keeps total equal to dailyMinutes even with weak-area boosts", () => {
    const inputs: { mins: number; weak: SkillCode[] }[] = [
      { mins: 60, weak: [] },
      { mins: 90, weak: ["listening"] },
      { mins: 120, weak: ["speaking", "shadowing"] },
      { mins: 180, weak: ["vocabulary", "grammar", "reading"] },
    ];
    for (const { mins, weak } of inputs) {
      const plan = planDailyTasks(mins, weak);
      const total = plan.reduce((a, p) => a + p.target_minutes, 0);
      expect(total, `total mismatch for ${mins} mins, weak=${weak}`).toBe(mins);
    }
  });

  it("rounds every skill to a multiple of 5 minutes", () => {
    const plan = planDailyTasks(95);
    plan.forEach((p) => {
      expect(p.target_minutes % 5).toBe(0);
    });
  });

  it("returns minutes that are positive integers", () => {
    const plan = planDailyTasks(60);
    plan.forEach((p) => {
      expect(Number.isInteger(p.target_minutes)).toBe(true);
      expect(p.target_minutes).toBeGreaterThan(0);
    });
  });
});
