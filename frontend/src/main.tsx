import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ApplicationShell } from "./components/ApplicationShell";
import { Library } from "./dashboards/Library";
import { Settings } from "./dashboards/Settings";
import { Unavailable } from "./dashboards/Unavailable";
import "./styles/panel.css";
import "./styles/tokens.css";
import "./styles/shell.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<ApplicationShell />}>
          <Route index element={<Navigate to="/library" replace />} />
          <Route path="/library" element={<Library />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/settings/book" element={<Settings />} />
          <Route path="*" element={<Unavailable />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
