---
description: Promote a workflow to production after evals pass and the sample is accepted.
argument-hint: <workflow_id>
---

# /promote-workflow

Promote a workflow from `building` or `revising` to `production`.

**Argument:** `$1` — the `workflow_id`.

## Preconditions (the promotion gate)

Apply `methodology/methods/acceptance-review.md`. All must hold:

1. Eval cases pass at or above the contract's `evals.pass_threshold`
   (`workflows/$1/evals/test-cases.yaml` and `regression-cases.yaml`).
2. The requester has accepted a finished sample, recorded as a dated entry in
   `workflows/$1/logs/decisions.md`.
3. The sensitivity classification in the contract is verified against
   `methodology/methods/sensitivity-policy.md`.
4. `workflows/$1/operations/runbook.md` is complete enough to operate the
   workflow.

If any precondition fails, stop and report which one — do not promote.

## Steps

1. Set `status: production` and update `last_revised` in
   `workflows/$1/contract.yaml`.
2. Append an entry to `workflows/$1/logs/iteration-log.md`: what passed, the
   eval result, and the sample-acceptance reference.
3. Run `/regenerate-index`.

## Outputs

- Contract at `status: production`.
- Updated iteration log and `portfolio/workflows.yaml`.

## Notes

- Commit with the `workflow-$1:` prefix.
