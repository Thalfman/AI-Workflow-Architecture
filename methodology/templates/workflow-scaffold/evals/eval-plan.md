# Eval plan — {{WORKFLOW_NAME}}

How this workflow proves it meets its contract. Case structure:
`methodology/schemas/eval-case.schema.yaml`. Promotion gate:
`methodology/methods/acceptance-review.md`.

## What we test
<The behaviors and failure modes that matter here, derived from
`contract.acceptance_criteria` and `contract.definition_of_good`.>

## Cases
- `test-cases.yaml` — must pass for promotion.
- `regression-cases.yaml` — captured from past failures; must keep passing.

## Graders
<Which grader each case uses and why: `exact` for deterministic output,
`semantic` for close-match prose, `llm-judge` for rubric-scored quality.>

## Pass threshold
`contract.evals.pass_threshold` is the bar. The workflow cannot be promoted
unless cases pass at or above it.

## Fixtures
Inputs in `fixtures/source/`, expected outputs in `fixtures/expected/`. Sanitized
or synthetic only — never raw confidential or restricted data.
