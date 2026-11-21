# ADR-003: Database

- **Status:** PROPOSED
- **Date:** 2026-11-21

## Decision

Use one SQLite database per Book Project, explicit migrations, foreign-key
enforcement, explicit connection lifecycle and WAL only after Windows teardown
and integrity testing demonstrate it is safe.

## Consequences

- Every database method must define close/idempotent cleanup.
- Windows teardown tests must prove directory deletion succeeds.
- A project database is never shared implicitly across projects.
