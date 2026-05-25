# Sensitivity policy

Rules for handling data by classification. This policy governs what may be
committed, what must stay local, and how fixtures are prepared. It is referenced
by the intake schema, the contract schema, the scoping method, and the
acceptance review.

## Classifications

| Level | Meaning | Examples |
|---|---|---|
| **public** | Already public or intended to be. | Published reports, marketing copy. |
| **internal** | Non-sensitive but not for outside eyes. | Internal status notes, team rosters. |
| **confidential** | Sensitive; limited audience; harm if leaked. | Unreleased financials, customer lists. |
| **restricted** | Regulated or high-harm. | PII, credentials, health, legal-hold data. |

## What may be committed

| Level | Raw data committed? | Fixtures |
|---|---|---|
| public | yes | real samples allowed |
| internal | yes, if non-identifying | real samples allowed |
| confidential | **no** | sanitized or synthetic only |
| restricted | **no** | synthetic only |

- **No raw confidential or restricted data is ever committed.** This restates the
  root `CLAUDE.md` rule and is non-negotiable.
- Raw intake examples live in `intakes/{id}/raw/`, which is gitignored. Only
  after sanitizing do they become committed fixtures under
  `workflows/{id}/fixtures/`.

## Where sensitive material lives instead

- **Secrets** (API keys, tokens, credentials): `.env` / `.env.local`, gitignored.
  Never inline in any committed file.
- **Machine-local context** that must not be shared: `CLAUDE.local.md` or any
  `*.local.md`, gitignored.
- **Local-only run records** that may reference sensitive inputs:
  `operations/run-records/*.local.yaml`, gitignored. Committed run records carry
  hashes, not raw content (see `schemas/run-record.schema.yaml`).

## Sanitizing fixtures

1. Replace real names, identifiers, and numbers with synthetic equivalents that
   preserve shape and edge cases.
2. Keep structure and formatting so the fixture still exercises the workflow.
3. Confirm no secret, PII, or restricted value survives in the sanitized copy.
4. When in doubt, synthesize from scratch rather than redact.

## In the contract
A workflow's `max_sensitivity` is the highest classification among its inputs.
`data_handling` must describe, in plain language, how inputs at that level are
obtained, processed, and disposed of consistent with this policy.
