import { SKILL_CODES, SKILL_RATIO, type SkillCode } from "@/lib/types/db";

export interface TaskPlanItem {
  skill_code: SkillCode;
  target_minutes: number;
}

/**
 * Allocate `dailyMinutes` across the six skills using the default ratios,
 * boosting weak areas. Rounds to the nearest 5 minutes with a 5-minute floor.
 */
export function planDailyTasks(
  dailyMinutes: number,
  weakAreas: SkillCode[] = [],
): TaskPlanItem[] {
  if (dailyMinutes < 5) dailyMinutes = 5;

  const boost = 0.05;
  const ratios: Record<SkillCode, number> = { ...SKILL_RATIO };

  if (weakAreas.length > 0) {
    const totalBoost = boost * weakAreas.length;
    weakAreas.forEach((s) => {
      ratios[s] = ratios[s] + boost;
    });
    const others = SKILL_CODES.filter((s) => !weakAreas.includes(s));
    const othersTotal = others.reduce((acc, s) => acc + ratios[s], 0);
    others.forEach((s) => {
      ratios[s] = ratios[s] - (ratios[s] / othersTotal) * totalBoost;
    });
  }

  // Raw minutes per skill.
  const raw = SKILL_CODES.map((s) => ({
    skill_code: s,
    minutes: dailyMinutes * ratios[s],
  }));

  // Round each to nearest 5; enforce min 5.
  const rounded = raw.map((r) => ({
    skill_code: r.skill_code,
    target_minutes: Math.max(5, Math.round(r.minutes / 5) * 5),
  }));

  // Adjust the largest bucket so the total matches dailyMinutes.
  const total = rounded.reduce((acc, r) => acc + r.target_minutes, 0);
  const delta = dailyMinutes - total;
  if (delta !== 0) {
    const largest = rounded.reduce((a, b) =>
      a.target_minutes > b.target_minutes ? a : b,
    );
    largest.target_minutes = Math.max(5, largest.target_minutes + delta);
  }

  return rounded;
}
