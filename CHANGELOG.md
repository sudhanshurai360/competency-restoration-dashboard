# Changelog

## v1.0.2 — Five data-accuracy corrections from a full source-PDF audit (PUBLISHED, 2026-09-11)

**Status:** PUBLISHED. Concept DOI `10.5281/zenodo.22652057` (unchanged); version DOI
`10.5281/zenodo.22712971`, confirmed live by direct query against Zenodo's own API. Note: a
`.zenodo.json` version-field fix (1.0.1 → 1.0.2) landed just after this release was cut, so
Zenodo's own metadata for this specific record still shows `version: 1.0.1` — the archived file
contents are correctly v1.0.2; only that one label is stale by one release.

A full, from-scratch audit checked every value in every dataset against the actual printed source
PDF (not against prior code comments, metadata, or automated spot-checks) before this data was
referenced with external contacts, including court officials and journalists. Found and fixed real
defects in all five states' extractors. No fabricated numbers were found anywhere — every issue
below is a completeness gap, a wrong-row selection, or a labeling/disclosure gap, not an invented
value.

- **Texas**: `waitlist_count` for `security_level=max` was pulled from Table 10's "Maximum
  Security" row — the not-yet-facility-assigned subset of the waitlist, per HHSC's own footnote
  ("people do not directly admit from the maximum security list") — instead of the Total row,
  which is the true full MSU waitlist. Understated the count by roughly 5-19% across all 8
  affected quarters (2023-11 through 2025-08; e.g. 2025-08: 419 shown, 484 actual).
- **California**: the dashboard's most recent reading was ~9 months stale (277, Aug 2025) while a
  newer figure (256, May 2026) sat unextracted in an already-downloaded PDF. Recovered 4 missing
  readings from a "Justification"-section sentence pattern with unambiguous dated footnotes.
- **Colorado (special master)**: roughly 28 `tier_wait_days_restoration` periods were 3-month
  rolling averages formatted identically to true single-month readings, with no way for a reader to
  tell which was which. Investigated changing which value ships, but the report's own prose treats
  the rolling average as its authoritative headline figure — instead added a purely additive
  `is_multi_month_avg` disclosure column (no value changed). One glued-dash header-parsing bug in
  this same column (found by an adversarial review) was also fixed.
- **Washington**: 24 rows were silently dropped whenever a table's day/percent columns were all
  genuinely "n/a" (zero completions that month) — the pipeline required a literal "%" cell to
  anchor column positions, so even the row's real, valid orders-signed/orders-completed counts were
  lost. Fixed by borrowing the column layout from a sibling row in the same table. Also
  hand-corrected 2 cells (`pct_within_alt3`, Jun-2022) where the source itself was revised between
  report vintages in a way the pipeline's own report-redundancy self-healing couldn't reach.
- **Oregon**: recovered one missing recent reading (Feb-2026, 16.5-day average) from the newest
  report's narrative text. The same sentence also states an admissions count (90), but that figure
  exists only inside a raster-image chart, not the extractable text layer — left genuinely blank
  rather than guessed.

Full per-finding detail, source-PDF verification, and independent adversarial review notes are
preserved in the originating session's working tree (not part of this public release, which carries
the corrected code and data, not the audit process itself).

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
