import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import tokens from "../src/styles/panel.tokens.json";

describe("panel design tokens", () => {
  it("keeps the CSS variables in sync with the JSON palette", () => {
    const css = readFileSync(resolve(dirname(fileURLToPath(import.meta.url)), "../src/styles/panel.css"), "utf8");
    const values = new Map(
      Array.from(css.matchAll(/--(icc-[\w-]+):\s*([^;]+);/g), (match) => [
        match[1],
        match[2].trim(),
      ]),
    );

    for (const [name, value] of Object.entries(tokens.color)) {
      expect(values.get(`icc-${name}`)?.toLowerCase()).toBe(value.toLowerCase());
    }
    for (const value of tokens.space) {
      expect(values.get(`icc-space-${value}`)).toBe(`${value}px`);
    }
    for (const value of tokens.radius) {
      expect(values.get(`icc-radius-${value}`)).toBe(`${value}px`);
    }
    expect(values.get("icc-font")).toBe(tokens.font);
    expect(values.get("icc-body")).toBe(`${tokens.bodyPx}px`);
    expect(values.get("icc-control-min")).toBe(`${tokens.controlMinPx}px`);
  });
});
