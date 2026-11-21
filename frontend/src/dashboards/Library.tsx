import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useProjectStore } from "../store/projectStore";
import type { Project } from "../types/api";

export function Library() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const activeProject = useProjectStore((state) => state.activeProject);
  const setActiveProject = useProjectStore((state) => state.setActiveProject);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<{ projects: Project[] }>("/api/v1/projects");
      setProjects(data.projects);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load the library");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, []);

  async function createProject(event: React.FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const data = await apiRequest<{ project: Project }>("/api/v1/projects", {
        method: "POST",
        body: JSON.stringify({ title }),
      });
      setActiveProject(data.project);
      setTitle("");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to create project");
    } finally {
      setBusy(false);
    }
  }

  async function openProject(project: Project) {
    if (busy) return;
    setBusy(true);
    try {
      const data = await apiRequest<{ project: Project }>("/api/v1/projects/open", {
        method: "POST",
        body: JSON.stringify({ root: project.root }),
      });
      setActiveProject(data.project);
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to open project");
    } finally {
      setBusy(false);
    }
  }

  async function closeProject() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const result = await apiRequest<{ closed: boolean }>("/api/v1/projects/close", { method: "POST" });
      if (!result.closed) throw new Error("Project was not closed");
      setActiveProject(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to close project");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1>Library</h1>
      <p className="page-intro">Create and open your book projects from your local library.</p>
      {error && <div role="alert" className="error-state">{error}</div>}
      {activeProject && (
        <div className="panel">
          <h2>Open project</h2>
          <p>{activeProject.title}</p>
          <button type="button" disabled={busy} onClick={() => void closeProject()}>Close project</button>
        </div>
      )}
      <div className="panel">
        <h2>Start a new project</h2>
        <form className="create-form" onSubmit={createProject}>
          <div className="field">
            <label htmlFor="project-title">Book title</label>
            <input
              id="project-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={busy}>Create project</button>
        </form>
      </div>
      <h2 className="section-heading">Your projects</h2>
      {loading ? (
        <div role="status">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="empty-state">No projects exist in this library.</div>
      ) : (
        <div className="project-grid">
          {projects.map((project) => (
            <article className="project-card" key={project.book_id}>
              <h2>{project.title}</h2>
              <small>{project.book_id}</small>
              <button type="button" disabled={busy} onClick={() => void openProject(project)}>Open</button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
