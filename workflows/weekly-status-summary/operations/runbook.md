# Runbook — Weekly Status Summary

How to operate this workflow in production. Must be complete before promotion
(`methodology/methods/acceptance-review.md`, gate 4).

## Trigger
Scheduled weekly (see `operations/trigger.config.yaml`, which mirrors
`contract.trigger`): every Friday afternoon, once contributors have posted their
individual updates.

## Run steps
Run this workflow with `/run-workflow weekly-status-summary <input-folder>`
(`methodology/commands/run-workflow.md`). It produces an auditable run packet under
`operations/run-records/{timestamp}/` from the templates in
`methodology/templates/run-packet/`. The steps it follows:
1. Gather that week's contributor updates (`contract.inputs[]`) into the input folder.
2. Scaffold the packet — deterministically via
   `python scripts/workflowctl.py run weekly-status-summary --input <input-folder>`,
   which copies the prompt into `PROMPT_USED.md`, hashes the inputs into `INPUTS.md`,
   and stubs `RUN_RECORD.md`. (No script generates the summary.)
3. Run `agent/production.prompt.md` over the updates to produce the summary into
   `OUTPUT_DRAFT.local.md` (`internal` content is gitignored, not committed).
4. Run `agent/reviewer.prompt.md` and capture the verdict in `REVIEW.md`
   (`contract.human_review.required` is true; review point is `pre_send`).
5. If approved, write `FINAL_OUTPUT.local.md` and deliver the summary to Delivery
   leadership and stakeholders (`contract.outputs[].audience`).
6. Complete `RUN_RECORD.md` (`methodology/schemas/run-record.schema.yaml`) — hashes of
   inputs/outputs and the reviewer sign-off, not the raw text.

## Failure handling
- Reviewer returns `rejected`: do not send. Fix the summary and re-review; if the
  fault is in the prompt, open a revision with `/revise-workflow` (contract-first).
- A contributor update is missing: note the gap in the summary; do not delay the
  whole report for one missing update unless leadership needs it.
- Evals fail after a change: stop. The workflow may not be sent or re-promoted until
  `scripts/run_evals.py weekly-status-summary` passes at threshold again.

## Data handling
Honor `contract.max_sensitivity` (internal) and `contract.data_handling`. Raw inputs
are not committed; record hashes in the run record. Strip personal data (emails,
signatures, handles) from the output. See
`methodology/methods/sensitivity-policy.md`.
