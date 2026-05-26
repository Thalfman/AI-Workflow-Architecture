#!/usr/bin/env python3
"""Operator control script for workflow runs.

Executable backbone of /run-workflow (methodology/commands/run-workflow.md). The
`run` subcommand does only the deterministic, model-free part of a run: it creates
the run-packet folder, copies the production prompt into the packet, hashes the
inputs, and stubs the six packet files from methodology/templates/run-packet/. It
never generates or reviews output and never sends anything — those stay
operator-driven (operator + Claude), exactly as the command spec states.

Run records are append-only evidence. This script refuses to run a non-production
workflow and refuses to overwrite an existing packet.

Usage:
    python scripts/workflowctl.py run <workflow_id> --input <folder>
Exit code 0 if a complete packet skeleton was written, 1 otherwise.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install it with: pip install -r requirements.txt")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(REPO_ROOT, "methodology", "templates", "run-packet")

# The six packet files, in the order the command spec lists them. Content-bearing
# files (the raw draft and final output) are kept out of version control for any
# workflow above public sensitivity by saving them with a .local.md suffix, which
# .gitignore excludes.
PACKET_FILES = ["INPUTS.md", "PROMPT_USED.md", "OUTPUT_DRAFT.md", "REVIEW.md", "FINAL_OUTPUT.md", "RUN_RECORD.md"]
CONTENT_BEARING = {"OUTPUT_DRAFT.md", "FINAL_OUTPUT.md"}


def fail(message):
    print(f"FAIL {message}")
    return 1


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def gather_inputs(input_dir):
    """Return a sorted list of (relative_path, sha256) for every regular file.

    Hidden files and .gitkeep placeholders are skipped — they are not run inputs.
    """
    found = []
    for root, _dirs, files in os.walk(input_dir):
        for name in files:
            if name.startswith(".") or name == ".gitkeep":
                continue
            abspath = os.path.join(root, name)
            rel = os.path.relpath(abspath, input_dir)
            found.append((rel, sha256_file(abspath)))
    found.sort(key=lambda item: item[0])
    return found


def combined_hash(file_hashes):
    """A deterministic hash over (relative name + per-file hash), order-independent
    because the inputs are sorted by name first."""
    h = hashlib.sha256()
    for rel, digest in file_hashes:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(digest.encode("utf-8"))
    return h.hexdigest()


def read_template(name):
    with open(os.path.join(TEMPLATE_DIR, name)) as f:
        return f.read()


def reviewer_signoff_block(contract):
    review = contract.get("human_review")
    required = isinstance(review, dict) and bool(review.get("required"))
    if required:
        return (
            "reviewer_signoff:               # contract.human_review.required is true\n"
            "  reviewer: null                # TODO who reviewed\n"
            "  decision: null                # TODO approved | approved_with_edits | rejected\n"
            "  at: null                      # TODO ISO 8601 review time"
        )
    return "reviewer_signoff: null          # contract.human_review.required is false"


def input_table(file_hashes):
    if not file_hashes:
        return "_(no input files found)_"
    lines = ["| File | sha256 |", "|---|---|"]
    for rel, digest in file_hashes:
        lines.append(f"| `{rel}` | `{digest}` |")
    return "\n".join(lines)


def render_packet(contract, workflow_id, iso_timestamp, file_hashes, prompt_body, prompt_source, content_suffix):
    combined = combined_hash(file_hashes)
    substitutions = {
        "{{RUN_TIMESTAMP}}": iso_timestamp,
        "{{TIMESTAMP}}": iso_timestamp,
        "{{INPUT_HASH}}": combined,
        "{{INPUT_TABLE}}": input_table(file_hashes),
        "{{PROMPT_BODY}}": prompt_body,
        "{{PROMPT_SOURCE}}": prompt_source,
        "{{REVIEWER_SIGNOFF}}": reviewer_signoff_block(contract),
    }
    rendered = {}
    for name in PACKET_FILES:
        text = read_template(name)
        for token, value in substitutions.items():
            text = text.replace(token, value)
        out_name = name.replace(".md", content_suffix) if name in CONTENT_BEARING else name
        rendered[out_name] = text
    return rendered, combined


def cmd_run(args):
    workflow_id = args.workflow_id
    workflow_dir = os.path.join(REPO_ROOT, "workflows", workflow_id)
    contract_path = os.path.join(workflow_dir, "contract.yaml")
    if not os.path.isfile(contract_path):
        return fail(f"no contract at workflows/{workflow_id}/contract.yaml")

    with open(contract_path) as f:
        contract = yaml.safe_load(f) or {}
    if not isinstance(contract, dict):
        return fail(f"workflows/{workflow_id}/contract.yaml is not a mapping")

    status = contract.get("status")
    if status != "production":
        return fail(
            f"workflow {workflow_id!r} is {status!r}, not 'production' — a run requires a "
            "production workflow. Route to /scope, /promote-workflow, or /revise-workflow instead."
        )

    prompt_source = os.path.join("workflows", workflow_id, "agent", "production.prompt.md")
    prompt_path = os.path.join(REPO_ROOT, prompt_source)
    if not os.path.isfile(prompt_path):
        return fail(f"production prompt missing: {prompt_source}")
    with open(prompt_path) as f:
        prompt_body = f.read().strip()

    input_dir = os.path.abspath(args.input)
    if not os.path.isdir(input_dir):
        return fail(f"input folder does not exist: {args.input}")
    file_hashes = gather_inputs(input_dir)
    if not file_hashes:
        return fail(f"no input files found in {args.input}")

    now = datetime.datetime.now(datetime.timezone.utc)
    folder_name = now.strftime("%Y%m%dT%H%M%SZ")
    iso_timestamp = now.replace(microsecond=0).isoformat()
    packet_dir = os.path.join(workflow_dir, "operations", "run-records", folder_name)
    if os.path.exists(packet_dir):
        return fail(f"packet already exists: {os.path.relpath(packet_dir, REPO_ROOT)}")

    max_sens = contract.get("max_sensitivity")
    content_suffix = ".md" if max_sens == "public" else ".local.md"

    rendered, combined = render_packet(
        contract, workflow_id, iso_timestamp, file_hashes, prompt_body, prompt_source, content_suffix
    )

    os.makedirs(packet_dir)
    for name, text in rendered.items():
        with open(os.path.join(packet_dir, name), "w") as f:
            f.write(text if text.endswith("\n") else text + "\n")

    rel_packet = os.path.relpath(packet_dir, REPO_ROOT)
    print(f"PASS scaffolded run packet: {rel_packet}")
    print(f"     {len(file_hashes)} input file(s), combined sha256 {combined[:16]}…")
    print(f"     content files use '{content_suffix}' (max_sensitivity: {max_sens})")
    print("     Next (operator + Claude): generate OUTPUT_DRAFT, run the reviewer into REVIEW,")
    print("     finalize FINAL_OUTPUT, then fill output_hash/success/sign-off in RUN_RECORD.md.")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="Operator control script for workflow runs.")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="scaffold a run packet for a production workflow")
    run_parser.add_argument("workflow_id", help="the workflow_id to run")
    run_parser.add_argument("--input", required=True, help="folder holding this run's input files")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
