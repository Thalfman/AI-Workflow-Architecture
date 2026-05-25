# AI Workflow Library — Constitution

This file holds the universal rules for the entire library. They apply in every
directory, regardless of which workflow or methodology area is active. More
specific `CLAUDE.md` files (in `methodology/` and in each `workflows/{id}/`)
layer on top of these rules; Claude Code's hierarchical loader gives the more
specific file precedence. Where a deeper file is silent, the rules here govern.

## The contract is the source of truth
- The workflow contract at `workflows/{name}/contract.yaml` is the single source
  of truth for that workflow. Never modify a workflow's behavior without first
  updating its contract. Any artifact — prompt, eval, runbook, trigger config —
  that contradicts the contract is wrong by definition.

## Data handling
- No raw restricted or confidential data is ever committed to this repository.
  Fixtures must be sanitized or synthetic. See
  `methodology/methods/sensitivity-policy.md` for classification rules.

## Session discipline
- Every working session that modifies a workflow must end with an entry in that
  workflow's `logs/iteration-log.md` describing what changed and what is next.

## The portfolio is derived
- The portfolio index at `portfolio/workflows.yaml` is regenerated from
  contracts. Do not hand-edit it. Run `/regenerate-index` to rebuild it.

## Promotion gate
- A workflow may not be promoted to production until its evals pass and the
  requester has accepted a finished sample (recorded in the workflow's
  `logs/decisions.md`).

## Methodology versioning
- Methodology improvements happen in the `methodology/` directory and are tagged
  with a new `methodology/VERSION`. Existing workflows continue to operate under
  the version they were built against until they are explicitly migrated. Drift
  is made visible, not urgent.

## Shared logic
- Cross-workflow shared logic is only extracted into `methodology/components/`
  after the same logic has appeared in at least two workflows. Resist premature
  abstraction.

## Auto memory boundary
- Auto memory at `~/.claude/projects/{this-repo}/memory/` may hold cross-cutting
  operational knowledge that applies to the library as a whole: slash command
  usage patterns, debugging recipes, shell command conventions, and personal
  working preferences inside the library.
- Auto memory must not hold workflow-specific knowledge of any kind. Requester
  preferences, data shapes, quality criteria, audience details, success metrics,
  and any decision that concerns a single workflow belong in that workflow's
  `contract.yaml` or `logs/decisions.md`, never in auto memory. If a fact
  concerns a specific `workflow_id`, it does not belong in auto memory regardless
  of how convenient that would be.
- When asked to remember something workflow-specific, update that workflow's
  contract or decisions log — do not write to auto memory. The `MEMORY.md` index
  must never reference a specific `workflow_id`.

## Commit conventions
- Commit message prefixes identify the concern touched:
  `scope:`, `methodology:`, `workflow-{id}:`, `portfolio:`, `infra:`.
