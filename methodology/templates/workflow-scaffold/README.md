# {{WORKFLOW_NAME}}

<One-line description of the deliverable this workflow produces.>

This directory is one workflow product. Its `contract.yaml` is the single source
of truth; every other file here implements it.

## Layout
- `contract.yaml` — the contract. Read it first.
- `CLAUDE.md` — working rules active inside this directory.
- `agent/` — production and reviewer prompts.
- `fixtures/` — sanitized/synthetic inputs (`source/`) and expected outputs (`expected/`).
- `evals/` — eval plan plus test and regression cases.
- `operations/` — trigger config, runbook, and run records.
- `logs/` — iteration log and decisions.

## Lifecycle
Managed by the methodology commands: `/new-workflow` (create), `/promote-workflow`
(to production), `/revise-workflow`, `/retire-workflow`. Current status lives in
`contract.yaml`.
