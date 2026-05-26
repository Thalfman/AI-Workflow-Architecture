# Request — Workflow Revision (Funnel C)

Use this to change how an existing workflow behaves **going forward** — for all
future runs, not just one. It feeds `/revise-workflow`, which is contract-first: the
contract changes before any prompt or eval. If your change is only for a single run,
use `workflow-run-input.md` instead.

## 1. Which workflow?
The name of the workflow you want changed.

## 2. What's wrong or missing today?
What about the current output isn't working for you?

## 3. What should change going forward?
Describe the new behavior you want for all future runs.

## 4. What kind of change is it?
Which of these does it touch? (Check all that apply.)
- [ ] Audience — who receives it
- [ ] Inputs — what sources it draws from
- [ ] Output format — structure, length, sections
- [ ] Content rules — what to include or exclude
- [ ] Cadence — how often it runs
- [ ] Review / sensitivity — how it's checked or what data it may use

## 5. Example of the desired new output
If you can, attach or sketch what "good" looks like after the change.
