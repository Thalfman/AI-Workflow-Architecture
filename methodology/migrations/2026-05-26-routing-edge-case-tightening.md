# Migration - tighten routing edge cases from the stress battery

- Date: 2026-05-26
- Methodology version: v0.5 -> v0.6 (minor; additive clarification)
- Docs: `methodology/methods/request-routing.md`, `docs/OPERATOR-GUIDE.md`

## What changed

Three clarity gaps in the routing prose were tightened. None changes the decision
tree; each makes an already-correct verdict easier to reach.

1. Ambiguity-to-C now states its trigger. The B-vs-C section says in plain prose
   that a request which adds or alters content without an explicit
   one-time-or-permanent marker is ambiguous by default and routes to C under the
   safety rule. A third worked-example row (a no-marker "let us try it" ask, verdict
   C) sits under the existing two.

2. Compound requests have first-class handling. A labeled note after the decision
   tree states that a single message carrying both a normal-run intent (B) and a
   future-behavior-change intent (C) routes to C as a whole under first-match-wins,
   and the dropped B half is handled by splitting the run off under the current
   contract now or queuing a Funnel B run once the revision lands.
   `docs/OPERATOR-GUIDE.md` gains a matching "Compound (B + C in one message)"
   worked case.

3. Guardrail 4 reconciles request sensitivity against the contracted envelope. When
   a request's stated sensitivity exceeds the matched workflow's contracted
   `max_sensitivity`, routing still classifies intent normally but flags the
   envelope mismatch in `recommended_funnel.md` and tells the operator not to
   proceed to `/run-workflow` until scope is confirmed, inputs are sanitized or
   downgraded, or a likely Funnel C review/sensitivity revision is opened to widen
   the envelope. Routing only flags and pauses; it does not decide whether the
   envelope should expand.

## Why

PR #6's routing stress-test battery (`docs/routing-test-battery/`) dry-ran eight
synthetic requests through the decision tree. All eight matched their expected
funnel, but three cases (case-01, case-07, case-08) surfaced wording gaps that made
the right verdict harder to reach than it needed to be. The battery's SUMMARY
recommended folding each gap back into the spec as a clarity fix; this migration
does exactly that. It promotes no battery case to a canonical exemplar and touches
no script, schema, contract, or workflow folder.

## Compatibility

Additive and backward compatible. No schema changed and no contract requires
migration. The decision tree is unchanged, so every funnel resolves exactly as
before and every existing workflow continues to operate unchanged under the version
recorded in its contract, per `methodology/CLAUDE.md`. The changes are wording-only:
clearer prose, one new worked-example row, one labeled note, one new operator-guide
worked case, and one extended guardrail sentence. The command spec
`methodology/commands/route-request.md` still delegates to the method document and
needs no edit here; if it later drifts from the tightened method language, sync it
in a follow-up.
