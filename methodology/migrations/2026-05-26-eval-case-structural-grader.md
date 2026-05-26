# Migration — add `structural` grader to the eval-case schema

- Date: 2026-05-26
- Methodology version: v0.1 → v0.2 (minor; additive)
- Schema: `methodology/schemas/eval-case.schema.yaml` `eval_case_schema_version` 1.0 → 1.1

## What changed

Added a fourth grader, `structural`, to the eval-case schema, plus an
`expected.checks` block holding machine-checkable assertions
(`required_sections`, `must_include_all`, `must_exclude`, `max_words`,
`min_words`). A `structural` case inspects the committed artifact at
`expected.output` and passes when every assertion holds.

## Why

The library's eval runner grades offline and deterministically (no model call,
no network). The existing graders could not support that: `exact`/`semantic`
require a freshly generated output to compare against, and `llm-judge` requires a
model. `structural` lets a workflow assert verifiable properties of a committed
sample output (required sections, contributor coverage, length budget, absence of
banned tokens) that run in CI without an API key.

## Compatibility

Additive and backward compatible. Existing cases using `exact`, `semantic`, or
`llm-judge` are unchanged and remain valid; `checks` is ignored by those graders.
No existing workflow contracts require migration. Workflows built against v0.1
keep operating under v0.1 until explicitly migrated, per `methodology/CLAUDE.md`.
