"""Tests for scripts/rollup_metrics.py -- the closed-loop measurement connector.

Proves the loop works: given run records with known reviewer verdicts, the rollup
computes the clean-send rate, writes it into the contract, and appends one value
ledger entry. The negative cases prove it refuses (and exits non-zero, leaving
current_value null) rather than write a misleading value -- when there are no
records, when an unfinished packet is present, or when the workflow's metric is not
the clean-send rate.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest
import yaml

import rollup_metrics as rm

FIXED_DAY = datetime.date(2026, 5, 27)


def write_contract(
    workflow_dir: Path,
    current_value: str = "null",
    metric_name: str = "Clean-send rate",
    human_review_required: bool = True,
    review_point: str = "pre_send",
    status: str = "production",
) -> Path:
    workflow_dir.mkdir(parents=True, exist_ok=True)
    contract = workflow_dir / "contract.yaml"
    contract.write_text(
        "# a hand-written contract with comments to preserve\n"
        "workflow_id: sample\n"
        f"status: {status}\n"
        "human_review:\n"
        f"  required: {str(human_review_required).lower()}\n"
        f"  review_point: {review_point}\n"
        "success_metric:\n"
        f"  name: {metric_name}\n"
        f"  current_value: {current_value}\n"
        '  target_value: ">= 0.9"\n'
    )
    return contract


def write_record(run_dir: Path, name: str, decision: str) -> None:
    """A finalized v0.5+ packet record (RUN_RECORD.md with a fenced YAML block)."""
    packet = run_dir / name
    packet.mkdir(parents=True)
    (packet / "RUN_RECORD.md").write_text(
        "# Run record\n\n"
        "```yaml\n"
        "timestamp: 2026-05-01T16:00:00+00:00\n"
        "input_hash: aaa\n"
        "output_hash: bbb\n"
        "success: true\n"
        "reviewer_signoff:\n"
        "  reviewer: Operator\n"
        f"  decision: {decision}\n"
        "  at: 2026-05-01T16:00:00+00:00\n"
        "anomalies: null\n"
        "```\n"
    )


def write_unfinished_record(run_dir: Path, name: str) -> None:
    """A scaffolded-but-unfinalized packet: success and decision still null."""
    packet = run_dir / name
    packet.mkdir(parents=True)
    (packet / "RUN_RECORD.md").write_text(
        "# Run record\n\n"
        "```yaml\n"
        "timestamp: 2026-05-01T16:00:00+00:00\n"
        "input_hash: aaa\n"
        "output_hash: null\n"
        "success: null\n"
        "reviewer_signoff:\n"
        "  reviewer: null\n"
        "  decision: null\n"
        "  at: null\n"
        "anomalies: null\n"
        "```\n"
    )


def write_flat_record(run_dir: Path, name: str, decision: str) -> None:
    """A pre-v0.5 flat {timestamp}.yaml record (the YAML document itself)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / name).write_text(
        "timestamp: 2026-04-24T16:00:00+00:00\n"
        "input_hash: ccc\n"
        "output_hash: ddd\n"
        "success: true\n"
        "reviewer_signoff:\n"
        "  reviewer: Operator\n"
        f"  decision: {decision}\n"
        "  at: 2026-04-24T16:00:00+00:00\n"
        "anomalies: null\n"
    )


def write_ledger(repo_root: Path) -> Path:
    portfolio = repo_root / "portfolio"
    portfolio.mkdir(parents=True, exist_ok=True)
    ledger = portfolio / "value-ledger.yaml"
    ledger.write_text("# Value ledger -- hand-maintained, append-only.\nentries: []\n")
    return ledger


def test_clean_send_rate_counts_only_approved() -> None:
    records = [
        {"reviewer_signoff": {"decision": "approved"}},
        {"reviewer_signoff": {"decision": "approved_with_edits"}},
        {"reviewer_signoff": {"decision": "approved"}},
        {"reviewer_signoff": {"decision": "rejected"}},
    ]
    rate, clean, total = rm.clean_send_rate(records)
    assert (clean, total) == (2, 4)
    assert rate == 0.5


def test_rollup_writes_value_and_one_ledger_entry(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir)
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_record(run_dir, "20260508T160000Z", "approved_with_edits")
    write_record(run_dir, "20260515T160000Z", "approved")
    ledger = write_ledger(tmp_path)

    result = rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    assert result["clean"] == 2
    assert result["total"] == 3
    assert result["value"] == 0.6667

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] == 0.6667

    ledger_text = ledger.read_text()
    assert ledger_text.startswith("# Value ledger")  # comment header preserved
    entries = yaml.safe_load(ledger_text)["entries"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["workflow_id"] == "sample"
    assert entry["event"] == "value"
    assert entry["date"] == FIXED_DAY
    assert "2/3" in entry["measurement"]


def test_rollup_includes_legacy_flat_records(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    write_contract(workflow_dir)
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_flat_record(run_dir, "20260424T160000Z.yaml", "rejected")
    write_ledger(tmp_path)

    result = rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    # The flat record is counted: total 2 (not 1), one of which is not a clean send.
    assert result["total"] == 2
    assert result["clean"] == 1
    assert result["value"] == 0.5


def test_rollup_refuses_with_no_records_and_leaves_value_null(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir)
    (workflow_dir / "operations" / "run-records").mkdir(parents=True)
    ledger = write_ledger(tmp_path)

    with pytest.raises(rm.RollupError):
        rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] is None
    assert yaml.safe_load(ledger.read_text())["entries"] == []


def test_rollup_refuses_unfinished_record(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir)
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_unfinished_record(run_dir, "20260508T160000Z")
    ledger = write_ledger(tmp_path)

    with pytest.raises(rm.RollupError):
        rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] is None
    assert yaml.safe_load(ledger.read_text())["entries"] == []


def test_rollup_refuses_non_clean_send_metric(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir, metric_name="Turnaround time")
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_ledger(tmp_path)

    with pytest.raises(rm.RollupError):
        rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] is None


def test_rollup_refuses_when_human_review_not_required(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir, human_review_required=False)
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_ledger(tmp_path)

    with pytest.raises(rm.RollupError):
        rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] is None


def test_rollup_refuses_non_pre_send_review(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir, review_point="post_send")
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_ledger(tmp_path)

    with pytest.raises(rm.RollupError):
        rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] is None


def test_rollup_refuses_non_production_status(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    contract = write_contract(workflow_dir, status="revising")
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_ledger(tmp_path)

    with pytest.raises(rm.RollupError):
        rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)

    contract_data = yaml.safe_load(contract.read_text())
    assert contract_data["success_metric"]["current_value"] is None


def test_rollup_is_idempotent_on_rerun(tmp_path: Path) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    write_contract(workflow_dir)
    run_dir = workflow_dir / "operations" / "run-records"
    write_record(run_dir, "20260501T160000Z", "approved")
    write_record(run_dir, "20260515T160000Z", "approved")
    ledger = write_ledger(tmp_path)

    rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)
    rm.rollup("sample", repo_root=tmp_path, today=FIXED_DAY)  # same day rerun
    rm.rollup(
        "sample", repo_root=tmp_path, today=datetime.date(2026, 6, 3)
    )  # later day

    # Same records and result -> one ledger entry, no duplicates across reruns.
    entries = yaml.safe_load(ledger.read_text())["entries"]
    assert len(entries) == 1


def test_main_refuses_and_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workflow_dir = tmp_path / "workflows" / "sample"
    write_contract(workflow_dir)
    (workflow_dir / "operations" / "run-records").mkdir(parents=True)
    write_ledger(tmp_path)
    monkeypatch.setattr(rm, "REPO_ROOT", tmp_path)

    assert rm.main(["sample"]) == 1
    assert "REFUSE" in capsys.readouterr().err
