#!/usr/bin/env python3
"""Validate workflow contracts against the canonical structure.

Checks every workflows/*/contract.yaml (and workflows/retired/*) for the required
fields, enum values, sensitivity rules, and referenced eval paths described by
methodology/schemas/contract.schema.yaml. That schema file is the canonical
STRUCTURAL GUIDE, not a formal/machine-readable JSON Schema, so this script
implements the minimum executable checks that mirror it. If the schema doc
changes, update these checks in the same commit.

Usage:
    python scripts/validate_contracts.py
Exit code 0 if every contract is valid, 1 otherwise.
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

# Required top-level fields, per methodology/schemas/contract.schema.yaml.
REQUIRED_TOP_LEVEL = [
    "workflow_id", "workflow_name", "owner", "requester", "status",
    "methodology_version", "contract_schema_version", "created", "last_revised",
    "trigger", "inputs", "outputs", "definition_of_good", "acceptance_criteria",
    "success_metric", "human_review", "max_sensitivity", "data_handling",
    "dependencies", "evals",
]

STATUS = {"scoping", "building", "in_review", "production", "revising", "retired"}
TRIGGER_TYPES = {"schedule", "event", "manual"}
SENSITIVITY_ORDER = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
REVIEW_POINTS = {"pre_send", "post_send", "sample_only"}


def contract_paths():
    paths = glob.glob(os.path.join(REPO_ROOT, "workflows", "*", "contract.yaml"))
    paths += glob.glob(os.path.join(REPO_ROOT, "workflows", "retired", "*", "contract.yaml"))
    return sorted(set(paths))


def validate(path):
    errors = []
    try:
        with open(path) as f:
            contract = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return [f"unparseable YAML: {exc}"]

    if not isinstance(contract, dict):
        return ["contract is not a YAML mapping"]

    for key in REQUIRED_TOP_LEVEL:
        if contract.get(key) in (None, ""):
            errors.append(f"missing required field: {key}")

    status = contract.get("status")
    if status is not None and status not in STATUS:
        errors.append(f"invalid status: {status!r} (expected one of {sorted(STATUS)})")

    trigger = contract.get("trigger")
    if isinstance(trigger, dict):
        ttype = trigger.get("type")
        if ttype is not None and ttype not in TRIGGER_TYPES:
            errors.append(f"invalid trigger.type: {ttype!r} (expected one of {sorted(TRIGGER_TYPES)})")

    max_sens = contract.get("max_sensitivity")
    if max_sens is not None and max_sens not in SENSITIVITY_ORDER:
        errors.append(f"invalid max_sensitivity: {max_sens!r}")

    human_review = contract.get("human_review")
    if isinstance(human_review, dict):
        rp = human_review.get("review_point")
        if rp is not None and rp not in REVIEW_POINTS:
            errors.append(f"invalid human_review.review_point: {rp!r}")

    inputs = contract.get("inputs")
    if isinstance(inputs, list):
        for i, inp in enumerate(inputs):
            if not isinstance(inp, dict):
                errors.append(f"inputs[{i}] is not a mapping")
                continue
            sensitivity = inp.get("sensitivity")
            if sensitivity is None:
                continue
            if sensitivity not in SENSITIVITY_ORDER:
                errors.append(f"inputs[{i}].sensitivity invalid: {sensitivity!r}")
            elif max_sens in SENSITIVITY_ORDER and SENSITIVITY_ORDER[sensitivity] > SENSITIVITY_ORDER[max_sens]:
                errors.append(
                    f"inputs[{i}].sensitivity ({sensitivity}) exceeds max_sensitivity ({max_sens})"
                )

    evals = contract.get("evals")
    if isinstance(evals, dict):
        workflow_dir = os.path.dirname(path)
        for key in ("test_cases_path", "regression_cases_path"):
            rel = evals.get(key)
            if not rel:
                errors.append(f"evals.{key} is missing")
            elif not os.path.exists(os.path.join(workflow_dir, rel)):
                errors.append(f"evals.{key} -> {rel} does not exist")
        threshold = evals.get("pass_threshold")
        if threshold is None:
            errors.append("evals.pass_threshold is missing")
        elif isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            errors.append(f"evals.pass_threshold must be numeric, got {threshold!r}")

    return errors


def main():
    paths = contract_paths()
    if not paths:
        print("No contracts found (empty library). OK.")
        return 0

    failed = 0
    for path in paths:
        rel = os.path.relpath(path, REPO_ROOT)
        errors = validate(path)
        if errors:
            failed += 1
            print(f"FAIL {rel}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS {rel}")

    print(f"\n{len(paths) - failed}/{len(paths)} contract(s) valid.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
