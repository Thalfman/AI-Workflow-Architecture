# Using this repository as a template

This repo is a reusable operating framework for AI workflows. You can clone it as the
starting point for a new AI workflow effort — a team, a domain, or a client — and it
arrives with the governance, schemas, commands, and one fully worked example already
in place. This guide takes you from a fresh clone to your first promoted workflow.

## What you inherit

- The constitution and working rules: root `CLAUDE.md`, `methodology/CLAUDE.md`, and
  the per-workflow `CLAUDE.md` in the scaffold.
- The contract schema and methods: `methodology/schemas/`, `methodology/methods/`.
- The six lifecycle commands as Claude Code slash commands: `.claude/commands/`
  (thin pointers to the canonical specs in `methodology/commands/`).
- The automation: `scripts/validate_contracts.py`, `regenerate_index.py`,
  `run_evals.py`, `check_promotion_gate.py`, plus CI in `.github/workflows/validate.yml`.
- A complete worked example: `workflows/weekly-status-summary/` — read it as the
  reference for what a filled-in workflow looks like.

## Make it yours (one-time)

1. Install the toolchain: `pip install -r requirements.txt`.
2. Decide whether to keep `workflows/weekly-status-summary/` as a living example or
   remove it. If you remove it, delete the directory and run
   `python scripts/regenerate_index.py` so the portfolio index reflects an empty library.
3. Skim `START-HERE.md` — it is the operator on-ramp and traces one request through
   every layer.

## Stand up your first workflow

The lifecycle is the same one the reference workflow went through:

1. **Intake.** Copy `methodology/templates/intake-template.md`, fill it in, and drop
   it in a folder under `intakes/`.
2. **`/scope <intake-folder>`** — produces a reply, a draft contract, and a
   `recommendation.md` (reject | defer | merge | one-off | create).
3. **`/new-workflow <id> <draft-contract>`** — stamps `workflows/<id>/` from the
   scaffold at `status: building`.
4. **Build, contract-first.** Edit `contract.yaml` first, then make the artifacts
   match: write `agent/production.prompt.md`, add synthetic `fixtures/source/` and an
   accepted sample in `fixtures/expected/`, and write eval cases in `evals/`. Use the
   reference workflow's `evals/test-cases.yaml` as a model — `structural` graders run
   offline and in CI.
5. **Move to `in_review`** when the artifacts are complete (update `contract.yaml` and
   log it in `logs/`), then prove it:
   - `python scripts/validate_contracts.py`
   - `python scripts/run_evals.py <id>`
   - `python scripts/check_promotion_gate.py <id>`
6. **Record acceptance** in `logs/decisions.md` (requester or owner for real work;
   operator/reference acceptance only for example workflows).
7. **`/promote-workflow <id>`** — moves it to `production` once all four gates pass.
8. **`/regenerate-index`** keeps `portfolio/workflows.yaml` in sync. Later,
   `/revise-workflow` and `/retire-workflow` handle change and sunset; retirement
   records value in `portfolio/value-ledger.yaml`.

## Keep it honest

- The contract is the source of truth. Never change behavior without changing the
  contract first.
- Commit fixtures that are synthetic or sanitized only — never raw confidential data
  (`methodology/methods/sensitivity-policy.md`).
- Evolve shared methodology in `methodology/` and bump `methodology/VERSION` with a
  migration note; existing workflows keep running under the version they recorded.
- CI (`.github/workflows/validate.yml`) runs contract validation, the index drift
  check, and `run_evals.py --all` on every push — keep it green.
