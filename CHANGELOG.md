# Changelog

## v1.0.0 — published version (PUBLISHED, 2026-09-08)

**Status:** PUBLISHED. Concept DOI `10.5281/zenodo.22652057`; version DOI
`10.5281/zenodo.22652058`.

First public release. Five-state harmonized dataset (Washington, Oregon, Colorado, Texas,
California) — 138 source documents with full provenance (`SOURCES.csv`), 135 of them actually
bundled as PDF files (Colorado's 3 Joint Budget Committee documents are withheld pending a direct
confirmation request to JBC staff — see `data/raw/co/README.md`), six per-state extractors, a
re-execution gate (`src/verify.py`), and a pre-publication PII/sealing safety review
(`SAFETY_REVIEW.md`) covering all 138 reviewed documents.

Washington and Oregon's underlying source-document corpus and safety review are shared with, and
match exactly, this project's earlier two-state academic-paper deposit (concept DOI
10.5281/zenodo.21436450, v1.1.0, published 2026-08-11) — this release adds Colorado, Texas, and
California as new coverage, and packages all five states as one dataset tracking the live public
dashboard at competencyrestoration.org, independent of that paper deposit's own version history.
