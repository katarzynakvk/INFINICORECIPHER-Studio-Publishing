# Bible Traceability Matrix

**Status:** INITIAL EXTRACTION

| Requirement ID | Bible authority | Phase | Implementation requirement | Verification | Current state |
|---|---|---|---|---|---|
| R-2.1 | §§2.1, 33, 34 | 1 | One persistent project and database per Book | Project lifecycle and isolation tests | MISSING |
| R-2.2 | §2.2, §37.17 | 1/All | Project-scoped database, files, jobs and context | Cross-Book access tests | MISSING |
| R-2.5 | §§2.5-2.7, 33.7 | 1/All | Immutable approved revisions with successor revisions | Revision and approval tests | MISSING |
| R-2.9 | §§2.9-2.11 | 1/All | No hidden defaults or synthetic success | Contract and UI state tests | MISSING |
| R-2.12 | §§2.12-2.13, 52.2 | 3/All | AI cannot approve or alter locked Canon | Permission and gateway tests | MISSING |
| R-3.1 | §§3.1-3.30, 4 | 1 | Application shell and truthful navigator states | Component/routing tests | MISSING |
| R-4.12 | §4.12 | 1 | Fourteen canonical dashboard entries | Navigator tests | MISSING |
| R-7.4 | §§7.4-7.12 | 1/4 | Versioned book/edition settings and dependency impact | Settings/KDP tests | MISSING |
| R-8 | §§8.1-8.24 | 4 | Versioned, pinned verified rulesets | KDP rule tests | MISSING |
| R-9 | §§9.1-9.23 | 1/3 | CanonRevision, DNA, references, locks and conflicts | Canon domain tests | MISSING |
| R-10 | §§10.1-10.21 | 2 | Source preservation, manuscript revisions and exact text | Import/hash/diff tests | MISSING |
| R-11 | §§11.1-11.10 | 2 | Stable pages and manual/assisted/blueprint planning | Planner/integrity tests | MISSING |
| R-12 | §§12.1-12.17 | 2 | PT-01 through PT-12 registry separate from page role | Registry tests | MISSING |
| R-14 | §§14.1-14.18 | 3 | Registered AI gateway and prohibited operations | Gateway/permission tests | MISSING |
| R-15 | §§15.1-15.18 | 3 | Scoped ContextManifest with hashes | Context isolation tests | MISSING |
| R-17 | §§17.1-17.19 | 3 | Candidate assets remain separate from approved source | Pipeline and approval tests | MISSING |
| R-18 | §§18.1-18.16 | 3 | Upscaling creates derivatives and validates effective PPI | Upscaler and PPI tests | MISSING |
| R-19 | §§19.1-19.21 | 3 | Independently managed interior layers | Composition and reopen tests | MISSING |
| R-20 | §§20.1-20.20 | 3/4 | LayoutDocument and adapter-rendered parity | Layout/renderer tests | MISSING |
| R-21 | §§21.1-21.19 | 4 | Cover revisions and dependency-driven review | Cover tests | MISSING |
| R-25 | §§25.1-25.13 | 4 | Explicit validation states and reports | Validation state tests | MISSING |
| R-26 | §§26.1-26.20 | 4 | Frozen export inputs and verified immutable exports | Export/package tests | MISSING |
| R-27 | §27 | 3/All | Governed job lifecycle, idempotency and recovery | Job lifecycle tests | MISSING |
| R-32 | §32 | 1 | Canonical project storage and safe paths | File integrity/security tests | MISSING |
| R-34 | §34 | 1 | Explicit SQLite schema, transactions and migrations | Database tests | MISSING |
| R-37 | §37 | 1/5 | Security and project scope enforcement | Security tests | MISSING |
| R-44 | §44 | 1/5 | Recovery and atomic persistence | Crash/recovery tests | MISSING |
| R-48 | §48 | All | Complementary test and evidence strategy | Gate execution | MISSING |
| R-49 | §49 | 5/6 | Repeatable Windows build and migration | Build/install/upgrade tests | MISSING |
