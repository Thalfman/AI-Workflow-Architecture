# Routing stress-test battery - diagnostic summary

This battery pressure-tests the routing judgment in
`methodology/methods/request-routing.md` and
`methodology/commands/route-request.md` against eight hypothetical front-door
requests. Each case was dry-run through the decision tree by hand and written up
as the three advisory files `/route-request` would produce. It tests routing
judgment only: it does not run any workflow, exercise the CI scripts, grade
evals, or execute a run packet. The intakes are synthetic diagnostic fixtures,
not canonical example exemplars, and nothing here mutates a contract, spec, or
the portfolio index. Ground truth for "what workflows exist" is the live
`portfolio/workflows.yaml`: one workflow, `weekly-status-summary`, at
`status: production`.

## Results

| Case | Verdict produced | Expected | Match | Note |
|---|---|---|---|---|
| case-01-b-vs-c-ambiguous-this-week-also | C | C | yes | Added section with no stated permanence; the genuine-ambiguity rule routes to C. |
| case-02-new-recurring-need | A | A | yes | No production workflow covers a monthly partner health report; recurring, so route to /scope. |
| case-03-clean-existing-run | B | B | yes | weekly-status-summary is production; new data, no future change, normal run. |
| case-04-permanent-future-change | C | C | yes | Permanent audience and length change to all future runs. |
| case-05-pure-one-off | D | D | yes | One-time board memo, not recurring, no workflow covers it. |
| case-06-half-filled-front-door | A | A | yes | Two front-door questions blank, but visible content clearly describes a new recurring deliverable. |
| case-07-multi-intent-run-plus-future-change | C | C | yes | Compound run-plus-permanent-change; Q2 fires, route to C, then queue B or split. |
| case-08-sensitive-data-flagged | B | B | yes | Normal run flagged confidential; B with a guardrail-4 sensitivity note. |

All eight cases matched their expected verdict. The decision tree resolved every
request to a single funnel without inventing a fifth outcome.

## Findings

The verdicts all landed where expected, but routing three of the eight cases
surfaced wording gaps that made the judgment harder than it needed to be. None
block routing today; each is a clarity improvement.

1. The ambiguity-to-C rule depends on an unstated permanence marker.
   - What the spec says: the worked examples contrast "Here's this week's data,
     and just this once also add a Customer Wins section." (B) against "From now
     on the weekly summary should include a Customer Wins section." (C), and the
     B-vs-C section says to route genuine ambiguity to C.
   - What was unclear in practice (case-01): the B example is only a B because of
     the explicit marker "just this once." Strip that marker and the identical
     surface request - add a Customer Wins section, "let us try it and go from
     there" - is ambiguous and flips to C. The spec never states in prose that
     the absence of an explicit one-time-or-permanent signal is itself the
     trigger for the ambiguity-to-C rule, so a reader can over-anchor on the B
     example and mis-route.
   - Recommended remediation: tighten wording in
     `methodology/methods/request-routing.md`. Add one line stating that when a
     request adds or alters content without an explicit one-time-or-permanent
     marker, permanence is ambiguous by default and routes to C; optionally add a
     third contrasting worked example with no permanence marker.

2. Compound requests (a run plus a permanent change in one message) have no
   first-class handling.
   - What the spec says: the decision tree is "top to bottom; first match wins"
     and resolves to a single funnel. Q2 routes any future-behavior change to C.
   - What was unclear in practice (case-07): a message that asks for this week's
     run AND a permanent change carries two intents at once. First-match-wins
     correctly routes the whole request to C, but the tree gives no guidance on
     what happens to the dropped B half, leaving the operator to invent the
     "split it, or queue a B after the revision lands" handling.
   - Recommended remediation: add a worked example to `docs/OPERATOR-GUIDE.md`
     (and a one-line note in `request-routing.md`) showing the compound case:
     route to C, and either split the run off under the current contract now or
     queue a Funnel B run once the revision lands.

3. Routing does not reconcile request sensitivity against the matched workflow's
   declared envelope.
   - What the spec says: guardrail 4 says if a request involves confidential or
     restricted data, flag the data-handling requirement and keep raw content out
     of committed files, per `methodology/methods/sensitivity-policy.md`.
   - What was unclear in practice (case-08): the request is a clean Funnel B run,
     but its inputs are confidential while `weekly-status-summary` declares
     `max_sensitivity: internal`. Guardrail 4 covers handling and non-commit of
     raw data, but says nothing about a request whose sensitivity exceeds the
     matched workflow's contracted envelope - arguably a signal that a
     review/sensitivity revision (Funnel C) is also warranted.
   - Recommended remediation: add a sentence to guardrail 4 in
     `methodology/methods/request-routing.md` - when request sensitivity exceeds
     the matched workflow's `max_sensitivity`, still run (B) but note the envelope
     mismatch and flag a possible review/sensitivity revision. If this is judged
     out of routing's advisory scope, "no change needed" is defensible and the
     flag stays in the B output only.

4. "Five fields" is loosely defined (minor; no change needed).
   - What the spec says: the front door is roughly five plain-language questions.
   - What was unclear in practice (case-06): because the questions are open
     prose, "missing two of five" is a judgment call about what counts as
     answered. This did not affect the verdict, and the funnel-specific
     missing_info ask was unaffected.
   - Recommended remediation: no change needed. The looseness is by design (the
     front door is deliberately informal) and routing classifies on content, not
     on field completeness.

## Recommended next PR

This battery is diagnostic. A follow-up PR can promote a curated subset to
canonical example exemplars under `intakes/`, where they would document the happy
path for each funnel. Recommendation:

- Promote to canonical exemplars: case-02 (A), case-03 (B), case-04 (C), and
  case-05 (D) - the clean one-per-funnel set - plus case-08 (B with a sensitivity
  flag) as the reference for the guardrail-4 path. These five cover every funnel
  and the sensitivity guardrail with unambiguous verdicts.
- Keep diagnostic-only, do not promote yet: case-01, case-06, and case-07. These
  are deliberately edge-shaped (ambiguity, a half-filled form, a compound
  request) and are most useful here alongside the findings they motivated.
  Promote them only after the finding-1 and finding-2 wording fixes land, so the
  exemplars match a tightened spec.
- New examples needed: once finding 2 is addressed, add a dedicated compound
  request exemplar to the operator guide. No new example is needed for findings 1
  or 3 - case-01 and case-08 already illustrate them.
