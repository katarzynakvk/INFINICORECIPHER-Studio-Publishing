# ADR-005: Frontend Architecture

- **Status:** PROPOSED
- **Date:** 2026-11-21

## Decision

Use React, TypeScript, Vite, React Router and Zustand or a similarly explicit accepted
state layer. The frontend will present backend state and track only working UI state.

## Consequences

- Typed API clients and error envelopes are required.
- Implementation routes may only expose implemented capabilities.
