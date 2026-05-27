# Feedback review

The cadence and process for reading a production workflow's accumulated run records
and deciding whether to **keep, revise, or retire** it. This is the stage 6 -> 7
ritual in `docs/plans/closed-loop-repo-assessment.md` (turn captured feedback into a
method or contract decision). It is the mirror of `acceptance-review.md`: acceptance
review is the one-time **entry** gate before promotion; feedback review is the
recurring gate that runs for the life of the workflow.

It is deliberately manual. The mechanisms to act already exist
(`/revise-workflow`, `/retire-workflow`, the `methodology/VERSION` bump); what was
missing is the *moment* feedback is read and turned into a decision. No command
auto-mutates a workflow from run data — the operator decides, and the decision is
recorded.

## When it happens

- **On a fixed cadence** — the recurring portfolio review (e.g. end-of-week or
  monthly), so a metric that is slipping or stale is surfaced before it bites.
- **On demand** — whenever a run produces a `rejected` verdict, a notable anomaly,
  or a streak of `approved_with_edits`, which signals the deliverable is drifting
  from what the contract promises.

## What you read

1. **The measured metric.** Run `scripts/rollup_metrics.py {id}` so
   `contract.success_metric.current_value` reflects every run record, then compare it
   to `target_value`. The rollup never fabricates a value: a workflow with no run
   records has no metric to review yet — operate it first.
2. **The run records.** The `RUN_RECORD.md` files under
   `operations/run-records/{timestamp}/`: the `reviewer_signoff.decision` trend and,
   especially, the `anomalies` field — retries, degraded inputs, manual
   intervention, threshold near-misses.
3. **The review notes.** Each packet's `REVIEW.md` "Required edits" — recurring edits
   are the clearest signal that the prompt or contract, not the run, is at fault.
4. **The decision history.** `logs/decisions.md`, so a new decision is made in the
   context of past ones.

## The three outcomes

- **Keep.** The metric meets or trends toward `target_value` and edits/anomalies are
  one-off. Record the reading (the rollup's `value-ledger.yaml` entry is the durable
  trace) and stop. Most reviews end here; resist the urge to tune a healthy workflow.
- **Revise.** The metric misses target, or the same required edit / anomaly recurs
  across runs — the deliverable, not the run, is the problem. Open `/revise-workflow`
  and make the change **contract-first** (update `contract.yaml`, record why in
  `logs/decisions.md`, then change `agent/` and `evals/` to match). Re-promotion
  clears the four acceptance-review gates again, including a **fresh** sample
  acceptance — a behavior change does not inherit the old one.
- **Retire.** The workflow no longer earns its place (the need is gone, or value is
  consistently low with no viable revision). Run `/retire-workflow`, which records a
  final `value-ledger.yaml` entry.

## Process

1. Run `scripts/rollup_metrics.py {id}`; note `current_value` vs `target_value`.
2. Read the run records: decision trend, anomalies, and recurring required edits.
3. Choose keep / revise / retire against the criteria above.
4. Record the decision and its reason in `logs/decisions.md` (and a line in
   `logs/iteration-log.md`), with the metric reading that motivated it.
5. Act: nothing further for keep; `/revise-workflow` (contract-first) for revise;
   `/retire-workflow` for retire.

## What this review does not do

- It does not change a workflow's behavior directly. Behavior changes go through
  `/revise-workflow`, contract-first, exactly as during the build phase.
- It does not auto-apply methodology changes. If a pattern across *several* workflows
  suggests a methodology improvement, that is a separate, versioned change under
  `methodology/` (a `VERSION` bump plus a migration note), and existing workflows are
  not auto-migrated.
- It does not treat a few runs as authoritative. A `success_metric` over a handful of
  runs is directional; weigh it as a signal, not a verdict.
