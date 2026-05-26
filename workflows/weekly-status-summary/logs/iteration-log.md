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
