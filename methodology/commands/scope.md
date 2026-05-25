---
description: Scope an intake folder and produce a reply, draft contract, and recommendation.
argument-hint: <path-to-intake-folder>
---

# /scope

Run the scoping methodology against an intake folder and decide whether it
should become a workflow.

**Argument:** `$ARGUMENTS` — path to an intake folder (e.g. `intakes/2026-05-acme-status`).

## Steps

1. Read the filled intake at `$ARGUMENTS` against
   `methodology/schemas/intake.schema.md`. Note any missing required fields.
2. Read any attached example artifacts in the intake folder.
3. Apply the five-activity scoping method documented in
   `methodology/methods/scoping-method.md`:
   1. Parse the intake against the schema.
   2. Classify by recurrence, complexity, and sensitivity.
   3. Compare against existing `workflows/*/contract.yaml` for merge candidates.
      If no workflows exist yet (the glob matches nothing), record "no merge
      candidates" and continue — an empty library is normal early on.
   4. Draft a contract from the intake content.
   5. Produce a recommendation with reasoning.
4. If the recommendation is `create`, propose a `workflow_id` slug (lowercase,
   hyphenated, derived from the deliverable — e.g. `weekly-status-report`).

## Outputs

Write all three into the intake folder (`$ARGUMENTS`):

- `scoping-reply.md` — a plain-language reply to send the requester: what you
  understood, the recommendation, and any questions or missing inputs.
- `draft-contract.yaml` — a draft conforming to
  `methodology/schemas/contract.schema.yaml`, `status: scoping`, populated as
  far as the intake allows. Leave unknowns as `null` with a `# TODO` note.
- `recommendation.md` — the verdict as its own auditable artifact. Its first line
  is exactly one of: **reject | defer | merge | one-off | create**, followed by
  one paragraph of reasoning. If `merge`, name the target workflow. If `create`,
  include the proposed `workflow_id`. (`scoping-reply.md` restates this for the
  requester; `recommendation.md` is the record automation reads.)

## Notes

- Do not create a workflow directory here. `create` is a recommendation only;
  `/new-workflow` performs the creation after the operator approves.
- Record the scoping outcome so it is auditable; the intake folder is the record.
