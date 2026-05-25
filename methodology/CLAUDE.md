# Methodology — working rules

These rules activate when Claude Code is working inside `methodology/`. They
layer on top of the root `CLAUDE.md`. The methodology is the tool wall: shared
commands, schemas, templates, and standards that every workflow depends on.
Changes here ripple outward, so move conservatively.

## Schema changes
- Be conservative about schema changes. A field rename or removal can silently
  invalidate every existing contract.
- Never break backward compatibility silently. If a change is breaking, bump the
  `contract_schema_version` at the top of `schemas/contract.schema.yaml` and
  write a migration note in `methodology/migrations/`.
- Always write a migration note when changing the contract schema, even for
  additive changes, so the change is discoverable later.

## Versioning
- Any change to the methodology that workflows should track requires
  incrementing `methodology/VERSION` (`vMAJOR.MINOR`). Increment MINOR for
  additive or clarifying changes; MAJOR for changes that require workflows to
  migrate before they keep working.
- Existing workflows are not auto-migrated. They keep running under the version
  recorded in their contract until explicitly migrated.

## Method documents
- Any change to the scoping methodology must be accompanied by an update to
  `methods/scoping-method.md`. The command and the method document must never
  disagree.
- The same applies to `methods/acceptance-review.md` and
  `methods/sensitivity-policy.md`: if behavior changes, the method document
  changes in the same commit.

## Commands
- Slash commands in `commands/` are markdown specifications of intent, not
  executable code. Keep them declarative: describe inputs, steps, and outputs.
- A command that produces or mutates a contract must reference
  `schemas/contract.schema.yaml` as the authority for structure.

## Components
- Do not add to `components/` speculatively. A component earns its place only
  after the same logic has appeared in at least two workflows.

## Commit prefix
- Commits touching this directory use the `methodology:` prefix.
