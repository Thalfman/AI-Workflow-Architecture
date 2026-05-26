---
description: Rebuild the portfolio index from all workflow contracts.
argument-hint: (none)
---

Execute the specification in @methodology/commands/regenerate-index.md.

Obey the rules in the root `CLAUDE.md` and `methodology/CLAUDE.md`. The methodology spec is
the single source of truth for this command — do not deviate from it. Once `scripts/regenerate_index.py`
exists (added with the automation layer), running it is the canonical way to perform this command.
This file is only a pointer so the command is discoverable in Claude Code; never duplicate the
spec's content here.
