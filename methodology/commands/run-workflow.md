---
description: Execute one production run of a workflow and record it as a run packet.
argument-hint: <workflow_id> <path-to-input-folder>
---

# /run-workflow

Perform a single production run of an existing workflow over new inputs and capture
it as an auditable run packet. This is the landing command for **Funnel B** in
`methodology/methods/request-routing.md` (a normal run with new data, optionally a
one-time note for this run only). It never changes the workflow's behavior — a change
to all future runs is a Funnel C revision (`/revise-workflow`), not a run.

**Arguments:** `$1` — the `workflow_id`. `$2` — path to a folder holding this run's
inputs (the files from `methodology/templates/workflow-run-input.md`, e.g. under
`intakes/{id}/raw/` or a local working folder).

## Preconditions

- `workflows/$1/contract.yaml` must exist and be at `status: production`. A workflow
  that is not in production cannot be run — stop and report its status, and route to
  the appropriate lifecycle step (`/scope`, `/promote-workflow`, `/revise-workflow`)
  instead. (This mirrors the routing guardrail: **B requires production**.)
- `$2` must exist and contain at least one input file.

## Files read

- `workflows/$1/contract.yaml` — the source of truth for inputs, outputs, review, and
  sensitivity.
- `workflows/$1/agent/production.prompt.md` and `agent/reviewer.prompt.md`.
- The input files at `$2`.
- `methodology/templates/run-packet/*` — the six packet templates.
- `methodology/schemas/run-record.schema.yaml` — the record the packet must satisfy.
- `methodology/methods/sensitivity-policy.md` — the data-handling rules.

## Steps

1. **Confirm production.** Read the contract; if `status` is not `production`, stop
   and report (see Preconditions).
2. **Scaffold the packet.** Create `workflows/$1/operations/run-records/{timestamp}/`
   and instantiate the six templates into it. The deterministic, model-free part of
   this step is the executable backbone `scripts/workflowctl.py run $1 --input $2`,
   which creates the folder, copies the production prompt into `PROMPT_USED.md`,
   hashes the inputs into `INPUTS.md`, and stubs `RUN_RECORD.md` with the timestamp
   and input hash. Running the script is optional; the packet may also be assembled
   by hand from the templates. **No script ever generates the output.**
3. **Generate the draft.** Run `agent/production.prompt.md` over the inputs and write
   `OUTPUT_DRAFT.md`. If `contract.max_sensitivity` is `internal` or higher, save it
   as `OUTPUT_DRAFT.local.md` so the raw content is gitignored.
4. **Review.** Run `agent/reviewer.prompt.md` against the draft and record the verdict
   in `REVIEW.md` (`approved | approved_with_edits | rejected`, with reasons tied to
   the checklist). Honor `contract.human_review`.
5. **Finalize.** If approved (with or without edits), produce the delivered output as
   `FINAL_OUTPUT.md` (or `FINAL_OUTPUT.local.md` for `internal`+ data). If rejected,
   do not deliver; fix and re-review, or open a revision if the prompt is at fault.
6. **Record.** Fill `RUN_RECORD.md` so its YAML block satisfies
   `run-record.schema.yaml`: `timestamp`, `input_hash`, `output_hash`, `success`,
   `reviewer_signoff` (when review is required), and `anomalies`.
7. **Deliver.** The operator sends `FINAL_OUTPUT` to the requester. Delivery is a
   human-approved step — routing and scaffolding never send anything.

## Outputs

A run packet at `workflows/$1/operations/run-records/{timestamp}/` containing the six
files: `INPUTS.md`, `PROMPT_USED.md`, `OUTPUT_DRAFT(.local).md`, `REVIEW.md`,
`FINAL_OUTPUT(.local).md`, and `RUN_RECORD.md`. The committed evidence is the
hash/sign-off files; raw produced content stays in the `.local.md` files.

## Guardrails

1. **A run never changes the contract.** A one-time ask goes in `INPUTS.md` under
   "one-time notes". A change to future behavior is Funnel C — stop and use
   `/revise-workflow`. When it is ambiguous whether an ask is one-time or permanent,
   treat it as a revision (route to C), per `request-routing.md`.
2. **Production only.** Refuse to run a non-production workflow.
3. **Human review gates delivery.** When `contract.human_review.required` is true, a
   recorded reviewer sign-off is required before delivery; a `rejected` verdict means
   do not send.
4. **Sensitivity.** Honor `contract.max_sensitivity` and `data_handling`. Raw input
   and output text for `internal`+ workflows is never committed — only hashes (in
   `INPUTS.md`/`RUN_RECORD.md`) and the review verdict are. Raw content lives in
   `.local.md` files (`methodology/methods/sensitivity-policy.md`).

## Notes

- Commit run artifacts with the `workflow-$1:` prefix. End the session with an entry
  in `workflows/$1/logs/iteration-log.md`.
- The run packet is append-only evidence — do not edit a packet after the run except
  to fill the fields the run produced.
