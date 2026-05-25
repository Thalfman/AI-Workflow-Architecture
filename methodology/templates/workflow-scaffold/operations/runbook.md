# Runbook — {{WORKFLOW_NAME}}

How to operate this workflow in production. Must be complete before promotion
(`methodology/methods/acceptance-review.md`, gate 4).

## Trigger
<How a run starts, matching `operations/trigger.config.yaml` and
`contract.trigger`.>

## Run steps
1. Gather inputs (`contract.inputs[]`).
2. Run the production prompt (`agent/production.prompt.md`).
3. If `contract.human_review.required` is true, run `agent/reviewer.prompt.md`
   and capture the verdict.
4. Deliver the output to `contract.outputs[].audience`.
5. Write a run record to `operations/run-records/{timestamp}.yaml`
   (`methodology/schemas/run-record.schema.yaml`).

## Failure handling
<What to do when a run fails or a review rejects: retries, fallbacks, who to
notify, when to halt the workflow.>

## Data handling
Honor `contract.max_sensitivity` and `contract.data_handling`. Raw inputs are not
committed; record hashes in the run record. See
`methodology/methods/sensitivity-policy.md`.
