// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StudyHeatmap } from "./StudyHeatmap";
import { buildHeatmap } from "@/lib/stats/heatmap";

describe("StudyHeatmap", () => {
  const today = new Date("2026-06-10T12:00:00Z");

  it("renders the week count and active-day summary", () => {
    const model = buildHeatmap(
      { "2026-06-08": 20, "2026-06-09": 40 },
      today,
      6,
    );
    render(<StudyHeatmap model={model} />);
    expect(screen.getByText("学習ヒートマップ")).toBeInTheDocument();
    expect(screen.getByText(/直近 6 週/)).toBeInTheDocument();
    expect(screen.getByText(/2 日学習/)).toBeInTheDocument();
  });

  it("renders 7 cells per week column (weeks*7 + 5 legend swatches)", () => {
    const model = buildHeatmap({}, today, 4);
    const { container } = render(<StudyHeatmap model={model} />);
    // Cells and legend swatches share the rounded square shape class.
    const squares = container.querySelectorAll(".rounded-\\[3px\\]");
    // 4 weeks * 7 days = 28 grid cells + 5 legend swatches = 33
    expect(squares.length).toBe(28 + 5);
  });

  it("gives studied days a descriptive tooltip", () => {
    const model = buildHeatmap({ "2026-06-09": 40 }, today, 4);
    render(<StudyHeatmap model={model} />);
    expect(screen.getByTitle("2026-06-09: 40分")).toBeInTheDocument();
  });

  it("renders a legend with 少 and 多 markers", () => {
    const model = buildHeatmap({}, today, 4);
    render(<StudyHeatmap model={model} />);
    expect(screen.getByText("少")).toBeInTheDocument();
    expect(screen.getByText("多")).toBeInTheDocument();
  });
});
