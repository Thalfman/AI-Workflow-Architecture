---
description: Rebuild the portfolio index from all workflow contracts.
argument-hint: (none)
---

# /regenerate-index

Regenerate `portfolio/workflows.yaml` as a derived view of every workflow
contract. Called by the lifecycle commands; may also be run standalone after any
contract edit.

## Steps

1. Walk every `workflows/*/contract.yaml` (including `workflows/retired/*/`).
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
   `workflows:` key. Set `last_regenerated` to today's date and
   `methodology_version_at_regeneration` to the contents of
   `methodology/VERSION`.

## Outputs

- A freshly derived `portfolio/workflows.yaml`.

## Notes

- This file is **derived**. Never hand-edit it; re-run this command instead.
- Do not touch `portfolio/value-ledger.yaml` — that is maintained by
  `/retire-workflow` and manual value entries, not derived from contracts.
- Commit with the `portfolio:` prefix.
