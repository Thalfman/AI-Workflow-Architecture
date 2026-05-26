#!/usr/bin/env python3
"""Check the promotion gate for a workflow before /promote-workflow.

Encodes the four conditions from methodology/methods/acceptance-review.md as
executable checks (cited below) and reads the workflow's own data files for
evidence. It does not parse prose docs at runtime. Keep this script and
acceptance-review.md in sync in the same commit.

Gates (all must hold; promotion is all-or-nothing), valid from building/in_review/revising:
  1. Evals pass at the contract's threshold (delegated to run_evals).
  2. A dated sample-acceptance entry with an accepted verdict exists in
     logs/decisions.md, dated no earlier than the contract's last_revised
     (a fresh acceptance is required after a revision).
  3. Sensitivity is consistent: each input.sensitivity <= max_sensitivity.
  4. operations/runbook.md is complete enough to trigger, run, review, and recover.

Usage:
    python scripts/check_promotion_gate.py <workflow_id>
Exit code 0 only if the status precondition and all four gates hold.
"""
from __future__ import annotations

import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install it with: pip install -r requirements.txt")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_evals  # noqa: E402  (same-directory import)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENSITIVITY_ORDER = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
PROMOTABLE_FROM = {"building", "in_review", "revising"}

# Acceptance is a dated "### ..." block that (a) carries an explicit
# "Verdict: accepted" line, (b) names who accepted, and (c) dates the acceptance in
# the heading. Matching a heading that merely contains "accept" is too loose (it
# would pass "not accepted"); reading the date from arbitrary body text is too loose
# (a fixture filename like week-2026-05-18.md could masquerade as the date). This
# follows the scaffold decisions.md format ("### <date> — sample accepted by <who>").
HEADING_RE = re.compile(r"^###\s+(.*)$", re.MULTILINE)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
ACCEPTED_VERDICT_RE = re.compile(r"verdict:\s*accepted\b", re.IGNORECASE)
ACCEPTED_BY_RE = re.compile(r"accepted by", re.IGNORECASE)


def coerce_date(value):
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def gate_sensitivity(contract):
    max_sens = contract.get("max_sensitivity")
    if max_sens not in SENSITIVITY_ORDER:
        return [f"max_sensitivity invalid or missing: {max_sens!r}"]
    inputs = contract.get("inputs")
    if not isinstance(inputs, list):
        return [f"inputs must be a list, got {type(inputs).__name__}"]
    errors = []
    for i, inp in enumerate(inputs):
        if not isinstance(inp, dict):
            errors.append(f"inputs[{i}] is not a mapping")
            continue
        s = inp.get("sensitivity")
        if s not in SENSITIVITY_ORDER:
            errors.append(f"inputs[{i}].sensitivity invalid: {s!r}")
        elif SENSITIVITY_ORDER[s] > SENSITIVITY_ORDER[max_sens]:
            errors.append(f"inputs[{i}].sensitivity ({s}) exceeds max_sensitivity ({max_sens})")
    return errors


def gate_runbook(workflow_dir):
    path = os.path.join(workflow_dir, "operations", "runbook.md")
    if not os.path.isfile(path):
        return ["operations/runbook.md is missing"]
    with open(path) as f:
        text = f.read()
    errors = []
    if len(text.strip()) < 200:
        errors.append("runbook.md is too short to operate the workflow")
    for needle in ("Trigger", "Run steps", "Failure"):
        if needle not in text:
            errors.append(f"runbook.md missing a '{needle}' section")
    if "review" not in text.lower():
        errors.append("runbook.md does not describe how the output is reviewed")
    return errors


def gate_acceptance(workflow_dir, contract):
    path = os.path.join(workflow_dir, "logs", "decisions.md")
    if not os.path.isfile(path):
        return ["logs/decisions.md is missing"]
    with open(path) as f:
        text = f.read()

    headings = list(HEADING_RE.finditer(text))
    accepted_dates = []
    for i, match in enumerate(headings):
        heading = match.group(1)
        body_start = match.end()
        body_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[body_start:body_end]
        if not ACCEPTED_VERDICT_RE.search(block):
            continue
        # Must name who accepted (acceptance-review.md: the entry names "who accepted").
        if not (ACCEPTED_BY_RE.search(heading) or ACCEPTED_BY_RE.search(block)):
            continue
        # The acceptance date must be in the heading, not arbitrary body text.
        date_match = DATE_RE.search(heading)
        if not date_match:
            continue
        try:
            accepted_dates.append(datetime.date.fromisoformat(date_match.group(1)))
        except ValueError:
            continue

    if not accepted_dates:
        return [
            "no acceptance entry in logs/decisions.md with a dated '### ' heading, a named "
            "approver ('accepted by ...'), and an explicit 'Verdict: accepted'"
        ]

    latest = max(accepted_dates)
    last_revised = coerce_date(contract.get("last_revised"))
    if last_revised and latest < last_revised:
        return [
            f"latest acceptance ({latest}) predates last_revised ({last_revised}); "
            "a fresh sample acceptance is required after a revision"
        ]
    return []


def main(argv):
    if len(argv) != 1:
        sys.exit("usage: check_promotion_gate.py <workflow_id>")
    workflow_id = argv[0]
    workflow_dir = os.path.join(REPO_ROOT, "workflows", workflow_id)
    contract_path = os.path.join(workflow_dir, "contract.yaml")
    if not os.path.isfile(contract_path):
        sys.exit(f"no contract at workflows/{workflow_id}/contract.yaml")

    with open(contract_path) as f:
        contract = yaml.safe_load(f) or {}

    print(f"Promotion gate — {workflow_id}\n")

    status = contract.get("status")
    status_ok = status in PROMOTABLE_FROM
    print(f"[{'PASS' if status_ok else 'FAIL'}] source status is promotable "
          f"(building|in_review|revising): got {status!r}")

    evals_ok, eval_lines = run_evals.evaluate_workflow(workflow_id)
    print(f"[{'PASS' if evals_ok else 'FAIL'}] gate 1 — evals pass at threshold")
    for line in eval_lines:
        print(f"        {line}")

    acceptance_errors = gate_acceptance(workflow_dir, contract)
    print(f"[{'PASS' if not acceptance_errors else 'FAIL'}] gate 2 — sample acceptance recorded")
    for e in acceptance_errors:
        print(f"        - {e}")

    sensitivity_errors = gate_sensitivity(contract)
    print(f"[{'PASS' if not sensitivity_errors else 'FAIL'}] gate 3 — sensitivity consistent")
    for e in sensitivity_errors:
        print(f"        - {e}")

    runbook_errors = gate_runbook(workflow_dir)
    print(f"[{'PASS' if not runbook_errors else 'FAIL'}] gate 4 — runbook complete")
    for e in runbook_errors:
        print(f"        - {e}")

    all_ok = status_ok and evals_ok and not acceptance_errors and not sensitivity_errors and not runbook_errors
    print(f"\n=> {'READY to promote' if all_ok else 'NOT ready — fix the failing gate(s)'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
