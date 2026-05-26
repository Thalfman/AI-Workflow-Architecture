# Reviewer prompt — Weekly Status Summary

Check a production output before it reaches leadership. The contract is the
standard — review against it, not against taste.

## What you are reviewing
A weekly status summary produced by `agent/production.prompt.md` from that week's
contributor updates.

## Checklist (from the contract)
- The three required sections are present and in order: Highlights, Risks & Blockers, Next Week.
- Every contributor who submitted an update is represented; missing updates are
  noted as gaps, not fabricated.
- Length is within the one-page budget (<= 350 words).
- No raw personal or confidential data: no email addresses, handles, signatures, or
  compensation figures (`contract.max_sensitivity: internal`).
- The summary is accurate to the inputs — no invented progress — and synthesizes
  themes rather than copying bullets (`contract.definition_of_good`).

## Verdict
Return one of `approved`, `approved_with_edits`, or `rejected`, with specific
reasons tied to the checklist. Because `contract.human_review.required` is true,
this verdict becomes `reviewer_signoff.decision` in the run record
(`methodology/schemas/run-record.schema.yaml`).
