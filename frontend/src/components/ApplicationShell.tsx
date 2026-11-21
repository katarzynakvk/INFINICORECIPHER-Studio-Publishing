import { NavLink, Outlet } from "react-router-dom";
import { NAVIGATOR_ITEMS } from "../routes/navigator";
import { useProjectStore } from "../store/projectStore";

export function ApplicationShell() {
  const activeProject = useProjectStore((state) => state.activeProject);
  const saveState = useProjectStore((state) => state.saveState);

  return (
    <div className="studio-shell">
      <aside className="global-navigator" aria-label="Global navigator">
        <img
          className="brand-logo"
          src="/logo.svg"
          alt="INFINICORECIPHER Studio Publishing"
        />
        <nav>
          {NAVIGATOR_ITEMS.map((item) => item.available ? (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => isActive ? "navigator-item active" : "navigator-item"}
            >
              <span>{item.number}</span>
              {item.label}
            </NavLink>
          ) : (
            <div key={item.path} className="navigator-item unavailable" aria-disabled="true">
              <span>{item.number}</span>
              {item.label}
              <small>Unavailable</small>
            </div>
          ))}
        </nav>
      </aside>
      <main className="studio-main">
        <header className="command-bar">
          <div>
            <strong>{activeProject?.title ?? "No active project"}</strong>
            {activeProject && <small>{activeProject.book_id}</small>}
          </div>
          <div className={`save-state ${saveState.toLowerCase()}`}>{saveState}</div>
        </header>
        <section className="dashboard-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
