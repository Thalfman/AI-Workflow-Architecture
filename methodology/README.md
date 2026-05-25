# Methodology

The tool wall. Everything reusable across workflows lives here: the slash
commands that drive the lifecycle, the schemas that define artifact structure,
the templates that new workflows are stamped from, and the method documents that
explain the judgment behind the commands.

## Layout

```
methodology/
├── VERSION              # methodology version tag (vMAJOR.MINOR)
├── CLAUDE.md            # rules active when working in this directory
├── commands/            # slash-command specifications (markdown, not code)
├── schemas/             # canonical structure for intakes, contracts, evals, runs
├── templates/           # intake template + workflow-scaffold copied by new-workflow
├── methods/             # documented methods behind the commands
├── components/          # shared logic — empty until two workflows prove a pattern
└── migrations/          # notes recorded when the contract schema changes
```

## How the commands work together

```
intake folder ──/scope──▶ recommendation (reject | defer | merge | one-off | create)
                              │ create
                              ▼
                         /new-workflow ──▶ workflows/{id}/  ──▶ /regenerate-index
                              │
                  build + eval + sample acceptance
                              ▼
                         /promote-workflow ──▶ status: production ──▶ /regenerate-index
                              │
                     change requested
                              ▼
                         /revise-workflow ──▶ status: revising (contract first)
                              │
                     no longer needed
                              ▼
                         /retire-workflow ──▶ archived + value-ledger note
```

`/regenerate-index` is called by the lifecycle commands and can also be run
standalone after any contract edit.

## Evolving the methodology safely

1. **Read the method document first.** Commands encode judgment that lives in
   `methods/`. Change the method document and the command together.
2. **Treat the contract schema as an API.** Other artifacts depend on its field
   names. Additive changes are safe; renames and removals are breaking.
3. **Write a migration note** in `migrations/` for any contract schema change,
   and bump `contract_schema_version` for breaking ones.
4. **Bump `VERSION`** when workflows should be able to see that the methodology
   moved. Existing workflows keep their recorded version until migrated.
5. **Earn components.** Promote shared logic into `components/` only after it has
   appeared in two workflows.

See `CLAUDE.md` in this directory for the enforceable rules.
