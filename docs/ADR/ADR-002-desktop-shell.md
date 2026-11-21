# ADR-002: Desktop Shell

- **Status:** BLOCKED
- **Date:** 2026-11-21

## Problem

The Bible requires Windows desktop delivery but does not select a shell.

## Options

- pywebview with a local Flask backend
- Electron with a bundled backend
- Tauri with sidecar/process integration
- WinUI shell with backend integration

## Evaluation criteria

- Windows lifecycle and shutdown
- SQLite/WAL handle release
- Local origin/security
- Packaging and installer support
- Frontend/backend resource ownership
- Repeatable dependency locking

## Consequence

No desktop shell is accepted by this ADR package. Implementing shell-specific code
before a Founder/Architecture decision would be premature.
