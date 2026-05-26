# Request routing method

The judgment behind `/route-request`. This is the library's *front door*: a thin,
advisory layer that classifies a raw incoming request into one of four funnels and
tells the operator exactly which small input set to ask the requester for. It runs
*before* intake and *before* `/scope`. It never mutates a workflow — it classifies
and prepares; the operator approves; the existing lifecycle commands do the work.

## The four funnels

| Funnel | Meaning | Lands on |
|---|---|---|
| **A — New Workflow** | A new recurring deliverable the library does not yet produce. | `/scope` (which still applies its own reject/defer/merge/one-off/create judgment) |
| **B — Existing Run** | A normal run of a production workflow with new data (optionally a one-time note for this run only). | `/run-workflow` (PR2) |
| **C — Revision** | A change to the *future* behavior of an existing workflow. | `/revise-workflow` |
| **D — One-Off Assist** | A genuinely valuable but non-recurring task. | Do it directly; do not create a workflow. |

## The decision tree

Top to bottom; first match wins.

```
START: a request arrives
│
├─ Q1. Does a PRODUCTION workflow already cover this deliverable?
│       (check portfolio/workflows.yaml for status: production)
│   │
│   ├─ YES ─ Q2. Is the requester asking to CHANGE future behavior of it
│   │            (format, audience, content rules, cadence, review/sensitivity)?
│   │        │
│   │        ├─ YES → FUNNEL C  (Workflow Revision → /revise-workflow)
│   │        │
│   │        └─ NO  ─ Q3. Are they just supplying new data for a normal run
│   │                     (maybe with one-time notes for THIS run only)?
│   │                 │
│   │                 ├─ YES → FUNNEL B  (Existing Run → /run-workflow)
│   │                 └─ NO  → clarify; likely C or a one-off
│   │
│   └─ NO ── Q4. Is the need RECURRING (will repeat on a schedule/trigger)?
│            │
│            ├─ YES → FUNNEL A  (New Workflow Intake → /scope, which may still
│            │                   return reject/defer/merge/one-off/create)
│            └─ NO  → FUNNEL D  (One-Off Assist → do directly, no workflow)
```

## The B-vs-C distinction (the critical one)

The litmus test is **scope of effect**:

- A change that affects **only this run** is a **Funnel B** run with a one-time
  note. Capture the note with the run inputs; **never** touch the contract.
- A change that affects **all future runs** is a **Funnel C** revision. Open it
  with `/revise-workflow`, contract-first.

When B-vs-C is genuinely ambiguous, **route to C** and say why. It is safer to open
a controlled, contract-first revision than to silently bake a one-time ask into a
contract — or to silently alter future behavior under cover of "just this run."

| Request | Funnel |
|---|---|
| "Here's this week's data, and just this once also add a Customer Wins section." | **B** (one-time note) |
| "From now on the weekly summary should include a Customer Wins section." | **C** (future change) |

## Routing is not scoping

Routing is the fast top-level switch; `/scope` is the deep judgment. For Funnel A,
routing only confirms "this looks like a new recurring need" and hands a populated
intake to `/scope`, which still applies its full five-activity method — including
the possibility of `reject`, `defer`, `merge`, or `one-off`. Routing never
pre-empts that verdict and never creates a workflow.

## Funnel → command mapping

| Funnel | Requester form to ask for | Next operator command |
|---|---|---|
| **A** | `methodology/templates/intake-template.md` (reused — no duplicate) | `/scope intakes/{id}` |
| **B** | `methodology/templates/workflow-run-input.md` | `/run-workflow {id} <input-folder>` (PR2) |
| **C** | `methodology/templates/workflow-revision-request.md` | `/revise-workflow {id}` |
| **D** | `methodology/templates/one-off-assist-request.md` | do directly — no workflow |

Everyone starts at the tiny universal `methodology/templates/front-door-request.md`
(~5 questions); the funnel-specific form is requested only if the front door leaves
required inputs missing.

## Worked examples

| Incoming request | Funnel | Why |
|---|---|---|
| "Every Friday I need a one-page summary of the team's status updates." | **A** | No production workflow yet; recurring. → `/scope`. |
| "Here are this week's three updates — can you do the Friday summary?" | **B** | `weekly-status-summary` is production; new data, normal run. |
| "Here's this week's data, and just this once also add a Customer Wins section." | **B** | Existing run + one-time note (change is for this run only). |
| "From now on the weekly summary should include a Customer Wins section." | **C** | Existing workflow; change to all future runs. → `/revise-workflow`. |
| "The weekly summary should go to the exec list instead of the team." | **C** | Future audience change. |
| "Can you draft a one-time board memo from these notes by Thursday?" | **D** | Not recurring; do it directly, no workflow. |
| "We keep needing ad-hoc competitive teardowns, roughly monthly." | **A** | Recurring → intake → `/scope` (which may decide merge/create). |

## Guardrails

1. Routing is **advisory and non-mutating**. It never creates, runs, revises, or
   promotes anything, and never writes inside `workflows/`.
2. It writes only three output files into the request folder:
   `recommended_funnel.md`, `missing_info.md`, `next_action.md`.
3. For B/C it must **confirm the target workflow is `status: production`** before
   recommending a run or revision. If the named workflow is not production (or does
   not exist), say so and route to the appropriate lifecycle step instead.
4. It respects sensitivity. If the request involves `confidential` or `restricted`
   data, flag the data-handling requirement and remind that raw content stays out
   of committed files, per `methodology/methods/sensitivity-policy.md`.
5. When B-vs-C is ambiguous, route to **C** and explain why.
6. Missing fields are never a blocker — routing still classifies, then lists what
   to request (same philosophy as `/scope`).
