# Routing test battery

Diagnostic battery for the request-routing logic in
`methodology/methods/request-routing.md`. Each `case-NN-*/` folder is one
hypothetical front-door request, dry-run through the decision tree by hand, with
the three advisory files `/route-request` would produce: `recommended_funnel.md`,
`missing_info.md`, and `next_action.md`. `SUMMARY.md` records the verdicts and
the findings the exercise surfaced.

These are synthetic diagnostic fixtures, NOT canonical example exemplars: they do
not live under `intakes/`, are never run, and change no contract, spec, or the
portfolio index. The operator (AI Workflow Architect) maintains this folder. To
add a case, write a new `case-NN-slug/front-door.md` as a sanitized completed
front-door form, dry-run it against the decision tree, write the three advisory
files, then add a row and any new finding to `SUMMARY.md`.
