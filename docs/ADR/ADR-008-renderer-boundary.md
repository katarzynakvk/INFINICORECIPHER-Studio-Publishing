# ADR-008: Renderer Boundary

- **Status:** BLOCKED
- **Date:** 2026-11-21

## Decision

No concrete renderer is selected. Layout remains governed by `LayoutDocument`;
rendering is behind an adapter for preview and production.

## Required before implementation

- Concrete preview renderer
- Concrete production PDF renderer
- Preview/export parity strategy
- Font resolution strategy
- PDF format and page geometry tests
