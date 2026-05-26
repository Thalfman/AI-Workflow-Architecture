# Decisions — Weekly Status Summary

The durable record of decisions for this workflow: contract changes (with
reasons), sample acceptance, and trade-offs. The contract is the source of truth;
this log explains *why* it looks the way it does.

## Decision log

### 2026-05-26 — Initial contract and build
- Decision: Defined the workflow as a weekly roll-up of individual contributor
  updates into one stakeholder summary with three fixed sections (Highlights,
  Risks & Blockers, Next Week), at `internal` sensitivity, with required pre-send
  human review.
- Reason: This is the recurring deliverable the workflow exists to produce. Fixed
  sections make the output predictable for stakeholders and machine-checkable for
  evals.
- Effect: Wrote `contract.yaml` first, then the production/reviewer prompts,
  synthetic fixtures, and structural eval cases to implement it (contract-first rule).

### 2026-05-26 — Structural, offline evals
- Decision: Grade this workflow with `structural` eval cases only.
- Reason: The library evaluates offline and deterministically. Section presence,
  contributor coverage, length budget, and PII exclusion are all checkable without
  a model. Tone and synthesis quality are left to the human reviewer at `pre_send`.
- Effect: All cases in `evals/test-cases.yaml` and `evals/regression-cases.yaml`
  use `grader: structural`. This workflow is built against methodology v0.2, which
  added that grader.

### 2026-05-26 — Status: building -> in_review
- Decision: Moved the contract from `status: building` to `status: in_review`.
- Reason: All build artifacts are complete — production and reviewer prompts,
  synthetic fixtures, the accepted sample output, structural eval cases, the
  runbook, and the trigger config — so the workflow is ready for promotion-gate
  testing. No lifecycle command performs this transition, so the contract was
  updated directly.
- Effect: `status: in_review` in `contract.yaml`; recorded here and in the
  iteration log.

## Sample acceptance (required for promotion)

Promotion to production requires a dated entry here recording that a finished
sample was accepted (`methodology/methods/acceptance-review.md`,
`/promote-workflow` precondition 2). For this synthetic reference workflow,
acceptance is recorded as operator/reference acceptance — there is no external
requester.

### 2026-05-26 — sample accepted by operator (reference acceptance)
- Accepted by: AI Workflow Architect (operator), standing in for the synthetic
  requester. This is operator/reference acceptance, not requester acceptance —
  there is no external requester for this reference workflow.
- Sample reviewed: `fixtures/expected/week-2026-05-18.md`, the summary produced
  from the three synthetic contributor updates in `fixtures/source/`.
- Verdict: accepted.
- Notes: The sample meets `contract.definition_of_good` and all four
  `acceptance_criteria`; structural evals pass at threshold 1.0. Approved for
  promoting this reference workflow to production. Real workflows require
  requester or owner acceptance, not operator sign-off.
