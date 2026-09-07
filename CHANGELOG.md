# Changelog

## v1.0.0 — 2026-09-07

First public release. Five-state harmonized dataset (Washington, Oregon, Colorado, Texas,
California) — 138 source documents, six per-state extractors, a re-execution gate
(`src/verify.py`), full per-file provenance (`SOURCES.csv`), and a pre-publication PII/sealing
safety review (`SAFETY_REVIEW.md`) covering all 138 files.

Washington and Oregon's underlying source-document corpus and safety review are shared with, and
match exactly, this project's earlier two-state academic-paper deposit (concept DOI
10.5281/zenodo.21436450, v1.1.0, published 2026-08-11) — this release adds Colorado, Texas, and
California as new coverage, and packages all five states as one dataset tracking the live public
dashboard at competencyrestoration.org, independent of that paper deposit's own version history.
