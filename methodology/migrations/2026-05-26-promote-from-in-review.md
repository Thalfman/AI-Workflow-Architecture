# Migration — allow promotion from `in_review`

- Date: 2026-05-26
- Methodology version: v0.2 → v0.3 (minor; additive)
- Docs: `methodology/commands/promote-workflow.md`, `methodology/methods/acceptance-review.md`

## What changed

`/promote-workflow` now accepts `in_review` as a valid source state, alongside
`building` and `revising`. Previously promotion was valid only from `building` or
`revising`, and `in_review` was explicitly a stop-and-report state.

## Why

`in_review` is in the status enum and the documented lifecycle (build → evaluate →
promote), but no command transitioned a workflow out of it into production, leaving
it orphaned. `in_review` is the natural "built, awaiting acceptance" state: a
workflow whose artifacts are complete but whose sample has not yet been accepted.
Wiring it into the promotion gate makes the lifecycle coherent. The four acceptance
gates are unchanged; only the set of valid source states expanded.

## Compatibility

Additive and backward compatible. Workflows promoted from `building` or `revising`
behave exactly as before. Existing workflows are not auto-migrated; they keep
recording the methodology version they were built against (`methodology/CLAUDE.md`).
`scripts/check_promotion_gate.py` encodes the same expanded set of source states
and is kept in sync with these docs.
