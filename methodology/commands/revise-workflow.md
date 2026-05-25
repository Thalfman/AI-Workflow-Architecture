---
description: Open a workflow for revision, contract-first.
argument-hint: <workflow_id> [reason]
---

# /revise-workflow

Open a production (or building) workflow for revision.

**Arguments:** `$1` — the `workflow_id`. Remaining text — the reason for revision.

## Steps

1. Set `status: revising` and update `last_revised` in
   `workflows/$1/contract.yaml`.
2. Record the reason for revision as a dated entry in
   `workflows/$1/logs/decisions.md`: what triggered it and the intended change.
3. Append a matching entry to `workflows/$1/logs/iteration-log.md`.
4. Run `/regenerate-index`.

## The contract-first rule

After this command, **the contract must be updated before any prompt or eval
change is made.** Behavior is defined by the contract; the prompt and evals
implement it. Remind the operator of this and do not edit
`agent/*.prompt.md` or `evals/*` until the contract reflects the intended new
behavior.

## Outputs

- Contract at `status: revising`.
- A decisions-log entry capturing the reason.
- Updated iteration log and `portfolio/workflows.yaml`.

## Notes

- Promote back to production with `/promote-workflow` once evals pass again and
  a fresh sample is accepted.
- Commit with the `workflow-$1:` prefix.
