# ADR-006: Backend Architecture

- **Status:** PROPOSED
- **Date:** 2026-11-21

## Decision

Use Flask routes/contracts, application services, domain rules, repositories and
provider/resource adapters. API routes do not own primary domain logic.

## Consequences

- Transactions, revisions and mutations are service/repository concerns.
- External capabilities remain behind adapter contracts.
