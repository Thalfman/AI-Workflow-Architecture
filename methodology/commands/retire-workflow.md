---
description: Retire a workflow and archive its directory.
argument-hint: <workflow_id> [reason]
---

# /retire-workflow

Retire a workflow that is no longer needed.

**Arguments:** `$1` — the `workflow_id`. Remaining text — the reason for retirement.

## Steps

1. Set `status: retired` and update `last_revised` in
   `workflows/$1/contract.yaml`.
2. Append a final entry to `workflows/$1/logs/iteration-log.md` and a dated note
   to `workflows/$1/logs/decisions.md` capturing the retirement reason.
3. Move the directory to `workflows/retired/$1/` (create `workflows/retired/` if
   it does not exist). Preserve history with `git mv`.
4. Record a retirement note in `portfolio/value-ledger.yaml`: the `workflow_id`,
   retirement date, reason, and any value delivered while it ran.
5. Run `/regenerate-index`.

## Outputs

- Contract at `status: retired`, directory archived under `workflows/retired/`.
- A value-ledger entry.
- Updated `portfolio/workflows.yaml`.

## Notes

- Retirement is reversible by reversing the `git mv` and setting status back to
  `revising`; nothing is deleted.
- Commit with the `workflow-$1:` prefix.
