B

`weekly-status-summary` is `status: production` in `portfolio/workflows.yaml`, so
Q1 is yes. The requester is not changing any future behavior, so Q2 is no, and
they are supplying this week's updates for a normal run, so Q3 is yes - a Funnel
B run. Hand the inputs to `/run-workflow weekly-status-summary`.

Sensitivity note (guardrail 4): the inputs are flagged confidential - named
customer accounts and unreleased renewal figures. Per
`methodology/methods/sensitivity-policy.md`, no raw confidential content is ever
committed: the raw updates stay in the gitignored local run record, only hashes
and the review verdict are committed, and customer detail must be stripped from
the published summary. Note too that the contract declares
`max_sensitivity: internal`, so confidential inputs sit above the workflow's
current envelope - worth confirming with the operator before the run, and
possibly a later review/sensitivity revision.
