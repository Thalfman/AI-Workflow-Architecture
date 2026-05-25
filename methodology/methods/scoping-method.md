# Scoping method

The judgment behind `/scope`. The intake gate is explicit: not every request
becomes a workflow. This method takes a filled intake and produces a
recommendation — **reject, defer, merge, one-off, or create** — with reasoning.

## The five activities

### 1. Parse the intake against the schema
Read the submission against `methodology/schemas/intake.schema.md`. Confirm every
required field is present. Missing required fields are not a reject — they are a
request for more information, surfaced in `scoping-reply.md`.

### 2. Classify by recurrence, complexity, and sensitivity
- **Recurrence** — one-off, irregular, or scheduled/recurring? Recurrence is the
  primary signal that a workflow (not a one-off) is warranted.
- **Complexity** — how many inputs, decision points, and quality dimensions? High
  complexity raises the bar for inputs and evals but does not block creation.
- **Sensitivity** — the most sensitive input, per
  `methodology/methods/sensitivity-policy.md`. Restricted data demands a data
  handling plan before any build.

### 3. Compare against existing workflows for merge candidates
Read `workflows/*/contract.yaml`. If an existing workflow already produces a
substantially similar deliverable for a similar audience, prefer **merge** over a
new directory. Cross-workflow contamination is avoided by not creating
near-duplicates.

### 4. Draft a contract from the intake content
Populate a `draft-contract.yaml` per `methodology/schemas/contract.schema.yaml`
as far as the intake allows. Map intake fields to contract fields: task →
`definition_of_good`, trigger → `trigger`, inputs/outputs directly, definition of
good → `acceptance_criteria` candidates, sensitivity → `max_sensitivity`. Leave
genuine unknowns as `null` with a `# TODO`.

### 5. Produce a recommendation with reasoning

| Recommendation | When |
|---|---|
| **reject** | Not a fit: not recurring, out of remit, or value does not justify a governed workflow. |
| **defer** | Worth doing, not now: missing inputs, unclear value, or blocked on a dependency. |
| **merge** | An existing workflow can absorb this with minor revision. Name the target. |
| **one-off** | Genuinely valuable but non-recurring. Do the work directly; do not create a workflow. |
| **create** | Recurring, scoped, and distinct. Propose a `workflow_id` slug. |

State one paragraph of reasoning. Only **create** leads to a workflow directory,
and only via `/new-workflow` after the operator approves.

## Output contract
`/scope` writes `scoping-reply.md`, `draft-contract.yaml`, and the recommendation
line into the intake folder. The intake folder is the durable record of the
decision.
