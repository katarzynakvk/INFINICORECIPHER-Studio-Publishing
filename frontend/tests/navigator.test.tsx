import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApplicationShell } from "../src/components/ApplicationShell";
import { Library } from "../src/dashboards/Library";

describe("ApplicationShell", () => {
  afterEach(() => vi.restoreAllMocks());

  it("shows the canonical navigator and unavailable phase states", () => {
    vi.stubGlobal("fetch", vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: { projects: [] },
        error: null,
      }),
    })));
    render(
      <MemoryRouter initialEntries={["/library"]}>
        <Routes>
          <Route element={<ApplicationShell />}>
            <Route path="/library" element={<Library />} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByRole("img", { name: "INFINICORECIPHER Studio Publishing" })).toBeTruthy();
    expect(screen.getAllByText("Library").length).toBeGreaterThan(0);
    expect(screen.getByText("Canon & Visual DNA")).toBeTruthy();
    expect(screen.getAllByText("Unavailable").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: "Skip to content" }).getAttribute("href")).toBe("#main-content");
    expect(screen.getByRole("main").id).toBe("main-content");
    expect(screen.getByRole("navigation", { name: "Workspace and system" })).toBeTruthy();
    expect(screen.getByRole("link", { name: "Library" }).getAttribute("aria-current")).toBe("page");
    expect(screen.getByLabelText("Book title")).toBeTruthy();
  });
});
