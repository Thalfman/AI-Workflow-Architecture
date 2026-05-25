# Reviewer prompt — {{WORKFLOW_NAME}}

Check a production output before it reaches the audience. The contract is the
standard — review against it, not against taste.

## What you are reviewing
<The deliverable produced by `agent/production.prompt.md`.>

## Checklist (from the contract)
- Meets every item in `contract.acceptance_criteria`.
- Output format matches `contract.outputs[].format` and `success_criteria`.
- Respects `contract.max_sensitivity` and `contract.data_handling`; no raw
  sensitive data leaked.
- Satisfies `contract.definition_of_good`.

## Verdict
Return one of `approved`, `approved_with_edits`, or `rejected`, with specific
reasons tied to the checklist. When `contract.human_review.required` is true,
this verdict becomes `reviewer_signoff.decision` in the run record
(`methodology/schemas/run-record.schema.yaml`).
