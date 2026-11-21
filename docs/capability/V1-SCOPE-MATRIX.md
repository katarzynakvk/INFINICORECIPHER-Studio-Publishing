# V1 Scope Matrix

**Status:** PROPOSED

| Capability | V1 disposition | Evidence required |
|---|---|---|
| Persistent per-Book projects | REQUIRED | Project lifecycle, database, isolation tests |
| Library, project overview and settings | REQUIRED | Implemented shell/API/UI tests |
| Canon and Visual DNA | REQUIRED | Revision, lock, approval and dependency tests |
| Manuscript import, versioning and text integrity | REQUIRED | TXT/DOCX/paste, hash and diff tests |
| Page planning and canonical PT-01–PT-12 | REQUIRED | Planning, identity and integrity tests |
| Illustration generation and approval | REQUIRED | AI boundary, candidate, approval tests |
| Upscaling and print derivatives | REQUIRED, provider capability may be NOT_SUPPORTED until adapter | Derivative/provenance tests |
| Interior Studio and LayoutDocument | REQUIRED | Composition and renderer tests |
| Cover Studio | REQUIRED | Cover dependency and approval tests |
| Validation and review | REQUIRED | Evidence tests for PASS/WARNING/FAIL/NOT_SUPPORTED |
| Interior and cover export | REQUIRED | Frozen input and artifact verification tests |
| GCU operations | REQUIRED adapter boundary; concrete operations remain capability-gated | Adapter and independent validation tests |
| Backup and restore | REQUIRED | Verification and restore tests |
| Windows desktop delivery | REQUIRED | Approved desktop shell, installer and cleanup tests |
| External Amazon approval | EXCLUDED | State internal validation only |
| Pilot-specific Canon as global Canon | EXCLUDED | Isolation test |

## v1 exclusions

- Publishing-platform approval claims
- Silent cross-Book operations
- AI self-approval
- Future/custom page types as global Canon
- Converting previews or exports into governing state
