# Architecture Baseline

**Source:** INFINICORECIPHER STUDIO PUBLISHING BIBLE v1.0
**Status:** PROPOSED — pending Founder/Architecture acceptance
**Build stage:** Phase 0

## 1. System shape

INFINICORECIPHER Studio Publishing is a Windows-targeted, local-first, project-based
desktop application with a backend-authoritative Flask API, one SQLite database per
Book Project, project-relative file storage, and a React/TypeScript client.

The backend API calls application services, which enforce application policy and
domain rules, and services use repositories and external adapters.

## 2. Baseline technology

These items are the Bible baseline, not claims of implementation:

| Concern | Baseline |
|---|---|
| Backend | Python 3.14-compatible implementation; Flask; typed contracts |
| Persistence | SQLite per project; explicit schema version; migrations; WAL only if accepted |
| Frontend | React; TypeScript; Vite; React Router; Zustand or accepted state layer |
| Desktop | Decision required in ADR-002 |
| Layout/renderer | Adapter boundary required; concrete renderer unresolved |
| AI | Adapter boundary required; provider/model unresolved |
| Upscaling | Adapter boundary required; provider unresolved |
| GCU | Closed-operation adapter; operations `canon_inventory`, `validate_assets`, `generate_manifest` |

## 3. Repository boundaries

- `backend/`: domain, services, repositories, API, security and adapters
- `frontend/`: typed UI state and API integration
- `desktop/`: shell and Windows packaging integration
- `docs/`: authority, architecture, evidence and operations
- `tests/`: cross-layer and acceptance evidence

## 4. Project isolation

Every Book Project is an isolation boundary. Project identity is persisted and
all services must verify `book_id`/`project_id` before accessing database rows,
files, jobs, events, conversations or exports.

Cross-project use is invalid unless represented by an explicit governed import.

## 5. Truthful implementation lifecycle

Capabilities progress through `MISSING`, `SCAFFOLDED`, `IMPLEMENTED`, `TESTED`,
`VERIFIED`, and `ACCEPTED`. `FILE EXISTS` is not capability evidence.

## 6. Testing strategy

Required test layers are unit, integration, API contract, database, file integrity,
UI, end-to-end, security, recovery, migration, accessibility, performance and
acceptance tests. Failure injection is required for database, storage, provider,
renderer, report, disk, interruption and migration failures.

No test is considered executed until a command, environment, suite and result are
recorded in the evidence register.

## 7. Resource lifecycle

SQLite connections, cursors, files, subprocesses, provider sessions, renderer
processes and temporary directories require explicit ownership and release.
Windows teardown must prove project directory deletion without locked database or
WAL/SHM handles.
