import { describe, expect, it } from "vitest";
import { nextReview } from "./reviewScheduler";

const FRESH = { repetition: 0, interval_days: 0, ease: 2.5 };

describe("nextReview", () => {
  it("resets repetition and pushes a 1-day interval on 'forgot'", () => {
    const next = nextReview({ repetition: 4, interval_days: 14, ease: 2.6 }, "forgot");
    expect(next.repetition).toBe(0);
    expect(next.interval_days).toBe(1);
    expect(next.ease).toBeLessThan(2.6); // ease decreases
    expect(next.ease).toBeGreaterThanOrEqual(1.3); // ease floored
  });

  it("advances to a 1-day interval on first 'known'", () => {
    const next = nextReview(FRESH, "known");
    expect(next.repetition).toBe(1);
    expect(next.interval_days).toBe(1);
    expect(next.ease).toBeGreaterThanOrEqual(2.5);
  });

  it("advances to a 3-day interval on second 'known'", () => {
    const after1 = nextReview(FRESH, "known");
    const after2 = nextReview(after1, "known");
    expect(after2.repetition).toBe(2);
    expect(after2.interval_days).toBe(3);
  });

  it("uses ease-multiplied interval from the third 'known' onward", () => {
    let s = FRESH;
    s = nextReview(s, "known"); // -> interval 1
    s = nextReview(s, "known"); // -> interval 3
    const before = s;
    s = nextReview(s, "known"); // -> round(3 * ease)
    expect(s.interval_days).toBe(Math.round(before.interval_days * before.ease));
    expect(s.repetition).toBe(3);
  });

  it("shortens interval and reduces ease on 'hard'", () => {
    const easy = nextReview(FRESH, "known");
    const easy2 = nextReview(easy, "known"); // interval 3
    const hard = nextReview(easy2, "hard");
    // Hard multiplies projected interval by 0.7.
    expect(hard.interval_days).toBeLessThan(easy2.interval_days * easy.ease);
    expect(hard.ease).toBeLessThan(easy2.ease);
    expect(hard.ease).toBeGreaterThanOrEqual(1.3);
  });

  it("caps ease at 2.8 even after many 'known' ratings", () => {
    let s = FRESH;
    // Clamp interval after each step so addDays() does not overflow Date range.
    for (let i = 0; i < 20; i += 1) {
      s = nextReview(s, "known");
      s = { ...s, interval_days: Math.min(s.interval_days, 30) };
    }
    expect(s.ease).toBeLessThanOrEqual(2.8);
  });

  it("returns an ISO YYYY-MM-DD next_review_on", () => {
    const next = nextReview(FRESH, "known");
    expect(next.next_review_on).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it("never returns interval_days < 1", () => {
    let s = { repetition: 10, interval_days: 1, ease: 1.3 };
    s = nextReview(s, "hard");
    expect(s.interval_days).toBeGreaterThanOrEqual(1);
  });
});
