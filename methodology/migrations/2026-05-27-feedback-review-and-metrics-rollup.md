# Migration — close the feedback loop (feedback-review + metrics rollup)

- Date: 2026-05-27
- Methodology version: v0.6 → v0.7 (minor; additive)
- Docs/files: `methodology/methods/feedback-review.md` (new),
  `scripts/rollup_metrics.py` (new), `tests/` (new — the repo's first test harness:
  `tests/test_rollup_metrics.py`, `tests/conftest.py`), `requirements-dev.txt` (new).
  First real run packets under
  `workflows/weekly-status-summary/operations/run-records/` and the first
  `portfolio/value-ledger.yaml` entry (written by the rollup, not by hand).

## What changed

Closed the backward arc of the lifecycle (stages 6 → 7 in
`docs/plans/closed-loop-repo-assessment.md`), which until now was designed but never
exercised. Two cheap pieces:

1. **A measurement connector.** `scripts/rollup_metrics.py <id>` reads every
   `RUN_RECORD.md` for a workflow, computes the clean-send rate (runs the reviewer
   approved with no edits ÷ total runs), writes it into the contract's
   `success_metric.current_value`, and appends one `event: value` entry to
   `portfolio/value-ledger.yaml`. It edits both files surgically to preserve their
   hand-written comments, and it **refuses to write and exits non-zero when there are
   no run records** — a never-run workflow gets `null`, never a fabricated number.
2. **A feedback-review ritual.** `methodology/methods/feedback-review.md` defines the
   recurring, manual moment where run records and the measured metric are read and
   turned into a keep / revise / retire decision. It mirrors `acceptance-review.md`:
   acceptance review is the entry gate, feedback review is the ongoing gate.

The reference workflow `weekly-status-summary` was operated for three synthetic weeks
to produce the first real run packets, and the rollup populated its
`current_value` (0.6667 vs a ≥ 0.9 target) — making the loop demonstrable end to end.

## Why

`success_metric.current_value` had always been `null` and the value ledger empty:
nothing flowed backward from runs into measurement. The forward arc (intake → route →
scope → create → promote → run) was complete; the loop was open at exactly these two
points. This is the lightest mechanism that closes it, consistent with the
constitution's "resist premature abstraction" stance — no dashboards, no
auto-revision agents, no anomaly mining.

## Compatibility

Additive and backward compatible. **No contract schema change** — `current_value`
was already a nullable field; the rollup only fills it. No run-record schema change.
Existing lifecycle commands and scripts behave exactly as before. Existing workflows
are not auto-migrated: they keep the `methodology_version` recorded in their contract
(per `methodology/CLAUDE.md`) and adopt the feedback-review cadence when next touched.
`tests/` is scoped to the rollup only and is not wired into CI; the runtime install
(`requirements.txt`) is unchanged, with pytest pinned separately in
`requirements-dev.txt`.
