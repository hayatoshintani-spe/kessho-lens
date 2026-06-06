// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { TodayTaskList } from "./TodayTaskList";
import type { DailyTask, SkillCode, TaskStatus } from "@/lib/types/db";

function makeTask(
  skill: SkillCode,
  minutes: number,
  status: TaskStatus = "pending",
): DailyTask {
  return {
    id: `${skill}-${minutes}`,
    user_id: "u1",
    task_date: "2026-06-06",
    skill_code: skill,
    target_minutes: minutes,
    status,
    content_item_id: null,
    created_at: "2026-06-06T00:00:00Z",
    updated_at: "2026-06-06T00:00:00Z",
  };
}

describe("TodayTaskList", () => {
  it("shows an empty state when there are no tasks", () => {
    render(<TodayTaskList tasks={[]} />);
    expect(
      screen.getByText(/まだ今日のタスクがありません/),
    ).toBeInTheDocument();
  });

  it("renders each task with its Japanese skill label and minutes", () => {
    render(
      <TodayTaskList
        tasks={[makeTask("vocabulary", 20), makeTask("listening", 25)]}
      />,
    );
    expect(screen.getByText("単語")).toBeInTheDocument();
    expect(screen.getByText("リスニング")).toBeInTheDocument();
    expect(screen.getByText("目安 20 分")).toBeInTheDocument();
    expect(screen.getByText("目安 25 分")).toBeInTheDocument();
  });

  it("summarizes done vs total minutes in the badge", () => {
    render(
      <TodayTaskList
        tasks={[
          makeTask("vocabulary", 20, "done"),
          makeTask("grammar", 15, "pending"),
          makeTask("reading", 15, "pending"),
        ]}
      />,
    );
    // 20 done out of 50 total
    expect(screen.getByText("20/50分")).toBeInTheDocument();
  });

  it("labels pending tasks 開始 and done tasks もう一度", () => {
    render(
      <TodayTaskList
        tasks={[
          makeTask("vocabulary", 20, "pending"),
          makeTask("grammar", 15, "done"),
        ]}
      />,
    );
    expect(screen.getByText("開始")).toBeInTheDocument();
    expect(screen.getByText("もう一度")).toBeInTheDocument();
  });

  it("links each task to its study route", () => {
    render(<TodayTaskList tasks={[makeTask("shadowing", 15)]} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/study/shadowing");
  });
});
