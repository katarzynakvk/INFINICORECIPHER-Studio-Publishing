import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Library } from "../src/dashboards/Library";
import { useProjectStore } from "../src/store/projectStore";
import type { Project } from "../src/types/api";

const project: Project = {
  book_id: "book-1",
  title: "First Book",
  schema_version: 2,
  created_at: "2026-01-01",
  state: "ACTIVE",
  root: "/library/first",
};

function response(data: unknown, ok = true) {
  return {
    ok,
    status: ok ? 200 : 409,
    json: async () => ({
      success: ok,
      data: ok ? data : null,
      error: ok ? null : { code: "ERROR", message: "Close failed" },
    }),
  };
}

describe("Library close project", () => {
  afterEach(() => {
    cleanup();
    useProjectStore.getState().setActiveProject(null);
    useProjectStore.getState().endProjectOperation();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("clears the active project only after the backend closes it", async () => {
    useProjectStore.getState().setActiveProject(project);
    const fetchMock = vi.fn(async (path: string) =>
      path.endsWith("/close") ? response({ closed: true }) : response({ projects: [] }),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<Library />);

    fireEvent.click(screen.getByRole("button", { name: "Close project" }));
    await waitFor(() => expect(useProjectStore.getState().activeProject).toBeNull());
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/projects/close",
      expect.objectContaining({ method: "POST" }),
    );
    expect(screen.queryByRole("button", { name: "Close project" })).toBeNull();
  });

  it("keeps the active project when closing fails", async () => {
    useProjectStore.getState().setActiveProject(project);
    vi.stubGlobal("fetch", vi.fn(async (path: string) =>
      path.endsWith("/close") ? response(null, false) : response({ projects: [] }),
    ));
    render(<Library />);

    fireEvent.click(screen.getByRole("button", { name: "Close project" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Close failed");
    expect(useProjectStore.getState().activeProject).toEqual(project);
    expect(screen.getByRole("button", { name: "Close project" })).toBeTruthy();
  });

  it("keeps lifecycle actions disabled if the Library is remounted during close", async () => {
    useProjectStore.getState().setActiveProject(project);
    let finishClose!: (value: ReturnType<typeof response>) => void;
    vi.stubGlobal("fetch", vi.fn((path: string) =>
      path.endsWith("/close")
        ? new Promise<ReturnType<typeof response>>((resolve) => { finishClose = resolve; })
        : Promise.resolve(response({ projects: [] })),
    ));
    const first = render(<Library />);
    fireEvent.click(screen.getByRole("button", { name: "Close project" }));
    first.unmount();
    render(<Library />);
    expect((screen.getByRole("button", { name: "Close project" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Create project" }) as HTMLButtonElement).disabled).toBe(true);
    finishClose(response({ closed: true }));
    await waitFor(() => expect(useProjectStore.getState().projectOperationBusy).toBe(false));
    expect(useProjectStore.getState().activeProject).toBeNull();
  });
});
