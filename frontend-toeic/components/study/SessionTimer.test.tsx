// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen } from "@testing-library/react";
import { SessionTimer } from "./SessionTimer";

describe("SessionTimer", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-06-06T10:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders 00:00 at the moment the session starts", () => {
    const start = Date.now();
    render(<SessionTimer running startedAt={start} />);
    expect(screen.getByText("00:00")).toBeInTheDocument();
  });

  it("advances mm:ss while running", () => {
    const start = Date.now();
    render(<SessionTimer running startedAt={start} />);

    act(() => {
      vi.advanceTimersByTime(65_000); // 1m 5s
    });

    expect(screen.getByText("01:05")).toBeInTheDocument();
  });

  it("does not advance when not running", () => {
    const start = Date.now();
    render(<SessionTimer running={false} startedAt={start} />);

    act(() => {
      vi.advanceTimersByTime(30_000);
    });

    expect(screen.getByText("00:00")).toBeInTheDocument();
  });

  it("shows 00:00 when startedAt is null", () => {
    render(<SessionTimer running startedAt={null} />);
    expect(screen.getByText("00:00")).toBeInTheDocument();
  });

  it("zero-pads minutes and seconds", () => {
    const start = Date.now();
    render(<SessionTimer running startedAt={start} />);

    act(() => {
      vi.advanceTimersByTime(9_000); // 9s
    });

    expect(screen.getByText("00:09")).toBeInTheDocument();
  });
});
