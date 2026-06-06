import { afterEach } from "vitest";
// Registers jest-dom matchers AND augments Vitest's `expect` types
// (toBeInTheDocument, toHaveAttribute, ...). Safe to load for node tests too.
import "@testing-library/jest-dom/vitest";

// Unmount React trees between tests — but only when a DOM is available
// (component tests run under jsdom; pure-logic tests run under node).
afterEach(async () => {
  if (typeof document !== "undefined") {
    const { cleanup } = await import("@testing-library/react");
    cleanup();
  }
});
