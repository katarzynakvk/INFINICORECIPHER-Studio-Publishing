import { create } from "zustand";
import type { Project } from "../types/api";

interface ProjectStore {
  activeProject: Project | null;
  projectOperationBusy: boolean;
  saveState: "SAVED" | "SAVING" | "DIRTY" | "FAILED";
  setActiveProject: (project: Project | null) => void;
  beginProjectOperation: () => boolean;
  endProjectOperation: () => void;
  setSaveState: (state: "SAVED" | "SAVING" | "DIRTY" | "FAILED") => void;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  activeProject: null,
  projectOperationBusy: false,
  saveState: "SAVED",
  setActiveProject: (project) => set({ activeProject: project }),
  beginProjectOperation: () => {
    if (get().projectOperationBusy) return false;
    set({ projectOperationBusy: true });
    return true;
  },
  endProjectOperation: () => set({ projectOperationBusy: false }),
  setSaveState: (saveState) => set({ saveState }),
}));
