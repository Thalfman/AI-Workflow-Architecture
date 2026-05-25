# Intake schema

Specification of what a filled intake (`methodology/templates/intake-template.md`,
once completed by a requester) must contain. `/scope` parses submissions against
this schema and flags missing required fields.

| Field | Required | Description |
|---|---|---|
| **Requester identity** | yes | Name, role, team, and best contact method. |
| **Recurring task description** | yes | The deliverable the requester produces or wants produced, and how often. |
| **Trigger** | yes | The event or schedule that causes the task to happen. |
| **Current process** | yes | Start-to-finish walkthrough of how it is done today. |
| **Inputs** | yes | The sources worked from, each with format and origin. |
| **Outputs** | yes | What the finished deliverable looks like, who reads it, and its format. |
| **Definition of good** | yes | How the requester knows the deliverable succeeded. |
| **Sensitivity classification** | yes | The most sensitive piece of information involved (`public | internal | confidential | restricted`). |
| **Pain point** | yes | Why help is being requested and what it costs today. |
| **Constraints** | no | Deadlines, tooling restrictions, audience expectations. |
| **Example artifacts** | recommended | Two or three sanitized examples of past deliverables. |

## Validation notes

- A submission missing any **required** field is incomplete; `/scope` should
  request the missing fields in `scoping-reply.md` rather than guess.
- **Sensitivity** maps directly to the contract's `inputs[].sensitivity` and
  `max_sensitivity`. If restricted data is involved, apply
  `methodology/methods/sensitivity-policy.md` before any fixture is created.
- Example artifacts must be **sanitized or synthetic** before they enter the
  repository as fixtures. Raw examples stay in `intakes/{id}/raw/` (gitignored).
