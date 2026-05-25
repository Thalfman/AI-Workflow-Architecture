---
description: Create a new workflow directory from the scaffold template.
argument-hint: <workflow_id> <path-to-draft-contract>
---

# /new-workflow

Stamp a new workflow from the scaffold template.

**Arguments:** `$1` — the `workflow_id` slug (lowercase, hyphenated).
`$2` — path to a draft contract (typically from a scoping run).

## Preconditions

- `workflows/$1/` must not already exist. If it does, stop and report.
- `workflows/retired/$1/` must not already exist. A retired workflow keeps its
  `workflow_id` reserved, so recreating that id would produce duplicate ids
  across active and retired contracts (and ambiguous index rows). To bring a
  retired workflow back, revive it deliberately per `/retire-workflow` (reverse
  the `git mv`), not with `/new-workflow`.
- `$1` must not be the reserved word `retired`. `workflows/retired/` is the
  archive namespace owned by `/retire-workflow`; a workflow with that id would
  collide with the archive container.
- The draft contract at `$2` must parse and broadly conform to
  `methodology/schemas/contract.schema.yaml`.

## Steps

1. Copy the entire contents of
   `methodology/templates/workflow-scaffold/` into `workflows/$1/`.
2. Replace `workflows/$1/contract.yaml` with the draft contract from `$2`, then:
   - Set `workflow_id: $1`.
   - Set `status: building`.
   - Set `methodology_version` to the contents of `methodology/VERSION`.
   - Set `contract_schema_version` to match the schema file's version comment,
     written as a quoted string (e.g. `"1.0"`) so YAML does not parse it as a
     number; the schema declares this field as `string`.
   - Set `created` and `last_revised` to today's date.
3. Initialize `workflows/$1/logs/iteration-log.md` with today's date and a first
   entry recording the creation event (created from scaffold, methodology
   version, source intake if known).
4. Run `/regenerate-index` to add the workflow to `portfolio/workflows.yaml`.

## Outputs

- A populated `workflows/$1/` directory at `status: building`.
- An updated `portfolio/workflows.yaml`.

## Notes

- Commit with the `workflow-$1:` prefix.
- Do not begin prompt or eval work in the same action; creation and building are
  separate sessions so the contract is reviewed first.
