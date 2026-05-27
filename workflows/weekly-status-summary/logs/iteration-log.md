# Iteration log — Weekly Status Summary

Append-only. Every session that touches this workflow ends with an entry here:
what changed and what is next. Newest entries at the bottom.

## 2026-05-26 — created
- Created from `methodology/templates/workflow-scaffold/` at methodology version `v0.2`.
- Source intake: n/a (reference workflow stood up to prove the lifecycle end to end).
- Status: `building`.
- Next: draft `agent/production.prompt.md` and the first eval cases.

## 2026-05-26 — built and moved to in_review
- Wrote the contract first, then the production and reviewer prompts, three
  synthetic contributor fixtures (one with a fake email signature), the accepted
  sample output, three structural test cases, one regression case, the runbook,
  and the schedule trigger config.
- Moved `status` from `building` to `in_review`: all build artifacts are complete
  and ready for promotion-gate testing.
- Next: run the eval runner and the promotion-gate checker, record operator
  acceptance, then `/promote-workflow`.

## 2026-05-26 — promoted to production
- Ran `scripts/run_evals.py weekly-status-summary`: 4/4 gradable cases passed
  (rate 1.00 vs threshold 1.0) — tc-001/002/003 and regression rc-001.
- All four promotion gates passed (`scripts/check_promotion_gate.py`): evals,
  sample acceptance, sensitivity, and runbook.
- Sample acceptance: operator/reference acceptance recorded 2026-05-26 in
  `logs/decisions.md`.
- Moved `status` from `in_review` to `production` and regenerated the portfolio index.
- Next: operate on the weekly schedule; revise with `/revise-workflow` if the
  deliverable needs to change (contract-first).

## 2026-05-26 — runbook updated for /run-workflow (methodology v0.5)
- Updated `operations/runbook.md` Run steps to operate via the new
  `/run-workflow weekly-status-summary <input-folder>` command, which produces a run
  packet under `operations/run-records/{timestamp}/` from the methodology run-packet
  templates. Operational doc only — the contract is unchanged.
- Verified `scripts/workflowctl.py run weekly-status-summary --input fixtures/source`
  scaffolds a complete six-file packet (prompt copied, inputs hashed, record stubbed);
  the demo packet was not committed (run-records hold real runs only). Raw content
  files (`OUTPUT_DRAFT.local.md`, `FINAL_OUTPUT.local.md`) stay gitignored.
- Next: operate weekly via `/run-workflow`; capture one-time asks as run notes, not
  contract changes.

## 2026-05-27 — closed the feedback loop (3 runs + metrics rollup + feedback review)
- Operated the workflow over three synthetic weeks (weeks of 2026-04-27, 05-04, 05-11)
  via the `/run-workflow` backbone, producing the first real run packets under
  `operations/run-records/` (verdicts: 2 approved, 1 approved_with_edits). These are a
  synthetic backfill to bootstrap the metric. Raw inputs and produced text stayed
  local/gitignored; only hashes and verdicts were committed.
- Added `scripts/rollup_metrics.py` and ran it: it measured the clean-send rate at
  0.6667 (2/3) against the `>= 0.9` target, wrote it into
  `contract.success_metric.current_value` (was `null`), and appended the first
  `portfolio/value-ledger.yaml` entry. Value is derived from run records, never typed.
- Added the `methodology/methods/feedback-review.md` ritual and bumped methodology to
  v0.7. This workflow stays recorded at `methodology_version: v0.2` — not auto-migrated.
- Next: at 0.6667 the metric is below the 0.9 target on a 3-run sample. On the next
  feedback review, watch whether `approved_with_edits` recurs (the invented-progress
  near-miss in the 05-04 run); if it does, open a contract-first `/revise-workflow` to
  tighten the production prompt's accuracy guard.
