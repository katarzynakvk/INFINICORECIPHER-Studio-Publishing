import { create } from "zustand";
import type { Project } from "../types/api";

interface ProjectStore {
  activeProject: Project | null;
  saveState: "SAVED" | "SAVING" | "DIRTY" | "FAILED";
  setActiveProject: (project: Project | null) => void;
  setSaveState: (state: "SAVED" | "SAVING" | "DIRTY" | "FAILED") => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  activeProject: null,
  saveState: "SAVED",
  setActiveProject: (project) => set({ activeProject: project }),
  setSaveState: (saveState) => set({ saveState }),
}));
