# ADR-004: Storage Model

- **Status:** PROPOSED
- **Date:** 2026-11-21

## Decision

Use project-relative governed folders matching the Bible storage architecture.
All write operations must use server-side path validation, atomic staging and hash
verification where the file is governed.

## Consequences

- Project movement and database/file reconciliation require explicit services.
- Symlinks and junctions are security-sensitive and require tests.
