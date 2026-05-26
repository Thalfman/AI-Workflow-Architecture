# Prompt Cards

Copy-paste snippets the operator sends to a requester to collect exactly what's
needed — no more. Start with the front door; reach for a funnel card only if
`/route-request` says inputs are still missing. Each card maps to a template in
`methodology/templates/`.

---

## Card 0 — Front door (send this first, to anyone)

> Happy to help. So I can point this to the right place, a few quick things:
> 1. What do you need? (the deliverable or task, in your words)
> 2. Have we done this for you before? If so, what's it called?
> 3. Is this a one-time thing or something recurring?
> 4. Any deadline?
> 5. Is any of the data confidential or regulated? (if unsure, just say so)

*(Template: `methodology/templates/front-door-request.md`)*

---

## Card A — Start something new (recurring need)

> This looks like a new recurring deliverable. To set it up properly, could you fill
> this out? It covers the task, how often it runs, your inputs, what "good" looks
> like, who reads it, and a couple of sanitized examples.

*(Template: `methodology/templates/intake-template.md` → then `/scope`)*

---

## Card B — Run the usual thing

> I can run that. For this run, send me:
> 1. Which workflow (or just the deliverable name)
> 2. The period it covers (e.g. this week)
> 3. The input files or pasted source
> 4. Anything special for *just this run* (one-time only)
> 5. Your deadline
> 6. A quick confirmation of how sensitive the inputs are

*(Template: `methodology/templates/workflow-run-input.md` → then `/run-workflow`)*

---

## Card C — Change it going forward

> Sounds like a permanent change to how this runs from now on. To do it cleanly:
> 1. Which workflow
> 2. What's not working today
> 3. What should change going forward
> 4. Does it change the audience, inputs, format, content rules, cadence, or review?
> 5. An example of the new output you want, if you have one

*(Template: `methodology/templates/workflow-revision-request.md` → then `/revise-workflow`)*

---

## Card D — One-off task

> Happy to do this one. Send me:
> 1. What needs to be done (and what "done" looks like)
> 2. The input material
> 3. Who it's for
> 4. The format you want
> 5. Deadline and any constraints

*(Template: `methodology/templates/one-off-assist-request.md` → done directly, no workflow)*
