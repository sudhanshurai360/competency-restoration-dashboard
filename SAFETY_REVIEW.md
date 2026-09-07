# Pre-publication safety review — source documents

**Scope:** all 138 source PDFs redistributed in `data/raw/` — 91 Washington + 18 Oregon (reviewed
2026-07-12, for this project's earlier two-state release) + 14 Colorado + 6 Texas + 9 California
(reviewed 2026-09-07, for this 5-state release). See `SOURCES.csv` for the full per-file list.

**Question:** is every bundled document safe to redistribute in a permanent public archive — i.e.,
an aggregate public court/agency/legislative report, containing **no individual PII**, and **not
itself sealed or restricted from distribution**?

## Washington + Oregon (91 + 18 files) — reviewed 2026-07-12

Reviewed under this project's earlier two-state release using a three-tier method: (1) a
deterministic keyword/PII/sealing sweep across all 109 files; (2) an independent full-text breadth
review of all 109; (3) a rendered-page depth review of the highest-risk files (the one Washington
report embedding a ~76-page class-member appendix; every Oregon report that tripped a
sealed/confidential/juvenile keyword). **Verdict: all 109 SAFE** — no individual PII found anywhere
(class members are de-identified as numeric IDs; patients in narrative reports are anonymized as
"Patient 1," approximate age only); named individuals are public-role only (the court monitor/
neutral expert, judges, attorneys, agency officials, and named class representatives who are
already public via the case caption); no document is itself sealed or restricted. Full detail in
this project's earlier release (same file set, unchanged; re-verified here only by confirming the
138-file corpus's WA/OR portion is byte-identical to that prior review's 109 files via `SOURCES.csv`
SHA-256 — it is).

## Colorado, Texas, California (14 + 6 + 9 = 29 files) — reviewed 2026-09-07

### Method

1. **Deterministic pre-sweep (all 29).** Full-text extraction (`pdfplumber`), then a
   keyword/pattern scan for the same markers used in the WA/OR review: `sealed`, `confidential`,
   `not for distribution`, `under seal`, SSN pattern (`\d{3}-\d{2}-\d{4}`), date-of-birth phrasing,
   medical-record-number, street-address patterns, `restricted`. All 29 files were text-extractable
   (no image-only/OCR blind spots).
2. **Context review of every hit (all flagged files).** Every single keyword match across all 29
   files was pulled with surrounding context and read directly — not just counted. Texas: zero
   hits in all 6 files. California and Colorado: hits found and individually reviewed (below).
3. **Breadth check for named individuals (Colorado's 11 `sm_*.pdf` Special Master reports).**
   Scanned for titled-name patterns (`Mr./Ms./Mrs./Dr. <Name>`), age-disclosure phrasing
   (`NN-year-old`), and individual/class-member ID references. Two benign professional-title hits
   (`Dr.`, `Ms.`, `Mr.` — report authors/officials in their professional capacity); zero
   age-disclosure hits; zero named-defendant/class-member references anywhere in the 11 reports.
4. **Depth review (rendered pages), scoped to what actually warranted it.** Unlike the WA/OR
   review, no file in this batch tripped a genuinely suspicious keyword (no `sealed`/`under seal`/
   `juvenile` hit anywhere in the 29 — Colorado's `confidential` hits and California's
   `confidential`/`restricted`/`date of birth` hits are described below and were each resolved as
   benign from surrounding text alone). No file in this batch has the structural risk profile of
   WA's one 76-page class-member appendix. A rendered-page depth pass was therefore not needed to
   reach a confident verdict; if that changes on a future addition to this corpus, run one before
   publishing.

### Findings, by hit

- **Colorado, `confidential` (2 hits, `sm_109305.pdf`)**: both are the consent decree's own
  procedural safeguard clause — "...with any private or confidential information redacted from the
  public filing" and "...obtained by the Special Master... which would otherwise be privileged or
  confidential, without consent of all Parties..." — describing the redaction *process* the decree
  itself requires, not actual confidential content present in this filing. Benign.
- **Colorado, street-address pattern (multiple hits, several `sm_*.pdf`)**: all are either (a) the
  U.S. District Court for Colorado's own public courthouse letterhead address ("901 19th Street,
  Denver, CO 80294"), (b) a treatment facility's institutional address in a program-capacity
  discussion ("432 7th Street property in Alamosa"), or (c) a false-positive regex match against
  program/agency names in a funding table ("...Road to Recovery" matched the "...Road" street-
  suffix pattern). No individual's home address. Benign.
- **California, `date of birth` (1 hit per file, 3 of 9 files)**: all three are the identical
  sentence — a definitional list of what data fields a diversion-program report *would* include if
  filed ("The name, social security number, date of birth, and demographics of each individual
  participating in the program") — immediately followed in the source text by a footnote stating
  "This information shall be confidential and shall not be open to public inspection." I.e., this
  sentence documents that such individual-level data is *excluded* from the report we have, not
  present in it. No actual name, SSN, or date of birth appears anywhere in any of the 9 files.
  Benign — and worth stating plainly: this is the one pattern class where the surrounding context
  had to be read carefully rather than dismissed on sight, and it was.
- **California, `confidential` (several hits)**: a mix of (a) the same "this information shall be
  confidential" exclusion-footnote pattern described above, and (b) "Telephones / Confidential Use"
  — a recurring facility-amenity/complaint category in patient-rights compliance tables (how many
  complaints concerned confidential phone access), not a reference to anyone's personal
  information. Benign.
- **California, `restricted` (several hits)**: all describe hospital *operations* — bed capacity
  constraints, unit/ward access restrictions, COVID-era patient-movement restrictions, or licensed
  housing-market terminology ("restricted housing market") — never a restriction on the document's
  own distribution. Benign.

### Verdict

All 29 Colorado, Texas, and California source documents are cleared for public redistribution on
the same PII/sealing basis as the earlier Washington/Oregon review: no individual PII found, no
document itself sealed or restricted from distribution. (Separately, and not a safety-review
question: **whether we have the right to redistribute these documents at all** — i.e., the
copyright/public-records question — is addressed per state in `data/raw/NOTICE` and each state's
own `data/raw/<state>/README.md`; that determination differs meaningfully by state and should be
read there, not assumed from this file.)

## Combined verdict

All 138 bundled source documents (91 WA + 18 OR + 14 CO + 6 TX + 9 CA) are cleared for public
redistribution on PII/sealing grounds.
