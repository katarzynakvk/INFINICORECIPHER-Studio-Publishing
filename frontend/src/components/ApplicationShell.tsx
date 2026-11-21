import { NavLink, Outlet } from "react-router-dom";
import { NAVIGATOR_ITEMS } from "../routes/navigator";
import { useProjectStore } from "../store/projectStore";

export function ApplicationShell() {
  const activeProject = useProjectStore((state) => state.activeProject);
  const saveState = useProjectStore((state) => state.saveState);

  return (
    <div className="studio-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <aside className="global-navigator" aria-label="Global navigator">
        <img
          className="brand-logo"
          src="/logo.svg"
          alt="INFINICORECIPHER Studio Publishing"
        />
        <nav aria-label="Workspace and system">
          {NAVIGATOR_ITEMS.map((item) => item.available ? (
            <div key={item.path}>
              {(item.number === "01" || item.number === "12") && (
                <div className="navigator-heading">{item.number === "01" ? "Workspace" : "System"}</div>
              )}
              <NavLink
                to={item.path}
                className={({ isActive }) => isActive ? "navigator-item active" : "navigator-item"}
              >
                <span aria-hidden="true">{item.number}</span>
                {item.label}
              </NavLink>
            </div>
          ) : (
            <div key={item.path}>
              {item.number === "12" && <div className="navigator-heading">System</div>}
              <div className="navigator-item unavailable" aria-disabled="true">
                <span aria-hidden="true">{item.number}</span>
                {item.label}
                <small>Unavailable</small>
              </div>
            </div>
          ))}
        </nav>
      </aside>
      <main className="studio-main" id="main-content" tabIndex={-1}>
        <header className="command-bar">
          <div className="project-context">
            <span className="context-label">Current project</span>
            <strong>{activeProject?.title ?? "No active project"}</strong>
            {activeProject && <small>{activeProject.book_id}</small>}
          </div>
          <div className={`save-state ${saveState.toLowerCase()}`} role="status">
            <span className="status-dot" aria-hidden="true" />
            {saveState}
          </div>
        </header>
        <section className="dashboard-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
