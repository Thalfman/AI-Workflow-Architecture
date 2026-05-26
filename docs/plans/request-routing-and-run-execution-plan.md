# Request Routing & Run Execution — Improvement Plan

## Context

The repo already governs the *lifecycle* of a workflow well: intake → `/scope`
→ `/new-workflow` → build → evals → `/promote-workflow`, plus `/revise-workflow`,
`/retire-workflow`, `/regenerate-index`, validation scripts, CI, and one
production reference workflow (`weekly-status-summary`).

What it does **not** yet have is a *front door*. Today every request — whether
it's a brand-new recurring need, "here's this week's data, run the usual thing,"
"change how the summary reads from now on," or "just do this one thing for me" —
enters through the same heavyweight intake form and the same `/scope` command.
For the sole operator that means manually deciding what kind of request each
message is, and asking the requester for the right inputs by hand every time.

This plan adds a thin routing layer that classifies an incoming request into one
of four funnels and tells the operator exactly which (small) input set to ask
for — without requesters needing to understand the repo, lifecycle, or commands.
It also plans the eventual `/run-workflow` execution path as a separate, later PR.

---

## 1. Direct recommendation

**Split into two PRs.**

- **PR1 — Request Routing (the next PR).** Pure documentation plus one command
  spec and a set of requester templates. No scripts, no schema changes, no eval
  changes. CI stays green by construction. It directly solves the stated #1
  problem ("which kind of request is this, and what do I need from the
  requester?") and is shippable in a single small review.
- **PR2 — Run Execution (the PR after).** The `/run-workflow` command, the
  run-packet templates, and (optionally) a deterministic `scripts/workflowctl.py`
  scaffolder. This is heavier: it touches data-handling/sensitivity, adds a
  permission entry, defines an on-disk run-packet structure, and is best
  validated against the production reference workflow.

**Why not one PR / the other options:**
- *Routing + lightweight run packet* couples a zero-risk docs change to
  run-packet design decisions, enlarging the review surface for no real speed-up.
- *Routing only* (with run execution deferred indefinitely) under-serves
  day-to-day use; Funnel B has no landing command. So PR2 is planned now, just
  shipped second.
- *Run execution only* skips the actual triage problem the operator asked to
  solve first.

The two PRs are independently valuable and independently reviewable. PR1 unblocks
classification immediately; PR2 makes Funnel B executable.

---

## 2. Current-state assessment

| Concern | How the repo handles it today |
|---|---|
| **Intake** | Requester fills the full `methodology/templates/intake-template.md` (9 required fields) and the operator drops it in a folder under `intakes/`. One form for everything. |
| **Scoping** | `/scope <intake-folder>` runs the 5-activity `scoping-method.md` and writes `scoping-reply.md`, `draft-contract.yaml`, `recommendation.md`. First line of the recommendation is `reject \| defer \| merge \| one-off \| create`. **This already triages one-off vs. workflow.** |
| **Workflow creation** | `/new-workflow <id> <draft-contract>` stamps `workflows/{id}/` from the scaffold at `status: building`, then `/regenerate-index`. |
| **Workflow runs** | **No command exists.** The reference workflow's `operations/runbook.md` describes a manual 5-step run (gather inputs → production prompt → reviewer prompt → deliver → write `operations/run-records/{timestamp}.yaml`). Run records are hashes-only per `run-record.schema.yaml`; `.gitignore` already reserves `*.local.yaml` and `*.local.md` for sensitive local content. |
| **Revisions** | `/revise-workflow <id>` sets `status: revising`, logs the reason in `logs/decisions.md`, re-indexes. Contract-first: contract changes before prompt/evals. |
| **One-off requests** | Recognized only as a `/scope` verdict (`one-off` = "do the work directly; do not create a workflow"). No dedicated capture form or entry path — it still goes through the full intake form first. |

**Gap:** there is no step *before* intake that decides which of these paths a raw
request belongs to, and no lightweight per-path input capture. The operator is
the router today.

---

## 3. Target operating model

The intended operator experience, request received → output delivered:

1. **Requester sends a request** (email/message/files), or fills the tiny
   universal front-door form (`front-door-request.md`, ~5 questions).
2. **Operator drops it** into `intakes/{id}/` and runs `/route-request intakes/{id}`.
3. **The repo classifies** the request into Funnel A/B/C/D and writes
   `recommended_funnel.md`, `missing_info.md`, `next_action.md` into that folder.
4. **The repo tells the operator what's missing** — exactly which small input set
   to request, by pointing at the matching requester template (not the full form).
5. **Dispatch by funnel:**
   - **A (new workflow):** the folder is already an intake; run `/scope` → (its own
     reject/defer/merge/one-off/create judgment) → `/new-workflow` on `create`.
   - **B (existing run):** `/run-workflow <id> <input-folder>` (PR2) produces a run packet.
   - **C (revision):** `/revise-workflow <id>` opens a contract-first revision.
   - **D (one-off):** do the work directly; **do not** create a workflow.
6. **Operator delivers the finished output** to the requester (the operator is the
   only one who ever touches the repo).

Routing is advisory and never mutating: it classifies and prepares, the operator
approves, and the existing lifecycle commands do the actual work.

---

## 4. Funnel routing logic

Decision tree (top to bottom; first match wins):

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

**Critical distinction (B vs C):** a change that affects **only this run** is a
Funnel B run with a one-time note. A change that affects **all future runs** is a
Funnel C revision. When ambiguous, route to C and let the contract-first flow
decide — never silently bake a one-time ask into the contract.

**Routing does not replace `/scope`.** For Funnel A, routing only confirms "this
looks like a new recurring need" and hands a populated intake to `/scope`, which
still applies its full judgment (including possibly `one-off`, `merge`, `defer`,
`reject`). Routing is the fast top-level switch; `/scope` is the deep judgment.

### Worked examples

| Incoming request | Funnel | Why |
|---|---|---|
| "Every Friday I need a one-page summary of the team's status updates." | **A** | No production workflow yet; recurring. → `/scope`. |
| "Here are this week's three updates — can you do the Friday summary?" | **B** | `weekly-status-summary` is production; new data, normal run. |
| "Here's this week's data, and just this once also add a Customer Wins section." | **B** | Existing run + one-time note (change is for this run only). |
| "From now on the weekly summary should include a Customer Wins section." | **C** | Existing workflow; change to all future runs. → `/revise-workflow`. |
| "The weekly summary should go to the exec list instead of the team." | **C** | Future audience change. |
| "Can you draft a one-time board memo from these notes by Thursday?" | **D** | Not recurring; do it directly, no workflow. |
| "We keep needing ad-hoc competitive teardowns, roughly monthly." | **A** | Recurring → intake → `/scope` (which may decide merge/create). |

---

## 5. Requester input model

The whole point: **the requester does not fill the same large form every time.**
There is one tiny universal front door, then a small funnel-specific ask.

- **Front door (everyone, ~5 questions)** — `front-door-request.md`:
  what do you need, is this something we've done before (and what's it called),
  is it a one-time thing or recurring, by when, and how sensitive is the data.
  This alone is usually enough for the operator to route.

Then, only if needed, the operator asks for the matching funnel form:

| Funnel | Form the operator asks for | Fields the requester provides |
|---|---|---|
| **A — New Workflow** | **Reuse existing `methodology/templates/intake-template.md`** | recurring output, frequency, inputs, desired output, audience, definition of good, examples, sensitivity, deadline/review constraints (the existing 9 + 2 optional fields already match Funnel A exactly). |
| **B — Existing Run** | `workflow-run-input.md` (new) | workflow name or desired output; run date/period; input files or pasted inputs; one-time notes for this run; deadline; sensitivity confirmation. |
| **C — Revision** | `workflow-revision-request.md` (new) | workflow name; what's wrong/missing today; what should change going forward; whether audience/input/output-format/sensitivity/review rules change; example of the desired new output. |
| **D — One-Off** | `one-off-assist-request.md` (new) | what needs to be done; input material; audience; desired format; deadline/constraints. |

**Key reuse decision:** the candidate file `new-workflow-intake.md` is dropped —
it would duplicate `intake-template.md`, which is already precisely the Funnel A
form. Routing points to the existing template instead (respects the repo's
"resist premature abstraction / contract is source of truth" rules).

---

## 6. Proposed file changes

### PR1 — Routing (the next PR)

**Add:**

| File | Purpose | Contents | Why this PR |
|---|---|---|---|
| `methodology/methods/request-routing.md` | Source-of-truth for the funnel decision tree. | The Section 4 decision tree, the B-vs-C distinction, the "routing ≠ scoping" handoff rule, and the funnel→command mapping. | Methods are the authority a command points at, mirroring `scoping-method.md`. |
| `methodology/commands/route-request.md` | Canonical spec for `/route-request`. | Inputs, files read, files written, decision outputs, missing-info behavior, guardrails (see Section 7). | Lives beside the other command specs; the methodology layer is the source of truth. |
| `.claude/commands/route-request.md` | UI discoverability pointer. | Frontmatter (`description`, `argument-hint`) + the standard one-line delegation: "Execute the specification in `@methodology/commands/route-request.md`…". | Required so `/route-request` appears in Claude Code; never duplicates the spec. |
| `methodology/templates/front-door-request.md` | The tiny universal intake. | ~5 plain-language questions (Section 5). | The entry artifact requesters actually send. |
| `methodology/templates/workflow-run-input.md` | Funnel B form. | The 6 Funnel-B fields. | Needed to ask for run inputs without the full intake. |
| `methodology/templates/workflow-revision-request.md` | Funnel C form. | The 5 Funnel-C fields. | Captures a future-behavior change cleanly. |
| `methodology/templates/one-off-assist-request.md` | Funnel D form. | The 5 Funnel-D fields. | Captures a one-off without spinning up a workflow. |
| `docs/OPERATOR-GUIDE.md` | The operator's day-to-day playbook. | "A request arrived — what do I do?" walkthrough: route → read the 3 outputs → ask for the right form → dispatch to the right command. Funnel→command cheat sheet. | The seam that makes the repo *feel* seamless to the sole operator. |
| `docs/PROMPT-CARDS.md` | Copy-paste cards the operator sends to requesters. | Short snippets: "send me this to start something new," "send me this to run the usual thing," "send me this to change it," "send me this for a one-off." | Removes the manual "what do I ask for?" step. |

**Modify (light):**

| File | Change |
|---|---|
| `README.md` & `START-HERE.md` | Add the front door as "step 0" before intake; one short paragraph + a link to `docs/OPERATOR-GUIDE.md`. |
| `methodology/VERSION` | Bump `v0.3 → v0.4` (additive/MINOR: new methodology surface). |
| `methodology/migrations/2026-05-26-request-routing.md` | Migration note recording the additive routing layer (per `methodology/CLAUDE.md`: changes get a discoverable note; existing workflows are unaffected). |

**Explicitly NOT in PR1:** `new-workflow-intake.md` (reuse `intake-template.md`),
any script, any schema change, any change to `weekly-status-summary`.

### PR2 — Run Execution (planned, shipped second)

**Add:** `methodology/commands/run-workflow.md`, `.claude/commands/run-workflow.md`,
`methodology/templates/run-packet/` (the 6 packet templates: `INPUTS.md`,
`PROMPT_USED.md`, `OUTPUT_DRAFT.md`, `REVIEW.md`, `FINAL_OUTPUT.md`,
`RUN_RECORD.md`), optionally `scripts/workflowctl.py`.

**Modify:** `.claude/settings.json` (allow `python scripts/workflowctl.py run:*`
if the script is built), `.gitignore` (confirm/extend the existing
`run-records/*.local.yaml` + `*.local.md` coverage for sensitive packets),
`workflows/weekly-status-summary/operations/runbook.md` (reference `/run-workflow`),
`methodology/VERSION` (→ `v0.5`) + a migration note.

---

## 7. Command design — `/route-request <request-file-or-folder>`

- **Argument / inputs:** a path to a request folder under `intakes/{id}/`
  (containing the front-door form and/or raw message/files), or a single request
  file. Mirrors `/scope`'s folder-as-record convention.
- **Files read:**
  - the request file(s) in the given path;
  - `portfolio/workflows.yaml` — to detect whether a matching workflow exists and
    is `status: production` (decides A vs B/C);
  - `methodology/methods/request-routing.md` — the decision tree it applies;
  - the four requester templates — to know each funnel's required inputs and to
    compute what's missing.
- **Decision outputs (written into the request folder):**
  - `recommended_funnel.md` — **first line is exactly one of `A | B | C | D`**,
    then one paragraph of reasoning (and, for B/C, the matched `workflow_id` and a
    note confirming it is `production`). This mirrors `recommendation.md`'s
    "machine-readable first line" convention so automation/operator can branch.
  - `missing_info.md` — the gap between what the requester supplied and the
    target funnel's required fields, phrased as a ready-to-send ask ("To proceed
    I need: …"), naming the specific template to fill.
  - `next_action.md` — the exact next operator command, e.g.
    `/scope intakes/{id}` (A), `/run-workflow {id} <input-folder>` (B),
    `/revise-workflow {id}` (C), or "do directly — no workflow" (D).
- **Missing-info behavior:** never blocks on missing fields. It still classifies,
  then lists what to request. (Same philosophy as `/scope`: missing fields are a
  request for info, not a rejection.)
- **Safety guardrails (the spec must state these):**
  1. Routing is **advisory and non-mutating** — it never creates, runs, revises,
     or promotes anything, and never writes inside `workflows/`.
  2. It only writes the three output files into the request folder.
  3. For B/C it must **confirm the target workflow is `production`** before
     recommending a run/revision; if not production, it says so and routes to the
     appropriate lifecycle step instead.
  4. It respects sensitivity: if the request involves `confidential`/`restricted`
     data, it flags the data-handling requirement and reminds that raw content
     stays out of committed files (`sensitivity-policy.md`).
  5. When B-vs-C is ambiguous, it routes to **C** and says why (safer to open a
     controlled revision than to silently alter future behavior).
  6. Commit prefix for routing artifacts/spec changes: `methodology:` (spec/
     templates) or `scope:` (a specific routed request), per the constitution.

---

## 8. Revision handling

When a requester provides feedback, new inputs, or a desired change to an
**existing** workflow, classify before acting:

| Situation | Funnel | Action |
|---|---|---|
| "Just this once, also include X / use this extra file." | **B (one-time run note)** | Run normally; capture the note in the run packet's `INPUTS.md`/one-time-notes. **Do not** touch the contract. |
| "From now on, change format/audience/content/cadence/review/sensitivity." | **C (future behavior change)** | `/revise-workflow <id>` → contract-first: update `contract.yaml`, log why in `logs/decisions.md`, then update prompt/evals. |
| "I need a different recurring deliverable that this workflow doesn't cover." | **A (new workflow)** | New intake → `/scope` (which may itself say `merge` into the existing workflow, or `create`). |
| "Do this one unrelated thing once." | **D (one-off)** | Do it directly; do not create or revise a workflow. |

The litmus test is **scope of effect**: *this run only* → B; *all future runs* →
C; *a new recurring need* → A; *non-recurring* → D. This rule is stated in both
`request-routing.md` and `docs/OPERATOR-GUIDE.md`.

---

## 9. Automation boundary

- **Automate now (PR1):** classification into A/B/C/D, the missing-info diff, and
  emitting the three advisory output files. All read-only + writes confined to the
  request folder.
- **Stay human-approved (always):** creating a workflow (`/new-workflow`),
  promoting (`/promote-workflow`), revising (`/revise-workflow`), and — in PR2 —
  sending/delivering any run output. Routing recommends; the operator dispatches.
- **Automate later (PR2):** deterministic *scaffolding* of a run packet
  (create the folder, copy the production prompt into `PROMPT_USED.md`, compute
  input hashes, stub the 6 files, write the `run-records/{timestamp}.yaml` shell).
- **Do not build (explicitly out of scope per constraints):** any AI/model API
  call inside scripts (so `workflowctl.py` can scaffold and hash but cannot
  *generate* output), a web app, external-system integrations, requester-facing
  repo operations, or any heavyweight framework. Output generation and review
  stay operator-driven (operator + Claude in the workflow directory).

---

## 10. Phased implementation plan

### Phase 1 — Routing front door (= PR1)
- **Objective:** classify any request into A/B/C/D and tell the operator what to ask for.
- **Files touched:** the 8 new files + 3 light edits in Section 6 (PR1).
- **Deliverables:** working `/route-request`, four requester templates, routing
  method doc, operator guide, prompt cards, VERSION bump + migration note.
- **Acceptance criteria:** see Section 11.
- **Out of scope:** any run execution, any script, any schema change, any
  `weekly-status-summary` edit.
- **Risk & mitigation:** *Risk* — routing duplicates/contradicts `/scope`.
  *Mitigation* — `request-routing.md` explicitly defers Funnel A's deep judgment
  to `/scope`; routing only does the top-level switch. *Risk* — a new requester
  template drifts from the existing intake. *Mitigation* — Funnel A reuses
  `intake-template.md` rather than adding a duplicate.

### Phase 2 — Run packet contract + templates (first half of PR2)
- **Objective:** define the on-disk run-packet shape without executing anything.
- **Files touched:** `methodology/templates/run-packet/*` (6 files),
  `methodology/commands/run-workflow.md`, `.claude/commands/run-workflow.md`,
  runbook reference update, VERSION + migration note.
- **Deliverables:** a documented, operator-runnable `/run-workflow` (Claude-driven,
  no script) that produces the 6-file packet under
  `workflows/{id}/operations/run-records/{timestamp}/`.
- **Acceptance criteria:** running it on `weekly-status-summary` with the existing
  synthetic fixtures produces a complete packet; `RUN_RECORD.md` carries the
  `run-record.schema.yaml` fields (timestamp, input/output hashes, success,
  reviewer signoff, anomalies); raw sensitive content uses `.local.md`.
- **Out of scope:** the Python scaffolder; any model API call.
- **Risk & mitigation:** *Risk* — committing sensitive run output. *Mitigation* —
  reuse the existing `.gitignore` `*.local.md` / `*.local.yaml` reservation;
  packet template states the rule inline.

### Phase 3 — `workflowctl.py run` scaffolder (second half of PR2, optional)
- **Objective:** deterministic, model-free creation of the packet skeleton + input hashes.
- **Files touched:** `scripts/workflowctl.py`, `.claude/settings.json` permission.
- **Deliverables:** `python scripts/workflowctl.py run <id> --input <folder>` creates
  the packet folder, copies the prompt, hashes inputs, stubs files; exits 0/1 in
  the existing argparse + PASS/FAIL house style.
- **Acceptance criteria:** mirrors the manual packet from Phase 2; refuses to run a
  non-`production` workflow; CI's three checks stay green.
- **Out of scope:** output generation, delivery, scheduling.
- **Risk & mitigation:** *Risk* — script diverges from the command spec.
  *Mitigation* — the script is the "executable backbone" of the spec, exactly as
  `regenerate_index.py` backs `/regenerate-index`.

---

## 11. Acceptance criteria for the next PR (PR1)

- [ ] `/route-request` is discoverable in Claude Code (`.claude/commands/route-request.md`
      exists with valid `description` + `argument-hint` frontmatter and delegates to the spec).
- [ ] `methodology/methods/request-routing.md` exists and contains the decision tree
      and the B-vs-C distinction.
- [ ] `methodology/commands/route-request.md` exists and specifies inputs, files read,
      the three outputs, missing-info behavior, and guardrails.
- [ ] The three requester templates exist (`workflow-run-input.md`,
      `workflow-revision-request.md`, `one-off-assist-request.md`) plus
      `front-door-request.md`; Funnel A reuses `intake-template.md` (no duplicate added).
- [ ] One example request maps to **each** funnel (the Section 4 examples are
      reflected in `docs/OPERATOR-GUIDE.md` so each of A/B/C/D has a worked case).
- [ ] `docs/OPERATOR-GUIDE.md` and `docs/PROMPT-CARDS.md` explain which form to ask
      for in each case.
- [ ] Existing CI stays green: `validate_contracts.py`, the index-drift check, and
      `run_evals.py --all` all pass unchanged.
- [ ] No existing lifecycle behavior changes: `/scope`, `/new-workflow`,
      `/promote-workflow`, `/revise-workflow`, `/retire-workflow`, `/regenerate-index`
      and all scripts behave exactly as before (PR1 adds only new files + doc edits).
- [ ] `methodology/VERSION` bumped to `v0.4` with a matching migration note.

---

## 12. Final recommendation

- **Build first (PR1):** the routing front door — `/route-request`,
  `request-routing.md`, the front-door + three funnel templates (reusing
  `intake-template.md` for Funnel A), `docs/OPERATOR-GUIDE.md`, and
  `docs/PROMPT-CARDS.md`. It's docs + one command spec, carries zero CI risk, and
  immediately makes the repo easier to operate.
- **Do not build yet:** `/run-workflow`, the run-packet templates, and
  `scripts/workflowctl.py` — these are PR2. And per the constraints, never build
  AI API calls, a web app, external integrations, requester-facing repo ops, or a
  heavyweight framework.
- **First implementation dispatch should:** create the eight PR1 files and the
  three light edits; verify `/route-request` is discoverable; route the seven
  Section-4 example requests and confirm each lands in the right funnel with a
  correct `missing_info.md`/`next_action.md`; run the three CI checks locally to
  confirm green; bump `VERSION` to `v0.4` with a migration note; commit under the
  `methodology:` prefix and open the PR.
