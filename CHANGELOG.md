# Changelog

## v1.0.1 — Colorado JBC documents added, permission confirmed (PUBLISHED, 2026-09-10)

**Status:** PUBLISHED. Concept DOI `10.5281/zenodo.22652057` (unchanged, always resolves to the
latest version); version DOI `10.5281/zenodo.22697301`, confirmed live by direct query against
Zenodo's own API (`version: "1.0.1"`, `publication_date: "2026-09-10"`) after the GitHub release
(`v1.0.1`) triggered the existing GitHub-Zenodo webhook integration.

The 3 Colorado Joint Budget Committee documents held back from v1.0.0 (`jbc_memo.pdf`,
`fy2024-25_humbrf2.5.pdf`, `fy2025-26_humbrf1.5.pdf`) are now bundled in `data/raw/co/`. JBC staff
(Jessi Neuberg) confirmed by email on 2026-09-10, in reply to the request sent 2026-09-07: "Yes,
all of our documents are public documents, so you are free to include them." This is now the
strongest rights basis of any document type in this archive — explicit written permission, not an
inference from fair-use doctrine.

138 of 138 provenanced source documents are now bundled (was 135 of 138 in v1.0.0). File integrity
verified before bundling: all 3 files' SHA-256 hashes match the values already on record in
`SOURCES.csv` since v1.0.0 (these files were hashed and safety-reviewed then; only their bundling
status changes now). Updated `README.md`, `data/raw/NOTICE`, `data/raw/co/README.md`,
`SAFETY_REVIEW.md`, and `docs/SOURCES.md` to reflect the new counts and rights basis; no change to
`SOURCES.csv` (it already carried correct metadata for these 3 files) or to any derived dataset
(`colorado_jbc.csv` was already built from data extracted before this bundling change).

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
