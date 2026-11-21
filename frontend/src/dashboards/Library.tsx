import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useProjectStore } from "../store/projectStore";
import type { Project } from "../types/api";

export function Library() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
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
    }
  }

  async function openProject(project: Project) {
    try {
      const data = await apiRequest<{ project: Project }>("/api/v1/projects/open", {
        method: "POST",
        body: JSON.stringify({ root: project.root }),
      });
      setActiveProject(data.project);
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to open project");
    }
  }

  return (
    <div>
      <h1>Library</h1>
      {error && <div role="alert" className="error-state">{error}</div>}
      <form onSubmit={createProject}>
        <label htmlFor="project-title">Book title</label>
        <input
          id="project-title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />
        <button type="submit">Create project</button>
      </form>
      {loading ? (
        <div>Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="empty-state">No projects exist in this library.</div>
      ) : (
        <div className="project-grid">
          {projects.map((project) => (
            <article className="project-card" key={project.book_id}>
              <h2>{project.title}</h2>
              <small>{project.book_id}</small>
              <button type="button" onClick={() => void openProject(project)}>Open</button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
