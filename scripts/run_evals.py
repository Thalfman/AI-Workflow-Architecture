#!/usr/bin/env python3
"""Run a workflow's eval cases offline and report the pass rate.

Makes "evals pass" executable without a model call or network. Offline, only the
structural grader can be auto-evaluated; the others need a freshly generated output
or a model:
  - structural : deterministic assertions about a committed output
                 (required_sections, must_include_all, must_exclude, max/min_words).
  - exact / semantic / llm-judge : need a generated output or a model, so they are
                 reported as manual-review-required and never silently passed.

Case structure: methodology/schemas/eval-case.schema.yaml. The bar is the contract's
evals.pass_threshold, computed over the gradable (structural) cases.

Usage:
    python scripts/run_evals.py <workflow_id>
    python scripts/run_evals.py --all
Exit code 0 if every evaluated workflow passes at threshold, 1 otherwise.
"""
from __future__ import annotations

import glob
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install it with: pip install -r requirements.txt")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, "workflows")

# Graders that cannot be evaluated offline (need a generated output or a model).
MANUAL_GRADERS = {"exact", "semantic", "llm-judge"}


def run_structural(text, checks):
    errors = []
    checks = checks or {}
    words = len(text.split())
    for section in checks.get("required_sections") or []:
        if section not in text:
            errors.append(f"missing required section: {section!r}")
    for token in checks.get("must_include_all") or []:
        if token not in text:
            errors.append(f"missing required token: {token!r}")
    for token in checks.get("must_exclude") or []:
        if token in text:
            errors.append(f"contains banned token: {token!r}")
    max_words = checks.get("max_words")
    if max_words is not None and words > max_words:
        errors.append(f"too long: {words} words > max_words {max_words}")
    min_words = checks.get("min_words")
    if min_words is not None and words < min_words:
        errors.append(f"too short: {words} words < min_words {min_words}")
    return errors


def grade_case(case, workflow_dir):
    """Return (status, detail) where status is PASS | FAIL | MANUAL."""
    grader = case.get("grader")
    expected = case.get("expected") or {}

    if grader == "structural":
        out_rel = expected.get("output")
        if not out_rel:
            return "FAIL", ["structural case missing expected.output"]
        out_path = os.path.join(workflow_dir, out_rel)
        if not os.path.exists(out_path):
            return "FAIL", [f"expected.output not found: {out_rel}"]
        with open(out_path) as f:
            text = f.read()
        errors = run_structural(text, expected.get("checks"))
        return ("PASS", []) if not errors else ("FAIL", errors)

    if grader in MANUAL_GRADERS:
        return "MANUAL", [f"{grader} needs a generated output or a model; not graded offline"]

    return "FAIL", [f"unknown grader: {grader!r}"]


def load_cases(workflow_dir, rel_path):
    """Return (cases, error). cases is a list; error is a message or None.

    A referenced-but-missing file is an error: the contract names both the test and
    regression paths, so a missing one (e.g. dropped regression coverage) must fail
    loudly rather than silently contribute zero cases.
    """
    path = os.path.join(workflow_dir, rel_path)
    if not os.path.exists(path):
        return [], f"{rel_path} does not exist"
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return [], f"{rel_path} is not valid YAML: {exc}"
    if data is None:
        return [], None
    if not isinstance(data, list):
        return [], f"{rel_path} is not a YAML list of cases"
    return data, None


def evaluate_workflow(workflow_id):
    """Evaluate one workflow. Return (passed: bool, lines: list[str])."""
    workflow_dir = os.path.join(WORKFLOWS_DIR, workflow_id)
    contract_path = os.path.join(workflow_dir, "contract.yaml")
    if not os.path.exists(contract_path):
        return False, [f"{workflow_id}: no contract at {os.path.relpath(contract_path, REPO_ROOT)}"]

    try:
        with open(contract_path) as f:
            contract = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        return False, [f"{workflow_id}: contract.yaml is not valid YAML: {exc}"]
    if not isinstance(contract, dict):
        return False, [f"{workflow_id}: contract.yaml is not a mapping"]

    evals = contract.get("evals")
    if not isinstance(evals, dict):
        return False, [f"{workflow_id}: evals is not a mapping"]

    threshold_raw = evals.get("pass_threshold", 1.0)
    if isinstance(threshold_raw, bool) or not isinstance(threshold_raw, (int, float)):
        try:
            threshold = float(threshold_raw)
        except (TypeError, ValueError):
            return False, [f"{workflow_id}: evals.pass_threshold is not numeric: {threshold_raw!r}"]
    else:
        threshold = float(threshold_raw)

    cases = []
    load_errors = []
    for rel in (
        evals.get("test_cases_path") or "evals/test-cases.yaml",
        evals.get("regression_cases_path") or "evals/regression-cases.yaml",
    ):
        loaded, err = load_cases(workflow_dir, rel)
        if err:
            load_errors.append(err)
        else:
            cases.extend(loaded)
    if load_errors:
        return False, [f"{workflow_id}: malformed eval file(s)"] + [f"  - {e}" for e in load_errors]

    lines = []
    gradable = 0
    passed = 0
    manual = 0
    for case in cases:
        if not isinstance(case, dict):
            gradable += 1
            lines.append(f"  FAIL   <malformed case>: expected a mapping, got {type(case).__name__}")
            continue
        status, detail = grade_case(case, workflow_dir)
        cid = case.get("id", "?")
        if status == "MANUAL":
            manual += 1
            lines.append(f"  MANUAL {cid}: {detail[0]}")
            continue
        gradable += 1
        if status == "PASS":
            passed += 1
            lines.append(f"  PASS   {cid}: {case.get('description', '')}")
        else:
            lines.append(f"  FAIL   {cid}: {case.get('description', '')}")
            for d in detail:
                lines.append(f"           - {d}")

    rate = (passed / gradable) if gradable else 0.0
    meets = gradable > 0 and rate >= threshold
    header = (
        f"{workflow_id}: {passed}/{gradable} gradable cases passed "
        f"(rate {rate:.2f} vs threshold {threshold})"
        + (f", {manual} manual-review-required" if manual else "")
    )
    if gradable == 0:
        header += " — no gradable cases (cannot auto-pass)"
    lines.insert(0, header)
    return meets, lines


def active_workflow_ids():
    ids = []
    for path in sorted(glob.glob(os.path.join(WORKFLOWS_DIR, "*", "contract.yaml"))):
        ids.append(os.path.basename(os.path.dirname(path)))
    return ids


def main(argv):
    if len(argv) != 1:
        sys.exit("usage: run_evals.py <workflow_id> | --all")
    target = argv[0]
    workflow_ids = active_workflow_ids() if target == "--all" else [target]
    if not workflow_ids:
        print("No active workflows to evaluate.")
        return 0

    all_passed = True
    for wid in workflow_ids:
        passed, lines = evaluate_workflow(wid)
        all_passed = all_passed and passed
        print("\n".join(lines))
        print(f"  => {'PASS' if passed else 'FAIL'}\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
