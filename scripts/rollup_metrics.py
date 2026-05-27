#!/usr/bin/env python3
"""Roll run-record verdicts up into a workflow's measured success metric.

The feedback connector the closed loop was missing (stages 5 -> 6 in
docs/plans/closed-loop-repo-assessment.md): nothing read run records and turned the
reviewer verdicts into a number. This script reads every committed run record for a
workflow (v0.5+ packet RUN_RECORD.md files and pre-v0.5 flat {timestamp}.yaml files),
computes the clean-send rate (the share of runs the reviewer approved with no edits),
writes it into the contract's success_metric.current_value, and appends one value
entry to portfolio/value-ledger.yaml.

Reproducible by construction, and it refuses rather than write a misleading value:
  - no run records          -> a workflow that never ran has no value to assert;
  - success_metric is not the clean-send rate, or human_review is not required
                            -> it would overwrite an unrelated metric;
  - any record is unfinished (success / decision still null)
                            -> it would silently skew the rate.
In every refusal it exits non-zero and leaves current_value untouched. A fabricated
number would be worse than null.

The contract and the ledger both carry hand-written comments, so this script edits
them surgically (one line / append-only) rather than round-tripping the whole file.

Usage:
    python scripts/rollup_metrics.py <workflow_id>
Exit code 0 if a metric was computed and written, 1 otherwise.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install it with: pip install -r requirements.txt")

REPO_ROOT = Path(__file__).resolve().parent.parent

# A "clean send" is a run the reviewer approved with no edits. approved_with_edits
# and rejected both count as runs (denominator) but not as clean sends (numerator).
CLEAN_DECISION = "approved"
VALID_DECISIONS = {"approved", "approved_with_edits", "rejected"}

# The clean-send rate is defined by reviewer sign-offs, so this script only applies to
# a workflow whose success_metric is that rate. The metric name is free-form in the
# contract, so identify it by this token (normalized) rather than overwriting whatever
# metric a workflow happens to declare.
CLEAN_SEND_TOKEN = "clean-send"

_YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
_CURRENT_VALUE_LINE = re.compile(r"^(?P<indent>[ \t]*)current_value:.*$", re.MULTILINE)
_ENTRIES_KEY = re.compile(r"^entries:", re.MULTILINE)


class RollupError(Exception):
    """A condition that must stop the rollup (e.g. no run records to measure)."""


def find_run_records(workflow_dir: Path) -> list[Path]:
    """Every committed run record for the workflow, in sorted (timestamp) order.

    Two record shapes are valid evidence (run-record schema + the v0.5 migration):
      - packet records    -- operations/run-records/{timestamp}/RUN_RECORD.md (v0.5+)
      - legacy flat files  -- operations/run-records/{timestamp}.yaml (pre-v0.5)
    Local-only *.local.yaml files are never committed evidence and are excluded.
    """
    run_dir = workflow_dir / "operations" / "run-records"
    packets = run_dir.glob("*/RUN_RECORD.md")
    flat = (p for p in run_dir.glob("*.yaml") if not p.name.endswith(".local.yaml"))
    return sorted([*packets, *flat])


def parse_run_record(path: Path) -> dict:
    """Parse a run record into its mapping.

    A packet RUN_RECORD.md carries the record in a fenced ```yaml block; a legacy flat
    {timestamp}.yaml file is the YAML document itself.
    """
    text = path.read_text()
    if path.suffix == ".md":
        match = _YAML_BLOCK.search(text)
        if match is None:
            raise RollupError(f"{path}: no ```yaml block found in run record")
        text = match.group(1)
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise RollupError(f"{path}: run-record YAML is not a mapping")
    return data


def decision_of(record: dict) -> str | None:
    signoff = record.get("reviewer_signoff")
    if isinstance(signoff, dict):
        return signoff.get("decision")
    return None


def assert_finished(path: Path, record: dict) -> None:
    """Refuse an unfinalized run record rather than count it as a non-clean send.

    A scaffolded-but-unfinished packet leaves success and reviewer_signoff.decision
    null; including it would silently lower the metric.
    """
    if record.get("success") is None:
        raise RollupError(
            f"{path}: run record is unfinished (success is null). Finalize or remove "
            "the packet before rolling up."
        )
    decision = decision_of(record)
    if decision not in VALID_DECISIONS:
        raise RollupError(
            f"{path}: run record has no reviewer decision yet ({decision!r}). Finalize "
            "or remove the packet before rolling up."
        )


def clean_send_rate(records: list[dict]) -> tuple[float, int, int]:
    """Return (rate, clean_count, total). Caller guarantees records is non-empty."""
    total = len(records)
    clean = sum(1 for record in records if decision_of(record) == CLEAN_DECISION)
    return clean / total, clean, total


def write_current_value(contract_path: Path, value: float) -> None:
    """Replace the single success_metric.current_value line, preserving comments."""
    text = contract_path.read_text()
    new_text, count = _CURRENT_VALUE_LINE.subn(
        lambda m: f"{m.group('indent')}current_value: {value}", text, count=1
    )
    if count != 1:
        raise RollupError(
            f"{contract_path}: expected exactly one 'current_value:' line, found {count}"
        )
    contract_path.write_text(new_text)


def append_ledger_entry(ledger_path: Path, entry: dict) -> None:
    """Append one entry to the value ledger, keeping its hand-written comment header."""
    raw = ledger_path.read_text()
    doc = yaml.safe_load(raw) or {}
    entries = list(doc.get("entries") or [])
    entries.append(entry)

    marker = _ENTRIES_KEY.search(raw)
    header = (raw[: marker.start()] if marker else raw).rstrip("\n")
    body = yaml.safe_dump(
        {"entries": entries},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    ledger_path.write_text(f"{header}\n{body}" if header else body)


def rollup(
    workflow_id: str,
    repo_root: Path | None = None,
    today: datetime.date | None = None,
) -> dict:
    """Compute the clean-send rate, write it to the contract, and log it to the ledger.

    Raises RollupError (without writing anything) when there is nothing to measure.
    """
    repo_root = repo_root or REPO_ROOT
    today = today or datetime.date.today()
    workflow_dir = repo_root / "workflows" / workflow_id
    contract_path = workflow_dir / "contract.yaml"
    if not contract_path.is_file():
        raise RollupError(f"no contract at {contract_path}")

    contract = yaml.safe_load(contract_path.read_text()) or {}
    human_review = contract.get("human_review") or {}
    metric = contract.get("success_metric") or {}
    metric_name = metric.get("name") or ""
    target = metric.get("target_value")

    # Only roll up workflows whose success_metric is the clean-send rate. The rate is
    # defined by reviewer sign-offs, so a workflow without required review, or with a
    # different metric entirely, must be refused rather than have its real metric
    # overwritten by an unrelated approval fraction.
    if not (isinstance(human_review, dict) and human_review.get("required")):
        raise RollupError(
            f"{workflow_id}: the clean-send rate is defined by reviewer sign-offs, but "
            "human_review.required is not true -- rollup_metrics does not apply here."
        )
    if CLEAN_SEND_TOKEN not in metric_name.lower().replace(" ", "-"):
        raise RollupError(
            f"{workflow_id}: success_metric.name is {metric_name!r}, not the clean-send "
            "rate -- rollup_metrics only computes that metric and will not overwrite a "
            "different one."
        )

    record_paths = find_run_records(workflow_dir)
    if not record_paths:
        raise RollupError(
            f"{workflow_id}: no run records under operations/run-records/ -- refusing "
            "to write a fabricated metric. Operate the workflow first (/run-workflow) "
            "so there is real feedback to measure."
        )

    records = []
    for path in record_paths:
        record = parse_run_record(path)
        assert_finished(path, record)
        records.append(record)
    rate, clean, total = clean_send_rate(records)
    value = round(rate, 4)

    write_current_value(contract_path, value)
    append_ledger_entry(
        ledger_path=repo_root / "portfolio" / "value-ledger.yaml",
        entry={
            "workflow_id": workflow_id,
            "date": today,
            "event": "value",
            "value": (
                f"{metric_name} measured at {value} across {total} production run "
                f"record(s): {clean} approved with no edits, {total - clean} not "
                "clean-send."
            ),
            "measurement": (
                f"{metric_name} = {clean}/{total} = {value} (target {target}); "
                f"computed by scripts/rollup_metrics.py from {total} RUN_RECORD.md "
                "file(s)."
            ),
            "notes": (
                "Derived from committed run records, not hand-entered. Small sample -- "
                "treat as directional, not authoritative."
            ),
        },
    )
    return {
        "workflow_id": workflow_id,
        "value": value,
        "clean": clean,
        "total": total,
        "target": target,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python scripts/rollup_metrics.py <workflow_id>", file=sys.stderr)
        return 1
    try:
        result = rollup(argv[0])
    except RollupError as exc:
        print(f"REFUSE {exc}", file=sys.stderr)
        return 1
    print(
        f"PASS {result['workflow_id']}: clean-send rate {result['value']} "
        f"({result['clean']}/{result['total']}) vs target {result['target']}"
    )
    print(
        "     wrote success_metric.current_value to the contract and appended a "
        "portfolio/value-ledger.yaml entry."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
