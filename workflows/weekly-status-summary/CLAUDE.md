# Workflow: Weekly Status Summary — working rules

These rules activate when Claude Code is working inside this workflow's
directory. They layer on top of the root and methodology `CLAUDE.md` files.
Claude Code loads this file only when work is happening here, which is how
cross-workflow contamination is prevented — knowledge about this workflow stays
scoped to this directory.

## The contract governs
- `contract.yaml` in this directory is the single source of truth for this
  workflow. Read it before doing anything. Never change this workflow's behavior
  without first updating the contract.
- The production prompt, evals, and runbook **implement** the contract. If any of
  them disagrees with the contract, the contract wins and the artifact is wrong.

## Contract-first changes
- To change behavior: update `contract.yaml` first, record why in
  `logs/decisions.md`, then change `agent/` and `evals/` to match.
- Never modify the contract without recording the reason in `logs/decisions.md`.

## Session discipline
- End every session that touches this workflow with an entry in
  `logs/iteration-log.md`: what changed and what is next.

## Data handling
- Honor `max_sensitivity` and `data_handling` in the contract. No raw
  confidential or restricted data in committed files. Fixtures in `fixtures/`
  are sanitized or synthetic only. See
  `methodology/methods/sensitivity-policy.md`.

## Memory boundary
- Nothing about this workflow goes into auto memory. Requester preferences, data
  shapes, quality criteria, and decisions belong in `contract.yaml` or
  `logs/decisions.md`.

## Promotion
- This workflow cannot reach `production` until evals pass and a finished sample
  has been accepted (recorded in `logs/decisions.md`). See
  `methodology/methods/acceptance-review.md`.
