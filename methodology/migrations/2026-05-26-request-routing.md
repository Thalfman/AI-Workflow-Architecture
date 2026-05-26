# Migration — add the request-routing front door

- Date: 2026-05-26
- Methodology version: v0.3 → v0.4 (minor; additive)
- Docs: `methodology/methods/request-routing.md`, `methodology/commands/route-request.md`,
  `.claude/commands/route-request.md`, four requester templates under
  `methodology/templates/`, `docs/OPERATOR-GUIDE.md`, `docs/PROMPT-CARDS.md`

## What changed

Added a thin, advisory routing layer in front of intake. A new `/route-request`
command classifies a raw incoming request into one of four funnels — **A** (new
workflow), **B** (existing run), **C** (revision), **D** (one-off) — and writes three
advisory files (`recommended_funnel.md`, `missing_info.md`, `next_action.md`) into
the request folder. Four requester templates were added: a tiny universal
`front-door-request.md`, plus `workflow-run-input.md`, `workflow-revision-request.md`,
and `one-off-assist-request.md`. Funnel A deliberately reuses the existing
`intake-template.md` rather than adding a duplicate. An operator guide and prompt
cards under `docs/` make the front door usable day to day.

## Why

The library governed a workflow's lifecycle well but had no *front door*: every
request entered through the same heavyweight intake form and `/scope`, and the
operator was the router by hand. Routing makes the top-level "which kind of request
is this, and what small input do I need from the requester?" decision explicit and
fast, while leaving the deep judgment to the existing commands.

## Compatibility

Additive and backward compatible. No schema changed; no contract requires migration.
Routing is non-mutating — it never writes inside `workflows/` and never creates,
runs, revises, or promotes anything; it only classifies and prepares. Every existing
lifecycle command (`/scope`, `/new-workflow`, `/promote-workflow`,
`/revise-workflow`, `/retire-workflow`, `/regenerate-index`) and every script behave
exactly as before. Funnel B's landing command (`/run-workflow`) is planned for a
later methodology version and is not part of this change. Existing workflows are not
auto-migrated; they keep recording the methodology version they were built against,
per `methodology/CLAUDE.md`.
