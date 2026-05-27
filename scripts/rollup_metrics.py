#!/usr/bin/env python3
"""Roll run-record verdicts up into a workflow's measured success metric.

The feedback connector the closed loop was missing (stages 5 -> 6 in
docs/plans/closed-loop-repo-assessment.md): nothing read run packets and turned the
reviewer verdicts into a number. This script reads every RUN_RECORD.md under
workflows/{id}/operations/run-records/, computes the clean-send rate (the share of
runs the reviewer approved with no edits), writes it into the contract's
success_metric.current_value, and appends one value entry to
portfolio/value-ledger.yaml.

Reproducible by construction: the value is derived from committed run records, never
hand-typed. If a workflow has no run records the script REFUSES to write and exits
non-zero -- a workflow that has never run has no measured value to assert, and a
fabricated number would be worse than null.

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

_YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
_CURRENT_VALUE_LINE = re.compile(r"^(?P<indent>[ \t]*)current_value:.*$", re.MULTILINE)
_ENTRIES_KEY = re.compile(r"^entries:", re.MULTILINE)


class RollupError(Exception):
    """A condition that must stop the rollup (e.g. no run records to measure)."""


def find_run_records(workflow_dir: Path) -> list[Path]:
    """Every packet's RUN_RECORD.md, sorted by packet folder (i.e. by timestamp)."""
    run_dir = workflow_dir / "operations" / "run-records"
    return sorted(run_dir.glob("*/RUN_RECORD.md"))


def parse_run_record(path: Path) -> dict:
    """Extract and parse the fenced YAML block from a RUN_RECORD.md."""
    match = _YAML_BLOCK.search(path.read_text())
    if match is None:
        raise RollupError(f"{path}: no ```yaml block found in run record")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise RollupError(f"{path}: run-record YAML is not a mapping")
    return data


def decision_of(record: dict) -> str | None:
    signoff = record.get("reviewer_signoff")
    if isinstance(signoff, dict):
        return signoff.get("decision")
    return None


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
    metric = contract.get("success_metric") or {}
    metric_name = metric.get("name") or "Clean-send rate"
    target = metric.get("target_value")

    record_paths = find_run_records(workflow_dir)
    if not record_paths:
        raise RollupError(
            f"{workflow_id}: no run records under operations/run-records/ -- refusing "
            "to write a fabricated metric. Operate the workflow first (/run-workflow) "
            "so there is real feedback to measure."
        )

    records = [parse_run_record(path) for path in record_paths]
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
