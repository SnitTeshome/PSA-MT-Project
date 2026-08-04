# `04_quality_checked/` — deduplicated and QC'd generation output

Stage 4 of the restructured pipeline: output of running the synthetic rows from
`03_generated/` through dedup (exact + fuzzy) and rule-based quality checks.

- `deduped.json` — post-dedup output.
- `quality_checked.json` — post-QC output.
- `quality_report.txt` — human-readable summary of what the QC pass caught/flagged.

Feeds into `05_translated/`.
