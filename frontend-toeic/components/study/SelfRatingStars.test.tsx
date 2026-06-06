// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SelfRatingStars } from "./SelfRatingStars";

describe("SelfRatingStars", () => {
  it("renders five star buttons", () => {
    render(<SelfRatingStars value={3} onChange={() => {}} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons).toHaveLength(5);
  });

  it("labels each star for accessibility", () => {
    render(<SelfRatingStars value={0} onChange={() => {}} />);
    expect(screen.getByLabelText("1 stars")).toBeInTheDocument();
    expect(screen.getByLabelText("5 stars")).toBeInTheDocument();
  });

  it("fills stars up to the current value", () => {
    render(<SelfRatingStars value={3} onChange={() => {}} />);
    const filled = document.querySelectorAll("svg.fill-amber-400");
    expect(filled).toHaveLength(3);
  });

  it("calls onChange with the clicked star number", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<SelfRatingStars value={2} onChange={onChange} />);

    await user.click(screen.getByLabelText("4 stars"));
    expect(onChange).toHaveBeenCalledWith(4);
  });

  it("supports rating down to a single star", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<SelfRatingStars value={5} onChange={onChange} />);

    await user.click(screen.getByLabelText("1 stars"));
    expect(onChange).toHaveBeenCalledWith(1);
  });

  it("shows no filled stars when value is 0", () => {
    render(<SelfRatingStars value={0} onChange={() => {}} />);
    const filled = document.querySelectorAll("svg.fill-amber-400");
    expect(filled).toHaveLength(0);
  });
});
