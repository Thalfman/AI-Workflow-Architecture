# Acceptance review

The criteria and process for accepting a workflow as ready for promotion to
production. `/promote-workflow` enforces this; this document is the authority for
what "ready" means.

## The four gates

A workflow may move to `production` only when all four hold:

1. **Evals pass.** Test and regression cases
   (`evals/test-cases.yaml`, `evals/regression-cases.yaml`) pass at or above the
   contract's `evals.pass_threshold`. Regression cases exist to catch behavior
   that previously broke; they are not optional.
2. **Requester sample acceptance.** The requester has reviewed a finished sample
   produced by the workflow and accepted it. This is recorded as a dated entry in
   `logs/decisions.md` naming who accepted and what they saw. Evals prove
   internal consistency; sample acceptance proves the deliverable is what the
   requester actually wanted.
3. **Sensitivity verified.** The contract's `max_sensitivity` and each
   `inputs[].sensitivity` are confirmed against
   `methodology/methods/sensitivity-policy.md`, and the `data_handling` plan is
   consistent with them.
4. **Runbook complete.** `operations/runbook.md` describes how to trigger, run,
   review, and recover the workflow well enough for the operator to run it
   without reconstructing context.

## Process

1. Run the evals; capture the result.
2. Confirm the sample-acceptance entry exists in `logs/decisions.md`.
3. Verify sensitivity and data handling.
4. Confirm the runbook is complete.
5. If all four pass, run `/promote-workflow {id}`. If any fail, stop and report
   which gate failed — promotion is all-or-nothing.

## Re-promotion after revision
A workflow returning from `revising` clears the same four gates. A fresh sample
acceptance is required; a prior acceptance does not carry over a behavior change.
