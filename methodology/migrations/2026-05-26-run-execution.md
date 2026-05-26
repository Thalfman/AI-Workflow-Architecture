# Migration — add the run-execution layer (/run-workflow + run packets)

- Date: 2026-05-26
- Methodology version: v0.4 → v0.5 (minor; additive)
- Docs: `methodology/commands/run-workflow.md`, `.claude/commands/run-workflow.md`,
  `methodology/templates/run-packet/` (six packet templates), `scripts/workflowctl.py`,
  and a clarifying comment in `methodology/schemas/run-record.schema.yaml`. Light edits
  to `.gitignore`, `.claude/settings.json`,
  `workflows/weekly-status-summary/operations/runbook.md`, and the PR1 routing docs that
  forward-referenced this command.

## What changed

Added the execution path for **Funnel B** (a normal run of a production workflow). A
new `/run-workflow <id> <input-folder>` command performs one production run and
captures it as an auditable **run packet** at
`workflows/{id}/operations/run-records/{timestamp}/`, instantiated from six templates:
`INPUTS.md`, `PROMPT_USED.md`, `OUTPUT_DRAFT.md`, `REVIEW.md`, `FINAL_OUTPUT.md`, and
`RUN_RECORD.md`. `RUN_RECORD.md` carries a YAML block conforming to
`run-record.schema.yaml` (timestamp, input/output hashes, success, reviewer sign-off,
anomalies).

A deterministic, model-free scaffolder `scripts/workflowctl.py run <id> --input <folder>`
backs the command exactly as `regenerate_index.py` backs `/regenerate-index`: it creates
the packet folder, copies the production prompt, hashes the inputs, and stubs the six
files. It never generates output, never reviews, and refuses to run a non-production
workflow. Output generation, review, and delivery stay operator-driven.

## Why

The library could classify a Funnel B request (via `/route-request`) but had no landing
command to actually run it — routing pointed at the manual runbook as a stopgap. This
makes a run a first-class, repeatable, evidence-producing operation while keeping the
human in the loop for generation, review, and delivery.

## Compatibility

Additive and backward compatible. No contract schema changed; no workflow contract
requires migration. The run-record schema gained only a clarifying location comment —
its fields are unchanged, and pre-v0.5 flat `{timestamp}.yaml` records remain valid
evidence. Every existing lifecycle command and script behaves exactly as before. Raw
input and output text for `internal`+ workflows is still never committed: hashes and the
review verdict are the committed evidence, and raw produced content lives in
`OUTPUT_DRAFT.local.md` / `FINAL_OUTPUT.local.md`, which `.gitignore` excludes (the
run-records ignore rule was widened to cover packet subfolders). Existing workflows are
not auto-migrated; they keep recording the methodology version they were built against,
per `methodology/CLAUDE.md`.
