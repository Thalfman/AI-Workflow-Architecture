---
description: Rebuild the portfolio index from all workflow contracts.
argument-hint: (none)
---

# /regenerate-index

Regenerate `portfolio/workflows.yaml` as a derived view of every workflow
contract. Called by the lifecycle commands; may also be run standalone after any
contract edit.

## Steps

1. Collect every workflow contract from both locations:
   - Active: `workflows/*/contract.yaml` (the `workflows/retired/` archive
     directory has no contract of its own, so it is skipped here).
   - Retired: `workflows/retired/*/contract.yaml`.
2. For each, extract a summary row:
   - `workflow_id`
   - `workflow_name`
   - `status`
   - `owner`
   - `requester.team`
   - `methodology_version`
   - `trigger.type`
   - `last_revised`
3. Overwrite `portfolio/workflows.yaml` with the collected rows under the
   `workflows:` key. If neither pattern matches any contract (a freshly
   scaffolded or empty library), write an empty list — `workflows: []` — rather
   than treating an unmatched glob as a literal path; an empty index is a valid
   result, not an error. Set `last_regenerated` to today's date and
   `methodology_version_at_regeneration` to the contents of
   `methodology/VERSION`.

## Outputs

- A freshly derived `portfolio/workflows.yaml`.

## Notes

- This file is **derived**. Never hand-edit it; re-run this command instead.
- Do not touch `portfolio/value-ledger.yaml` — that is maintained by
  `/retire-workflow` and manual value entries, not derived from contracts.
- Commit with the `portfolio:` prefix.
