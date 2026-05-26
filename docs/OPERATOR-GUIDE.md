# Operator Guide — the front door

The day-to-day playbook for the sole operator. A request just arrived. What do you
do? This guide turns a raw message into the right command, without you having to
remember the whole lifecycle. The judgment behind it lives in
`methodology/methods/request-routing.md`; the command is `/route-request`.

## A request arrived — what do I do?

1. **Capture it.** Create `intakes/{id}/` and put the requester's raw message and any
   attachments under `intakes/{id}/raw/` — that subfolder is gitignored, so
   potentially sensitive content never lands in a tracked path before it has been
   sanitized. If they haven't sent anything structured, send them the front door
   (`methodology/templates/front-door-request.md`) — about five questions; see
   `docs/PROMPT-CARDS.md` for a copy-paste version.
2. **Route it.** Run `/route-request intakes/{id}`. It classifies the request into
   funnel **A**, **B**, **C**, or **D** and writes three files into the folder:
   - `recommended_funnel.md` — the funnel (first line is `A`/`B`/`C`/`D`) + reasoning.
   - `missing_info.md` — exactly what to ask the requester for next, naming the form.
   - `next_action.md` — the exact next command to run.
3. **Read the three outputs.** They tell you the funnel, what (if anything) is
   missing, and your next move.
4. **Ask for the right form (only if needed).** If `missing_info.md` lists gaps,
   send the requester the matching form (and only that form) from
   `docs/PROMPT-CARDS.md`.
5. **Dispatch by funnel** using the cheat sheet below.

Routing is advisory — it never changes a workflow. You approve; the lifecycle
commands do the work.

## Funnel → command cheat sheet

| Funnel | Means | Ask requester for | Then run |
|---|---|---|---|
| **A — New Workflow** | A new recurring deliverable we don't produce yet. | `methodology/templates/intake-template.md` | `/scope intakes/{id}` |
| **B — Existing Run** | A normal run of a production workflow with new data. | `methodology/templates/workflow-run-input.md` | `/run-workflow {id} <input-folder>` *(PR2; until it ships, run manually per `workflows/{id}/operations/runbook.md`)* |
| **C — Revision** | A change to a workflow's future behavior. | `methodology/templates/workflow-revision-request.md` | `/revise-workflow {id}` |
| **D — One-Off** | A valuable non-recurring task. | `methodology/templates/one-off-assist-request.md` | do it directly — no workflow |

## The one distinction that matters: B vs C

The litmus test is **scope of effect**:

- *This run only* → **B**. Capture the ask as a one-time note with the run inputs.
  **Never** touch the contract.
- *All future runs* → **C**. Open a contract-first revision with `/revise-workflow`.

When it's genuinely ambiguous, route to **C** — it's safer to open a controlled
revision than to silently bake a one-time ask into the contract.

## Worked cases — one per funnel

**Funnel A — new recurring need.**
> "Every Friday I need a one-page summary of the team's status updates."

No production workflow covers this yet, and it recurs. Routing returns **A**. Ask
for the full `intake-template.md`, then run `/scope intakes/{id}` — which applies its
own judgment and may still say `merge`, `defer`, or `create`.

**Funnel B — normal run of an existing workflow.**
> "Here are this week's three updates — can you do the Friday summary?"

`weekly-status-summary` is in production; this is just new data. Routing returns
**B**. Ask for `workflow-run-input.md` if the inputs aren't already attached, then
run `/run-workflow weekly-status-summary <input-folder>` (PR2). Until `/run-workflow`
ships, perform the run manually following
`workflows/weekly-status-summary/operations/runbook.md`.
> "Here's this week's data, and just this once also add a Customer Wins section."

Still **B** — the extra section is a one-time note for *this run only*. Record it
with the run inputs; do not change the contract.

**Funnel C — change future behavior.**
> "From now on the weekly summary should include a Customer Wins section."
> "The weekly summary should go to the exec list instead of the team."

Both change *all future runs* of a production workflow. Routing returns **C**. Ask
for `workflow-revision-request.md`, then run `/revise-workflow weekly-status-summary`
and let the contract-first flow decide.

**Funnel D — one-off.**
> "Can you draft a one-time board memo from these notes by Thursday?"

Valuable but not recurring. Routing returns **D**. Ask for
`one-off-assist-request.md` if needed, then just do the work — do not create a
workflow.

## A note on sensitivity

If a request involves `confidential` or `restricted` data, routing flags it. Keep
raw content out of committed files: raw intake material lives in the gitignored
`intakes/{id}/raw/`, and sensitive run content stays in `*.local.md` /
`*.local.yaml`. The rules are in `methodology/methods/sensitivity-policy.md`.
