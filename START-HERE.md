# Start here

This repository is an **AI workflow operating framework**: it turns recurring,
AI-assisted work requests into governed, reusable workflow products. If you are new,
read this page first — it traces one request through every layer in about five minutes.

## The three concerns

| Concern | Directory | What lives here |
|---|---|---|
| **Methodology** | `methodology/` | The reusable tool wall: command specs, schemas, methods, and the workflow scaffold. |
| **Workflows** | `workflows/` | One directory per approved workflow product. Each is governed by its own `contract.yaml`. |
| **Portfolio** | `portfolio/` | The derived index (`workflows.yaml`) and the `value-ledger.yaml`. |

The rules that bind every session live in the root `CLAUDE.md` (the constitution).
More specific `CLAUDE.md` files in `methodology/` and in each workflow layer on top of it.

## One request, end to end

Follow a single request from inbox to production. Each step is a slash command; the
canonical specification for every command lives in `methodology/commands/`, and the thin
pointer in `.claude/commands/` is what makes it appear in Claude Code.

0. **Front door.** Before intake, a raw request arrives. Drop it in `intakes/{id}/` and
   run **`/route-request <request-folder>`** — it classifies the request into one of four
   funnels (new workflow, existing run, revision, one-off) and tells you which small form
   to ask the requester for. Routing is advisory and never mutates a workflow. The
   operator's day-to-day playbook is [`docs/OPERATOR-GUIDE.md`](docs/OPERATOR-GUIDE.md).
1. **Intake.** For a new recurring need, a requester fills in
   `methodology/templates/intake-template.md` and drops it in a folder under `intakes/`.
2. **`/scope <intake-folder>`** — triages the request and writes a reply, a draft
   contract, and a `recommendation.md` whose first line is one of
   *reject | defer | merge | one-off | create*. Scoping never creates a workflow.
3. **`/new-workflow <id> <draft-contract>`** — stamps `workflows/<id>/` from
   `methodology/templates/workflow-scaffold/` at `status: building` and refreshes the index.
4. **Build.** Inside the workflow directory, make `contract.yaml` true: write
   `agent/production.prompt.md`, add synthetic `fixtures/`, and define `evals/`. The
   contract is the source of truth — update it first, then make artifacts match.
5. **Evaluate.** Run the eval runner against the workflow's `evals/`. A workflow cannot
   be promoted until its evals pass at the contract's `pass_threshold`.
6. **`/promote-workflow <id>`** — enforces the promotion gate
   (`methodology/methods/acceptance-review.md`): evals pass, a sample was accepted (dated
   entry in `logs/decisions.md`), sensitivity is verified, and the runbook is complete.
   On success, `status: production`.
7. **`/revise-workflow <id>`** and **`/retire-workflow <id>`** handle change and sunset
   later in the workflow's life.
8. **`/regenerate-index`** rebuilds `portfolio/workflows.yaml` from all contracts. The
   index is derived — never hand-edit it.

A complete worked example of steps 3–6 lives in
[`workflows/weekly-status-summary/`](workflows/weekly-status-summary/) — read its
`contract.yaml`, prompt, fixtures, and `logs/` to see the lifecycle in action.

## Automation layer

The `scripts/` directory holds the small Python helpers an operator (and CI) run to keep
the framework honest. Install once with `pip install -r requirements.txt`, then:

| Script | What it does |
|---|---|
| `scripts/validate_contracts.py` | Checks every contract against the structure in `methodology/schemas/contract.schema.yaml`. |
| `scripts/regenerate_index.py` | The executable backbone of `/regenerate-index`. |
| `scripts/run_evals.py <id>` / `--all` | Runs a workflow's eval cases offline and reports the pass rate. |
| `scripts/check_promotion_gate.py <id>` | Verifies the four promotion-gate conditions before `/promote-workflow`. |
| `scripts/workflowctl.py run <id> --input <folder>` | The model-free backbone of `/run-workflow`: scaffolds a run packet (copies the prompt, hashes inputs, stubs the record). |

These same checks run automatically in CI (`.github/workflows/validate.yml`) on every
push: contract validation, a portfolio-index drift check, and `run_evals.py --all`.

## Where to go deeper

- The constitution every session obeys: [`CLAUDE.md`](CLAUDE.md)
- The operating rhythm and command table: [`README.md`](README.md)
- How the methodology works and evolves safely: [`methodology/README.md`](methodology/README.md)
- The scoping judgement behind the intake gate: [`methodology/methods/scoping-method.md`](methodology/methods/scoping-method.md)
- Reusing this repo for a new effort: [`methodology/templates/USING-THE-TEMPLATE.md`](methodology/templates/USING-THE-TEMPLATE.md)
