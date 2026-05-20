import { describe, expect, it } from "vitest";
import { minutesToHm, pct, safeWpm } from "./format";

describe("pct", () => {
  it("formats a fraction as a percent string", () => {
    expect(pct(0.5)).toBe("50%");
    expect(pct(1)).toBe("100%");
    expect(pct(0)).toBe("0%");
  });

  it("honors the requested digit count", () => {
    expect(pct(0.1234, 1)).toBe("12.3%");
    expect(pct(0.6666, 2)).toBe("66.66%");
  });
});

describe("minutesToHm", () => {
  it("returns minutes only when under an hour", () => {
    expect(minutesToHm(0)).toBe("0分");
    expect(minutesToHm(45)).toBe("45分");
  });

  it("returns hour-only when minutes are zero", () => {
    expect(minutesToHm(60)).toBe("1時間");
    expect(minutesToHm(180)).toBe("3時間");
  });

  it("returns combined h/m otherwise", () => {
    expect(minutesToHm(90)).toBe("1時間30分");
    expect(minutesToHm(125)).toBe("2時間5分");
  });
});

describe("safeWpm", () => {
  it("returns 0 when seconds is zero or negative", () => {
    expect(safeWpm(100, 0)).toBe(0);
    expect(safeWpm(100, -1)).toBe(0);
  });

  it("computes words per minute", () => {
    // 100 words in 60s = 100 WPM
    expect(safeWpm(100, 60)).toBe(100);
    // 50 words in 30s = 100 WPM
    expect(safeWpm(50, 30)).toBe(100);
    // 80 words in 60s = 80 WPM
    expect(safeWpm(80, 60)).toBe(80);
  });

  it("rounds to an integer", () => {
    expect(Number.isInteger(safeWpm(33, 60))).toBe(true);
  });
});
