# ADR-001: Technology Stack

- **Status:** PROPOSED
- **Date:** 2026-11-21
- **Scope:** Backend, frontend and dependency strategy

## Decision

Use Flask with typed Python contracts, SQLite, React, TypeScript and Vite as the
baseline required by the Bible. Pin a verified runtime and dependency lock before
implementation acceptance.

## Alternatives

- FastAPI instead of Flask
- Django instead of Flask
- Electron or other shell remains separate

## Consequences

- Python 3.14 compatibility must be verified against available dependencies.
- Dependency locks and repeatable builds are mandatory.
- Frontend must remain a working UI state client, never persistence authority.

## Required approval

Founder/Architecture acceptance must approve this proposal and the exact runtime pin.
