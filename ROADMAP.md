# Roadmap

Phase status is evidence-based, not filename-based.

| Phase | Status | Unlock condition |
|---|---|---|
| 0 — Audit & Architecture Lock | ACCEPTED | Phase 0 Founder Acceptance recorded |
| 1 — Foundation | IN_PROGRESS | Phase 0 accepted |
| 2 — Manuscript & Planning | NOT_STARTED | Phase 1 accepted |
| 3 — AI & Production | NOT_STARTED | Phase 2 accepted |
| 4 — Cover & Publishing | NOT_STARTED | Phase 3 accepted |
| 5 — Hardening | NOT_STARTED | Phase 4 accepted |
| 6 — Acceptance and v1 Release | NOT_STARTED | Phase 5 accepted |

## Future architectural workstream

| Workstream | Status | Entry condition | Gate |
|---|---|---|---|
| Mobile Client & Synchronization | PROPOSED — NOT_STARTED | Phase 1 formally accepted; reconcile proposal with the authoritative Bible and decide release scope | Approve ADR-009, service topology, security boundary, capability matrix and synchronization contract before implementation |

This is a future cross-cutting architecture workstream, not a new numbered phase
and not authorization to begin mobile implementation during Phase 1 or Phase 2.
Planning may define its scope after the Phase 1 gate; implementation must follow
approved dependencies and its own acceptance criteria. No v1 inclusion or exclusion
is implied until the authoritative specification and Founder decision establish it.

The mobile client is intended to be a first-class client of the same logical Studio
projects and governed contracts, not an independent publishing system. See
`docs/architecture/ARCHITECTURE-BASELINE.md` and proposed
`docs/ADR/ADR-009-mobile-client-and-synchronization.md`.
