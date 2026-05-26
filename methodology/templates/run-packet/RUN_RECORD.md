# Run record — this run

The machine-readable evidence that this run happened and how it went. The YAML block
below conforms to `methodology/schemas/run-record.schema.yaml`. This file is
committed: it carries no raw input or output text — only hashes and the sign-off.

```yaml
timestamp: {{TIMESTAMP}}        # ISO 8601, when the run occurred
input_hash: {{INPUT_HASH}}      # sha256 of the run's inputs (see INPUTS.md)
output_hash: null               # TODO sha256 of FINAL_OUTPUT once produced
success: null                   # TODO true once an acceptable deliverable is produced

{{REVIEWER_SIGNOFF}}
anomalies: null                 # nullable — retries, degraded inputs, manual steps, near-misses
```
