# Closed-Loop Repo Assessment

Status: assessment / planning. No code or contracts changed by this document.
Date: 2026-05-27.

## TL;DR

This repo is **already a closed-loop *design*.** The forward arc — intake →
route → scope → create → promote → run — is fully specified and largely
automated. The feedback arc — capture → improve → reuse — is designed but has
**never been exercised** and is missing exactly two cheap pieces: a metrics
rollup script and a feedback-review ritual. Closing the loop is mostly an
*operational* act (actually run the workflow), not an architectural one. It
should be done, but minimally: the repo serves one operator and holds one
workflow, so most "closed-loop automation" you could imagine would be
overengineering for traffic that does not exist.

## 1. What the repo does well

- **Contract-first governance that is load-bearing, not decorative.** Every
  workflow claim lives in `contract.yaml`; prompts, evals, and runbooks are
  derived artifacts validated against it (`scripts/validate_contracts.py`, CI).
- **A real promotion gate.** `check_promotion_gate.py` enforces four conditions
  (evals pass, dated sample acceptance, sensitivity verified, runbook complete)
  before `building -> production`. This is the quality spine.
- **Deterministic, offline, model-free evals.** `run_evals.py` grades structural
  checks (sections, tokens, length) with no network — fast, reproducible, CI-safe.
- **Disciplined sensitivity handling.** Four-level policy, `*.local.md` gitignore
  for `internal+` content, hashes-not-raw in run records, `intakes/*/raw/` ignored.
- **Honest versioning.** `methodology/VERSION` (v0.6) plus per-workflow recorded
  version; drift is *visible, not urgent*. Migration notes required on schema change.
- **Audit trail by construction.** Append-only `iteration-log.md` / `decisions.md`,
  immutable run packets, derived portfolio index. You can reconstruct *why* and *when*.

## 2. Does it already have enough structure to support a closed loop?

Yes — structurally. The eight lifecycle stages map to existing mechanisms; the
question is which stages are merely *specified* versus *exercised with real data*.

| # | Closed-loop stage | Mechanism today | State |
|---|---|---|---|
| 1 | Intake | `intakes/{id}/` + `raw/` (gitignored) + front-door form | Built, unexercised |
| 2 | Routing / classification | `/route-request` -> funnel A/B/C/D + 3 output files | Spec'd, unexercised |
| 3 | Execution-path selection | Funnels dispatch: A->`/scope`->`/new-workflow`; B->`/run-workflow`; C->`/revise-workflow`; D->direct | Spec'd |
| 4 | Output creation | `/run-workflow` + `agent/production.prompt.md` -> `OUTPUT_DRAFT` | Spec'd; **0 runs**. Model step is human/Claude-in-loop by design |
| 5 | Review / validation | `agent/reviewer.prompt.md` + `REVIEW.md` verdict + offline evals + promotion gate | Built; evals ran once at promotion |
| 6 | Feedback capture | `RUN_RECORD.md` (`success`, `reviewer_signoff`, `anomalies`) + `decisions.md` + `value-ledger.yaml` | **Schema only — never written.** `current_value: null`, ledger empty |
| 7 | Method / template improvement | `methodology/` + `VERSION` + `migrations/` | Built but **intuition-driven**, no path from run data |
| 8 | Reuse in future requests | `components/` (gated on 2+ workflows), `/scope` merge detection | Designed, unexercised; 1 workflow -> no reuse pressure |

Stages 1–5 are architecturally complete. Stages 6–8 are where the loop is open:
nothing flows *backward* from runs into measurement, method, and reuse.

## 3. What is missing for a *true* closed loop

Three things, in priority order, none of them large:

1. **Operational data.** The workflow has never run in production. No run records
   means no feedback to capture, no metric to compute, no ledger to populate.
   This is the single biggest gap and it is solved by *operating*, not building.
2. **A measurement connector.** Nothing reads `operations/run-records/*/RUN_RECORD.md`
   and rolls reviewer verdicts into `success_metric.current_value` and a
   `value-ledger.yaml` entry. Today that link is purely manual and has never
   happened. One small script closes it.
3. **A feedback->improvement ritual.** There is no defined moment where accumulated
   run feedback is reviewed and turned into a `/revise-workflow` decision or a
   methodology change. The mechanism to *act* (`/revise-workflow`, `VERSION` bump)
   exists; the *trigger* does not. This is a method doc and a cadence, not automation.

## 4. What should remain manual

- **Output generation and review.** Model drafting and the `pre_send` human review
  are deliberately human/Claude-in-loop. Do not script the model call into a
  hands-off pipeline at this scale.
- **The build phase.** Prompt engineering, fixture design, eval authoring, runbook
  writing. These are judgment work; automating them now buys nothing.
- **The create/merge/retire decisions.** `/scope` recommends; the operator decides.
- **Methodology evolution.** Improvements stay deliberate and versioned, never
  auto-applied to existing workflows (the constitution already mandates this).

## 5. What should become repeatable

- **Running a production workflow.** Establish the muscle: `/run-workflow` ->
  inspect packet -> record verdict, on the actual Friday cadence.
- **A periodic portfolio review.** A fixed ritual (e.g., end-of-week) that runs the
  metrics rollup and surfaces workflows whose metric is slipping or stale.

## 6. What should become measurable

- **`success_metric.current_value`.** Computed from run records, not hand-typed.
  For `weekly-status-summary` this is clean-send rate against a `>= 0.9` target.
- **Value-ledger entries.** Periodic value records tied to a measurement, so the
  portfolio has memory beyond current state.

## 7. What should become auditable

Already strong; extend, don't rebuild:

- Run packets are the audit unit — keep them immutable and hash-based for `internal+`.
- The metrics rollup must be **reproducible**: deriving the same number from the
  same run records, never editing the contract by hand to assert a value.
- Any feedback-driven revision must leave the existing trail: `decisions.md`
  reason entry, contract-first change, fresh sample acceptance on re-promotion.

## 8. What should become automated *later*

Only after volume justifies it:

- **Model-graded evals** (`llm-judge` / `semantic`) wired offline via the Claude
  API, to cover the synthesis/tone quality that structural checks cannot — once
  there are enough runs to calibrate the judge.
- **A CI metrics *report*** (non-gating) that prints current vs. target per workflow.
- **First `components/` extraction**, triggered naturally when a second and third
  workflow exhibit the same logic (the constitution's 2-workflow rule).

## 9. What would be overengineering for this repo

Building any of these now assumes scale the repo does not have (one operator, one
workflow, no real traffic):

- Self-healing / auto-revision agents that mutate contracts from run data.
- Anomaly-detection or ML pattern-mining across runs.
- Dashboards, web UI, or metrics visualization.
- Event/queue/webhook intake automation.
- Multi-operator RBAC or approval routing.
- Speculative `components/` extraction (constitution forbids it under 2 workflows).
- A full model-graded eval harness before there is run volume to calibrate it.

---

## The eight questions

**1. Can this repo become closed-loop?**
Yes, with no architectural rework. The forward arc is built; closing the loop
needs real runs + one rollup script + one review ritual.

**2. Should it become closed-loop?**
Yes — it is the explicit design intent — but *minimally*. The repo's own ethos
(resist premature abstraction, colocation over tooling) is the right constraint.
Close the loop with the lightest mechanism that works, then stop.

**3. Minimum viable closed-loop version**
- Operate `weekly-status-summary` for 2–3 cycles via `/run-workflow` with
  realistic synthetic inputs, producing real run packets with reviewer verdicts.
- Add `scripts/rollup_metrics.py`: read `RUN_RECORD.md` files -> compute the
  workflow's `success_metric` -> write `current_value` into the contract and append
  a `value-ledger.yaml` entry. The one missing connector.
- Add `methodology/methods/feedback-review.md`: the method for stage 6->7 — how to
  read run records and decide *revise / retire / keep*. Kept manual, mirrors
  `acceptance-review.md`.
- That alone closes stages 4->5->6->7 with near-zero new architecture.

**4. Strongest practical version**
- Everything in the MVP, plus:
- A thin `/review-portfolio` command (+ `.claude` pointer) that runs the rollup and
  surfaces workflows needing attention — the recurring ritual made one command.
- A non-gating metrics report step in `.github/workflows/validate.yml`.
- `methodology/methods/learnings-extraction.md`: convert recurring run anomalies
  into versioned methodology improvements (closes stage 7 as a real path).
- Build 2–3 more real workflows so reuse pressure is genuine -> earn the first
  `methodology/components/` extraction and exercise `/scope` merge detection
  (closes stage 8).
- *Optionally* model-graded evals via the Claude API for the semantic dimension.

**5. What should not be built yet**
See section 9. In short: no auto-revision agents, no anomaly ML, no dashboards, no
event-driven intake, no multi-operator machinery, no speculative components, no
full LLM-judge harness. All presuppose absent scale.

**6. What files would need to change (MVP)**
- `workflows/weekly-status-summary/contract.yaml` — `success_metric.current_value`
  populated **by the rollup, not by hand**.
- `workflows/weekly-status-summary/logs/iteration-log.md` + `decisions.md` —
  session entries (constitution requires).
- `portfolio/value-ledger.yaml` — first real entry, **written by the rollup**.
- `methodology/VERSION` + `methodology/migrations/` — bump when the new method doc
  / command lands (methodology rules require it).
- `README.md` / `docs/OPERATOR-GUIDE.md` — document the feedback/review cadence stage.
- `.github/workflows/validate.yml` — (strongest version) add non-gating metrics report.

**7. What new files should be added**
- *MVP:* `scripts/rollup_metrics.py`; `methodology/methods/feedback-review.md`;
  real run packets under
  `workflows/weekly-status-summary/operations/run-records/{timestamp}/`.
- *Strongest:* `methodology/commands/review-portfolio.md` (+ `.claude` pointer);
  `methodology/methods/learnings-extraction.md`; optionally `scripts/grade_llm.py`
  or model-graded support inside `run_evals.py`.

**8. Tests / verification that prove the loop works**
- **End-to-end loop trace** on the existing workflow (the definitive proof):
  `/run-workflow` -> run packet with `RUN_RECORD.md` created ->
  `rollup_metrics.py` populates `current_value` and writes a ledger entry ->
  simulate a degrading signal (repeated `approved_with_edits`) ->
  `/revise-workflow` opens a contract-first change -> re-promote ->
  `/run-workflow` again shows the metric move. This single trace exercises
  stages 4–8.
- **Existing gates stay green:** `validate_contracts.py`,
  `regenerate_index.py` drift check, `run_evals.py --all` (CI passes).
- **Rollup unit test** (first `tests/` dir, small): given N synthetic run records
  with known verdicts, assert the computed metric and the ledger entry.
- **Negative test:** rollup refuses to write when no run records exist;
  `current_value` stays `null` rather than fabricated.

## Tradeoffs and honest caveats

- The biggest lever is *use*, not *build*. If the operator will not actually run
  the workflow weekly, no amount of tooling closes the loop — it just adds
  scaffolding around an idle benchmark.
- `success_metric` for one workflow over a handful of runs is a weak statistic.
  Treat early `current_value` as directional, not authoritative.
- Structural evals cannot judge synthesis quality (the workflow's actual value).
  Until model-graded evals exist, the `pre_send` human review *is* the quality
  gate — keep it.
- Adding a `tests/` directory introduces the repo's first test harness. Keep it
  to the rollup only; do not retrofit tests onto the declarative command specs.
