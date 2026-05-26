# AI Workflow Library

One repository that holds an entire AI workflow operation: intake, scoping,
building, production, revision, and retirement. It serves a single architect
(the operator) who turns recurring deliverable requests from non-technical
project managers into durable, governed AI workflows.

> **New here?** Read [`START-HERE.md`](START-HERE.md) first — it traces one request
> through every layer in about five minutes.

This is not a generic monorepo. It is a workshop with three concerns sharing one
root:

| Concern | Directory | Metaphor | Holds |
|---|---|---|---|
| **Methodology** | `methodology/` | The tool wall | Reusable commands, schemas, templates, and standards |
| **Workflows** | `workflows/` | The project benches | One subdirectory per approved workflow product |
| **Portfolio** | `portfolio/` | The dashboard | The derived index and value ledger across all workflows |

These live together because, at pilot scale, physical colocation is the only
enforcement mechanism a solo operator can sustain.

## Daily operating rhythm

1. Open the portfolio index at `portfolio/workflows.yaml` and pick one workflow.
2. Work inside that workflow's directory — its `CLAUDE.md` scopes Claude Code to
   it automatically.
3. Honor the workflow's `contract.yaml` as the source of truth.
4. End the session with an entry in the workflow's `logs/iteration-log.md`.

## Intake to production, in commands

| Stage | Command | Result |
|---|---|---|
| Triage a request | `/scope <intake-folder>` | Reply, draft contract, recommendation |
| Create a workflow | `/new-workflow <id> <draft-contract>` | New `workflows/{id}/` from scaffold |
| Ship it | `/promote-workflow <id>` | Status → `production` after evals + acceptance |
| Change it | `/revise-workflow <id>` | Status → `revising`, contract-first |
| Sunset it | `/retire-workflow <id>` | Archived, ledger updated |
| Rebuild the index | `/regenerate-index` | `portfolio/workflows.yaml` refreshed |

## Where to go deeper

- The five-minute on-ramp for newcomers: [`START-HERE.md`](START-HERE.md)
- The rules that govern every session: [`CLAUDE.md`](CLAUDE.md)
- How the methodology works and how to evolve it safely:
  [`methodology/README.md`](methodology/README.md)
- The scoping method behind the intake gate:
  [`methodology/methods/scoping-method.md`](methodology/methods/scoping-method.md)
- Reusing this repo as a template for a new effort:
  [`methodology/templates/USING-THE-TEMPLATE.md`](methodology/templates/USING-THE-TEMPLATE.md)

## Key principles

- **The contract is load-bearing.** Every claim about a workflow lives in its
  `contract.yaml`. Contradicting artifacts are wrong by definition.
- **The intake gate is explicit.** Not every request becomes a workflow. Scoping
  recommends one of: reject, defer, merge, one-off, or create.
- **Methodology drift is versioned, not branched.** Each workflow records the
  methodology version it was built against.
- **The portfolio is derived.** Never hand-edit it.
