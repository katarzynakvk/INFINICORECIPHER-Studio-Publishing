# Architecture Baseline

**Source:** INFINICORECIPHER STUDIO PUBLISHING BIBLE v1.0
**Status:** PROPOSED — pending Founder/Architecture acceptance
**Build stage:** Phase 0

## 1. System shape

INFINICORECIPHER Studio Publishing is a local-first, project-based Studio ecosystem.
The current implementation baseline is a Windows-targeted desktop application with
a backend-authoritative Flask API, one SQLite database per Book Project,
project-relative file storage, and a React/TypeScript client.

The target architecture also includes a dedicated mobile client for Android phones
and tablets, large-screen and foldable Android devices, iPhone and iPad. Desktop
and mobile are clients of the same governed Studio contracts and logical project
source of truth; mobile is not an independent publishing system. The mobile client
is a future architectural workstream, not a claim of current implementation or
accepted release scope.

The backend API calls application services, which enforce application policy and
domain rules, and services use repositories and external adapters. A mobile client
must use the same authoritative services and domain rules rather than reimplement
Canon, permissions, production state or persistence policy.

## 1.1 Proposed mobile architecture extension

This section records a proposed architecture extension for review. The Bible DOCX
was not present in the repository when this proposal was recorded; therefore this
section does not claim that the Bible has been amended or that this extension has
received Founder/Architecture acceptance. Reconcile it with the authoritative
Bible before treating it as an accepted requirement.

### Shared Studio contracts

The mobile client must consume the shared, versioned Studio contracts for Project
ID, Book ID, Edition ID, Page ID, Asset ID, Job ID, Conversation ID, Canon data,
manuscript structure, project metadata, production status, Asset Library metadata,
generation-job state, validation state, version information, permissions,
authentication and synchronization state. It must not create incompatible
identifiers, domain representations or an independent persistence authority.

Desktop and mobile must address the same logical project, edition, page, asset,
job, conversation and governed revisions. Local mobile data may cache server or
project data and hold pending changes for offline work, but must expose its
synchronization state and must never silently become a competing authoritative
book version.

The synchronization contract must eventually define revision identity, change
timestamps, pending operations, conflict detection and resolution, retries,
interrupted synchronization, offline edits, deletion/tombstone handling, asset
transfer and recovery. The following user-visible states are a proposed minimum;
exact transitions and whether additional states are needed remain for a future ADR:

```text
SYNCED
OFFLINE
PENDING_UPLOAD
PENDING_DOWNLOAD
CONFLICT
SYNC_FAILED
```

Conflicts involving production-critical data or Canon-locked information must be
presented explicitly and resolved through governed workflows. They must not be
silently overwritten or resolved by last-write-wins.

### Mobile capabilities and adaptive workspace

Mobile access must be capability-based and permission-aware. A future capability
matrix must define which Studio operations are available on each device class and
under which online, offline, project, Edition and permission conditions. This
architecture proposal does not imply full desktop feature parity or authorize
mobile-only production operations.

The mobile interface must use purpose-designed responsive workspace modes rather
than simply scaling down the desktop UI. Navigation, panels, editors, dialogs and
production controls must adapt to available space, including phone, tablet,
foldable and large-screen layouts, portrait and landscape, and accessibility
settings. The canonical Studio dashboard order and backend capability truth remain
authoritative across clients.

The interaction model should support touch, long press, drag-and-drop, stylus,
hardware keyboard, pointer and accessibility input where available. Destructive
or governance-sensitive actions—including changing locked Canon, deleting assets,
replacing approved content or changing publication structure—must require clear,
deliberate confirmation and cannot depend only on an easily triggered gesture.

### Governance and security

Canon Lock, validation, controlled Canon changes, asset approval, project
permissions, Edition isolation and finalization rules apply identically on every
client. Shared backend/domain policies are authoritative; clients may not weaken
them or maintain separate Canon logic.

Authentication, authorization, credential storage, transport security, local
cache protection and provider-secret boundaries are explicit architecture
dependencies. Sensitive provider credentials must not be embedded in or exposed
to the mobile client. The concrete authentication and credential design remains
subject to the existing security decision process.

### Decisions intentionally left open

This proposal does not select a mobile framework, synchronization transport,
deployment topology, cloud service, conflict-merge algorithm, offline write
policy, asset-transfer protocol, authentication mechanism or mobile release
scope. In particular, the logical single source of truth does not prescribe
whether a mobile client connects to a desktop-hosted service, a separately
deployed service or another accepted topology. Resolve these decisions through
reviewed ADRs before implementing synchronization or remote production workflows.

## 2. Baseline technology

These items are the Bible baseline, not claims of implementation:

| Concern | Baseline |
|---|---|
| Backend | Python 3.14-compatible implementation; Flask; typed contracts |
| Persistence | SQLite per project; explicit schema version; migrations; WAL only if accepted |
| Frontend | React; TypeScript; Vite; React Router; Zustand or accepted state layer |
| Desktop | Decision required in ADR-002 |
| Mobile | First-class Android/iOS client; capability-adapted UI and shared Studio contracts; implementation and synchronization decisions deferred to ADR-009 |
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
