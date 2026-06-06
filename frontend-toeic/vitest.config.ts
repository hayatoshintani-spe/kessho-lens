import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  test: {
    // Default to node for pure-logic tests; component tests opt into jsdom
    // via a `// @vitest-environment jsdom` docblock at the top of the file.
    environment: "node",
    globals: true,
    setupFiles: ["./test/setup.ts"],
    include: [
      "lib/**/*.test.ts",
      "lib/**/*.spec.ts",
      "components/**/*.test.tsx",
      "components/**/*.test.ts",
    ],
    coverage: {
      include: ["lib/**/*.ts", "components/**/*.tsx"],
      exclude: ["lib/**/*.test.ts", "lib/**/*.spec.ts", "lib/types/**", "**/*.d.ts"],
      reporter: ["text", "html"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
