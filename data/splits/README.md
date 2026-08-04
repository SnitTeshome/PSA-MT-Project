# `data/splits/` — train/dev/test splits and backend-comparison benchmarks

- **`agriculture/`** — per-language train/val/test splits (Dholuo, Ekegusii,
  Kiswahili, Somali) used for the Week 3/4 backend comparisons documented in
  `docs/ekegusii_transfer_learning.md` and `docs/week4_swahili_dholuo_summary.md`.
- **`crossdomain/`** — held-out benchmark sets spanning multiple domains (not just
  Agriculture), used for the cross-domain generalization checks in
  `docs/ekegusii_transfer_learning.md` §22-23 and `docs/results_summary.md`. Result
  files here are named after the specific backend each one scored (e.g. one file is
  named for the cloud translation API used to produce it) — kept as originally
  written for traceability rather than renamed.
