# Eval plan — Weekly Status Summary

How this workflow proves it meets its contract. Case structure:
`methodology/schemas/eval-case.schema.yaml`. Promotion gate:
`methodology/methods/acceptance-review.md`.

## What we test
The properties a stakeholder summary must hold, drawn from
`contract.acceptance_criteria` and `contract.definition_of_good`:
- the three required sections are present,
- every contributor is represented,
- the summary stays within the length budget,
- no raw personal or confidential data leaks.

## Cases
- `test-cases.yaml` — three cases that must pass for promotion (pass_threshold 1.0).
- `regression-cases.yaml` — guards a past failure (a contributor's email signature
  leaked into the summary); must keep passing.

## Graders
All cases use the `structural` grader: deterministic, offline, machine-checkable
assertions about the committed sample output (`fixtures/expected/week-2026-05-18.md`).
No model call is required, so the evals run in CI. Quality judgments that need a
model (tone, synthesis quality) are left to the human reviewer at `pre_send`.

## Pass threshold
`contract.evals.pass_threshold` is 1.0 — every case must pass before promotion.

## Fixtures
Inputs in `fixtures/source/`, the accepted sample output in `fixtures/expected/`.
Synthetic only — the source updates even contain a fake email signature to prove
the summary strips it.
