# Architecture Blockers

| ID | Blocker | Impact | Required decision | State |
|---|---|---|---|---|
| B-001 | Python runtime not pinned; Bible allows Python 3.14-compatible | Dependency and build reproducibility | Approved runtime/installer baseline | OPEN |
| B-002 | Desktop shell unresolved | Foundation shell, packaging and lifecycle | Select shell per ADR-002 | OPEN |
| B-003 | Renderer unresolved | Preview/export implementation | Select preview and production renderer per ADR-008 | OPEN |
| B-004 | AI provider unresolved | AI operations and tests | Select provider adapter policy | OPEN |
| B-005 | Upscaler provider unresolved | Print-asset derivatives | Select provider or defer capability | OPEN |
| B-006 | KDP ruleset source authority unresolved | Profiles and validation | Verified rules source and verification authority | OPEN |
| B-007 | Authentication/credential details unresolved | Local role and secret boundary | Approved mechanism | OPEN |
| B-008 | Existing GCU executable unavailable from repository audit | GCU operations | Provide executable/spec or mark NOT_SUPPORTED | OPEN |
| B-009 | Bible attachment provides a complete section registry but no detailed body text | Some low-level requirements remain to be extracted from the DOCX source | Obtain/source the complete DOCX or confirmed detailed markdown | OPEN |

No application implementation should falsely depend on these decisions being closed.
