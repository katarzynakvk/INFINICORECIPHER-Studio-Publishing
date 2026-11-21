# Architecture Lock

**Status:** ACCEPTED
**Source revision:** repository `93f7969`
**Founder decision:** ACCEPTED by the Founder on 2026-11-21

## Accepted for proposal

The following constraints are derived directly from the Bible and are not open to
implementation reinterpretation:

- Backend-authoritative Flask API
- Typed Python domain contracts
- SQLite per Book Project
- React/TypeScript/Vite frontend
- Explicit schema migrations and foreign-key enforcement
- Project-relative governed storage
- Adapter boundaries for AI, upscaling, rendering and GCU
- Immutable approved revisions and successor revisions
- Explicit human approval; AI cannot approve
- Project and Edition scoped operations
- SHA-256 evidence for governed files
- Phase-gated implementation

## Requires decision

- Concrete Python runtime version and lock
- Desktop shell
- Renderer technology
- AI provider/model
- Upscaling provider
- KDP ruleset verification authority
- Authentication and credential mechanism details
- Local event delivery transport
- Migration and installer tooling

## Lock rule

No implementation may silently resolve a decision marked in this document as
requiring decision. Material change requires an ADR update and approval.
