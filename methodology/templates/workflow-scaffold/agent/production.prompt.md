# Production prompt — {{WORKFLOW_NAME}}

This prompt implements `contract.yaml`. If anything here disagrees with the
contract, the contract wins: update the contract first, then this prompt.

## Context
<Who the deliverable is for and what role you play. Pull the audience and purpose
from `contract.outputs[].audience` and `contract.definition_of_good`.>

## Input shape
<The inputs you receive, matching `contract.inputs[]`: names, formats, and where
they come from. State what to do if an input is missing or malformed.>

## Task
<What to produce, step by step.>

## Output requirements
<Exact format, structure, and length, matching `contract.outputs[].format` and
`contract.outputs[].success_criteria`.>

## Quality bar
<What "good" means, drawn from `contract.definition_of_good` and
`contract.acceptance_criteria`. List what to avoid.>

## Data handling
Honor `contract.max_sensitivity` and `contract.data_handling`. No raw confidential
or restricted content in examples, prompts, or logs. See
`methodology/methods/sensitivity-policy.md`.
