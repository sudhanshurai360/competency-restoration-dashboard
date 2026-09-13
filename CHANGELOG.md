# Changelog

## v1.0.3 — Three further independent audit rounds; new Texas attrition metric (PUBLISHED, 2026-09-12)

**Status:** PUBLISHED. Concept DOI `10.5281/zenodo.22652057` (unchanged); version DOI TBD, to be
confirmed live via Zenodo's own API and recorded in a follow-up commit, per this project's usual
practice.

After v1.0.2, three further rounds of independent, differently-lensed review were run against the
private working tree (10 reviewers each, two per state): a numeric-fidelity/completeness pass, a
blind independent-rebuild/date-arithmetic pass, and a final site-integrity/fresh-reverification
pass. The last of these found zero new data-correctness issues — every fix from the prior two
rounds independently re-checked clean against the raw source PDFs. This release ports the real,
confirmed findings from all three rounds into this public archive.

- **Washington**: recovered 40 previously-missing facility/stage/setting-months (Oct 2017–Aug
  2018) that fell entirely outside every later report's own redundancy window — a font-metrics
  quirk specific to 3 report vintages (`Trueblood-Report-2018-11.pdf`, `-2018-12.pdf`,
  `-2019-01.pdf`) defeated `pdfplumber`'s default word-boundary detection for these tables'
  inpatient rows. Fixed via a dedicated extraction fallback gated on exactly those 3 files.
- **Colorado (special master)**: recovered 20 previously-missing `tier_wait_days_restoration` rows
  (10 months × 2 tiers) from a table format the extractor didn't yet parse (month-per-row rather
  than the corpus's usual tier-per-row layout), plus OCR-recovered 6 more `tier_waitlist_count`
  rows from a second cid-encoded page in `sm_2024-11-28.pdf`. Also resolved the 14 rows whose
  `is_multi_month_avg` flag (added v1.0.2) shipped blank — traced to 2 header-parsing bugs (a
  glued fiscal-year token format, and a 45px-radius header-word assignment that could satisfy two
  adjacent narrow columns at once); every row now resolves to `True` or `False`, no underlying
  `value` changed.
- **Texas**: added `removed_count` — a new metric, the number of people removed from each
  security level's waitlist per quarter (a flow figure, not previously in the dataset), with its
  own `pdf_page_removed`/`table_ref_removed` citation columns. Also hardened era-detection (the
  extractor now checks for `Table 10`'s presence rather than a hardcoded fiscal-quarter string,
  closing a break risk for the next report vintage) and table-lookup (skips sub-numbered
  cross-reference decoys like "Table 7.2." that share a match prefix with the real table).
- **Oregon**: recovered 3 more missing readings (`waitlist_count` 2025-04; `avg_wait_days` for
  2 additional periods) from narrative-text patterns not previously matched, and fixed a
  date-resolution bug where a bare month reference in a two-date sentence was resolved to the
  nearer-but-wrong of the two dates rather than the correct one.
- **California**: recovered 2 more historical Pre/Post-SIP-order waitlist readings (2020-03=869,
  2020-05=1144) from a fixed reference table not previously parsed, and fixed a latent citation
  bug where a value matched across a PDF page break could cite the wrong page (no shipped value
  was affected).
- **Colorado (JBC)**: corrected a docstring claim about the source reports' table structure;
  disclosed (not yet built) a larger monthly time series present in one report that this pipeline
  doesn't currently extract.

Also hardened several extractors against edge cases confirmed to affect no currently-shipped
value: Colorado's year-arithmetic for a glued fiscal-year header token, and removal of a
cross-token year-propagation fallback confirmed to be dead code against the current corpus (a
token now resolves a year only from its own text, never a neighboring column's).

Separately, this release corrects 9 stale or incorrect comments found by a pre-publication
comment audit — mostly comments still saying `data/raw/<state>/` (this archive's own convention)
that had been copied from the private working tree's `dashboard_data/raw/<state>/` wording, plus
one outdated file count and one already-fixed "produces 0 rows" claim for `sm_2024-11-28.pdf`
(now OCR-recovered, not blank). No functional code changed as part of that pass.

**Fixed a reproducibility gap**: `co_special_master.py`'s OCR recovery path for `sm_2024-11-28.pdf`
(added in v1.0.2, now extended to a second page of that file) depends on `pytesseract` and the
separate `tesseract` system binary — neither was declared in `requirements.txt` or `README.md`,
so a clean `pip install -r requirements.txt && python src/verify.py` following v1.0.2's own
instructions would have crashed on this one file for anyone without `tesseract` already installed.
Both are now documented; see `README.md`'s Setup section.

Full per-finding detail and independent adversarial review notes are preserved in the originating
session's working tree (not part of this public release, which carries the corrected code and
data, not the audit process itself).

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
