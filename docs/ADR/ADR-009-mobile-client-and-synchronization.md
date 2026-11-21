# ADR-009: Mobile Client and Synchronization Boundaries

- **Status:** PROPOSED — architecture review required
- **Date:** 2026-11-21
- **Related:** `docs/architecture/ARCHITECTURE-BASELINE.md`, `ROADMAP.md`

## Context

The Studio is currently implemented as a Windows-targeted, local-first desktop
application. The target ecosystem also needs a dedicated mobile client for Android
and iOS device classes, including tablets, large-screen and foldable devices.
Offline use and multiple clients introduce synchronization, conflict, identity,
authorization and sensitive-credential concerns that must not be hidden inside a
mobile UI implementation.

The authoritative Bible DOCX was not available in the repository when this ADR
was drafted. This proposal must be reconciled with the Bible and formally accepted
before it is treated as an authoritative requirement.

## Proposed architectural constraints

- Desktop and mobile clients use shared, versioned Studio contracts and stable
  project, Book, Edition, Page, Asset, Job and Conversation identities.
- Both clients operate on the same logical project source of truth and governed
  domain rules; mobile is not an independent publishing system.
- Mobile caches and pending offline changes expose explicit synchronization state.
- Conflicts involving production-critical or Canon-locked data are surfaced for
  governed resolution; they are never silently overwritten.
- Canon Lock, validation, asset approval, project permissions, Edition isolation
  and finalization rules apply equally on every client.
- Mobile interfaces adapt to phone, tablet, foldable and large-screen workspaces,
  touch/stylus input and keyboard/pointer input where available.
- Sensitive provider credentials are not exposed to the mobile client.
- A capability matrix will define which operations are available on each client
  and under which project, Edition, permission and synchronization conditions.

## Decisions required before implementation

1. Reconcile and accept the mobile requirements against the authoritative Bible.
2. Decide whether mobile is in v1 or a later release/workstream.
3. Define the authoritative service topology and how a mobile client reaches it
   without creating a competing project authority.
4. Choose the mobile implementation framework and supported OS baselines.
5. Define authentication, authorization, transport security and local-cache
   protection.
6. Define offline read/write capabilities, revision semantics, conflict handling,
   retries, interrupted synchronization, deletions and recovery.
7. Define asset-transfer behavior, limits and integrity verification.
8. Define the mobile capability matrix and acceptance/test strategy.

## Consequences

- No mobile framework, cloud service, transport or merge algorithm is selected by
  this proposal.
- The current Phase 1 Foundation acceptance gate and Phase 2 hard gate are
  unchanged.
- Mobile implementation must not begin until Phase 1 is formally accepted and
  mobile scope and blocking architecture decisions are approved.
- Final desktop packaging still requires resolution of the desktop-shell decision
  under ADR-002.
