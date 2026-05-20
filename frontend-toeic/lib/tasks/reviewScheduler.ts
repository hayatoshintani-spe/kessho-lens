import { addDays, formatISO, startOfDay } from "date-fns";

export type ReviewRating = "known" | "forgot" | "hard";

export interface ReviewState {
  repetition: number;
  interval_days: number;
  ease: number;
}

/**
 * SM-2 light. Returns the next interval/ease and a next-review-on date string.
 */
export function nextReview(prev: ReviewState, rating: ReviewRating) {
  let { repetition, ease } = prev;
  let interval: number;

  if (rating === "forgot") {
    repetition = 0;
    interval = 1;
    ease = Math.max(1.3, ease - 0.2);
  } else {
    if (repetition === 0) interval = 1;
    else if (repetition === 1) interval = 3;
    else interval = Math.round(prev.interval_days * ease);

    repetition += 1;
    if (rating === "hard") {
      interval = Math.max(1, Math.round(interval * 0.7));
      ease = Math.max(1.3, ease - 0.15);
    } else {
      ease = Math.min(2.8, ease + 0.05);
    }
  }

  const next = addDays(startOfDay(new Date()), interval);
  return {
    repetition,
    ease,
    interval_days: interval,
    next_review_on: formatISO(next, { representation: "date" }),
  };
}
