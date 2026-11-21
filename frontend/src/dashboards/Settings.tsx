import { type FormEvent, useEffect, useMemo, useState } from "react";
import { apiRequest } from "../api/client";
import { useProjectStore } from "../store/projectStore";
import type { Setting, SettingScope } from "../types/api";

const SCOPES: SettingScope[] = ["BOOK", "EDITION", "PROJECT"];

export function Settings() {
  const activeProject = useProjectStore((state) => state.activeProject);
  const setSaveState = useProjectStore((state) => state.setSaveState);
  const [scope, setScope] = useState<SettingScope>("BOOK");
  const [scopeId, setScopeId] = useState("");
  const [key, setKey] = useState("trim_size");
  const [value, setValue] = useState("");
  const [setting, setSetting] = useState<Setting | null>(null);
  const [state, setState] = useState<"UNSET" | "EXPLICIT">("UNSET");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolvedScopeId = useMemo(
    () => scope === "BOOK" ? activeProject?.book_id ?? "" : scopeId.trim(),
    [activeProject?.book_id, scope, scopeId],
  );

  useEffect(() => {
    setSetting(null);
    setState("UNSET");
    setError(null);
  }, [scope, resolvedScopeId, key]);

  async function loadSetting() {
    if (!resolvedScopeId || !key.trim()) {
      setError("Scope, scope identity and key are required.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<{ setting: Setting | null; state: "UNSET" | "EXPLICIT" }>(
        `/api/v1/settings?scope=${encodeURIComponent(scope)}&scope_id=${encodeURIComponent(resolvedScopeId)}&key=${encodeURIComponent(key.trim())}`,
      );
      setSetting(data.setting);
      setState(data.state);
      setValue(data.setting?.value == null ? "" : String(data.setting.value));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load setting");
    } finally {
      setLoading(false);
    }
  }

  async function saveSetting(event: FormEvent) {
    event.preventDefault();
    if (!resolvedScopeId || !key.trim()) {
      setError("Scope, scope identity and key are required.");
      return;
    }
    setLoading(true);
    setError(null);
    setSaveState("SAVING");
    try {
      const data = await apiRequest<Setting>("/api/v1/settings", {
        method: "POST",
        body: JSON.stringify({
          scope,
          scope_id: resolvedScopeId,
          key: key.trim(),
          value,
        }),
      });
      setSetting(data);
      setState(data.state);
      setSaveState("SAVED");
    } catch (caught) {
      setSaveState("FAILED");
      setError(caught instanceof Error ? caught.message : "Unable to save setting");
    } finally {
      setLoading(false);
    }
  }

  if (!activeProject) {
    return (
      <div>
        <h1>Settings</h1>
        <div className="blocked-state">Open a project before editing project-scoped settings.</div>
      </div>
    );
  }

  return (
    <div>
      <h1>Settings</h1>
      <p className="page-intro">Only explicitly persisted values are shown. Unset values have no hidden fallback.</p>
      {error && <div role="alert" className="error-state">{error}</div>}
      <div className="panel">
        <h2>Explicit setting</h2>
        <form onSubmit={saveSetting} className="settings-form">
          <div className="field">
            <label htmlFor="setting-scope">Scope</label>
            <select id="setting-scope" value={scope} onChange={(event) => setScope(event.target.value as SettingScope)}>
              {SCOPES.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="setting-scope-id">Scope identity</label>
            <input
              id="setting-scope-id"
              value={scope === "BOOK" ? activeProject.book_id : scopeId}
              onChange={(event) => setScopeId(event.target.value)}
              readOnly={scope === "BOOK"}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="setting-key">Key</label>
            <input id="setting-key" value={key} onChange={(event) => setKey(event.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="setting-value">Value</label>
            <input id="setting-value" value={value} onChange={(event) => setValue(event.target.value)} />
          </div>
          <div className="settings-actions">
            <button type="button" onClick={() => void loadSetting()} disabled={loading}>Read value</button>
            <button type="submit" disabled={loading}>Save explicit value</button>
          </div>
        </form>
      </div>
      <div className={`setting-state ${state.toLowerCase()}`}>
        <strong>{state}</strong>
        {setting && <span>Revision {setting.revision}</span>}
      </div>
    </div>
  );
}
