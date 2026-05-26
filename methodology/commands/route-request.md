---
description: Classify an incoming request into funnel A/B/C/D and tell the operator what to ask for.
argument-hint: <path-to-request-file-or-folder>
---

# /route-request

Classify a raw incoming request into one of four funnels and prepare the operator's
next move — without the requester needing to understand the repo, the lifecycle, or
the commands. This is the library's front door. It applies the decision tree in
`methodology/methods/request-routing.md`.

**Argument:** `$ARGUMENTS` — a path to a request folder under `intakes/{id}/`
(containing the front-door form and/or a raw message/files), or a single request
file. Mirrors `/scope`'s folder-as-record convention.

## Files read

- The request file(s) at `$ARGUMENTS`.
- `portfolio/workflows.yaml` — to detect whether a matching workflow exists and is
  `status: production` (this decides Funnel A vs B/C).
- `methodology/methods/request-routing.md` — the decision tree this command applies.
- The four requester templates (`front-door-request.md`, `intake-template.md`,
  `workflow-run-input.md`, `workflow-revision-request.md`, `one-off-assist-request.md`)
  — to know each funnel's required inputs and compute what is missing.

## Steps

1. Read the request at `$ARGUMENTS`.
2. Read `portfolio/workflows.yaml`. Determine whether a production workflow already
   covers the requested deliverable; if so, capture its `workflow_id`.
3. Apply the decision tree in `methodology/methods/request-routing.md` to pick a
   single funnel (A, B, C, or D). When B-vs-C is ambiguous, choose **C**.
4. Compare what the requester supplied against the target funnel's required fields
   (per that funnel's template) and compute the gap.
5. Write the three output files (below). Do not act on the recommendation.

## Outputs

Write all three into the request folder (`$ARGUMENTS`):

- `recommended_funnel.md` — **first line is exactly one of `A | B | C | D`**, then
  one paragraph of reasoning. For B/C, name the matched `workflow_id` and confirm it
  is `status: production`. This mirrors `recommendation.md`'s machine-readable
  first-line convention so the operator (or automation) can branch on it.
- `missing_info.md` — the gap between what the requester supplied and the target
  funnel's required fields, phrased as a ready-to-send ask ("To proceed I need: …")
  and naming the specific template for the requester to fill. If nothing is missing,
  say so.
- `next_action.md` — the exact next operator command:
  `/scope intakes/{id}` (A), `/run-workflow {id} <input-folder>` (B),
  `/revise-workflow {id}` (C), or "do directly — no workflow" (D).

## Guardrails

1. Routing is **advisory and non-mutating**. Never create, run, revise, or promote
   anything; never write inside `workflows/`.
2. Write only the three output files, and only into the request folder.
3. For B/C, confirm the target workflow is `status: production` before recommending
   a run or revision. If it is not production (or does not exist), say so and route
   to the appropriate lifecycle step instead.
4. Respect sensitivity: if the request involves `confidential`/`restricted` data,
   flag the data-handling requirement and remind that raw content stays out of
   committed files (`methodology/methods/sensitivity-policy.md`).
5. When B-vs-C is ambiguous, route to **C** and say why.
6. Missing fields never block. Classify anyway, then list what to request.

## Notes

- Routing does not replace `/scope`. For Funnel A it only confirms "this looks like
  a new recurring need" and hands a populated intake to `/scope`, which applies its
  own full judgment (including possibly `reject`, `defer`, `merge`, `one-off`).
- Commit prefix: `methodology:` for spec/template changes; `scope:` for artifacts of
  a specific routed request.
