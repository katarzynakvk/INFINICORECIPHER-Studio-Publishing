# Engineering Constitution

The repository implements the following non-negotiable rules.

1. Project Data beats conversation memory.
2. Backend state beats frontend state.
3. Persistent state beats visual assumptions.
4. AI proposes; humans approve.
5. AI cannot approve, change governing Canon or overwrite approved text.
6. Approved revisions are immutable.
7. Editing an approved entity creates a successor revision.
8. Save does not mean approval.
9. Every mutation carries project scope and expected revision where applicable.
10. Cross-Book access is blocked unless an explicit governed import exists.
11. Secrets never enter Project Data, manifests, prompts, diagnostics or logs.
12. All governed paths are resolved and validated server-side.
13. SQLite resources have explicit, idempotent lifecycle management.
14. Validation checks must return truthful states:
   `PASS`, `FAIL`, `WARNING`, `NOT_TESTED`, `NOT_SUPPORTED`, `BLOCKED`.
15. UNCERTAIN operations never become COMPLETED.
16. Exports are not complete until required files and reports persist and verify.
17. Effective PPI is calculated from placement size, never assumed from DPI metadata.
18. Every external capability is behind an adapter contract and capability registry.
