# Pre-publication safety review — source documents

**Scope:** all 141 source PDFs this project has provenance for (91 Washington + 18 Oregon, reviewed
2026-07-12 for this project's earlier two-state release, + 14 Colorado + 6 Texas + 9 California,
reviewed 2026-09-07 for this 5-state release, + 2 more Washington and 1 more Colorado, reviewed
2026-09-13 — see "2026-09-13 addition" below) — **all 141 are bundled** as PDF files in
`data/raw/`. Colorado's JBC budget memos were held back from the initial bundle pending a
separate confirmation request, unrelated to this safety review (see `data/raw/co/README.md`) —
they passed this same PII/sealing review before that withholding decision was made, and were added
to the bundle once JBC staff confirmed no objection (2026-09-10). See `SOURCES.csv` for the full
per-file list.

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
document itself sealed or restricted from distribution. (This verdict is about individual PII
specifically -- a later, separate review pass found one Colorado document names a private
third-party contractor in an unadjudicated allegation, a different risk category; see "Two items
outside this review's original PII/sealing scope" near the end of this file for that disclosure.)
(Separately, and not a safety-review
question: **whether we have the right to redistribute these documents at all** — i.e., the
copyright/public-records question — is addressed per state in `data/raw/NOTICE` and each state's
own `data/raw/<state>/README.md`; that determination differs meaningfully by state and should be
read there, not assumed from this file.)

## Two items outside this review's original PII/sealing scope, disclosed here rather than left silent

A later, independent review (2026-09-07, applying lenses beyond the PII/sealing keyword sweep
above) found two things worth stating explicitly, neither of which changes the verdict below:

**1. Small-cell counts are not suppressed.** Several derived-dataset rows (e.g. in
`data/derived/washington.csv`) report facility/month cells as small as 1-2 individuals. No
suppression is applied. This mirrors the source documents' own disclosure granularity exactly —
this project is not creating any small cell that isn't already sitting, unsuppressed, in the
public court-monitor or agency report it was extracted from. Suppressing it here would make the
dataset diverge from its own cited source for no privacy gain, since anyone can already read the
same number off the original PDF this project links to. No individual is named in any such row;
the underlying PII/sealing review above already covers whether that's true.

**2. A named private individual appears in one Colorado document, in an unadjudicated-allegation
context.** `data/raw/co/sm_2024-05-28.pdf` (a Special Master report in *Center for Legal Advocacy
v. Barnes*) names Joel Watts, owner of Integrated Insights Therapy (Delta, CO), stating the
Special Master's own committee had "likely" found he misappropriated program funds. This is not a
class member or patient (the population this review's keyword sweep was built to check) -- he's a
third-party contractor named in the Special Master's own account of a funding-oversight matter.
Disclosed here plainly:
- The passage is verbatim content from a public federal court filing, already public via RECAP
  independent of this project (see `data/raw/co/README.md` and `SOURCES.csv` for the verified
  source URL).
- The allegation is the Special Master's own characterization ("likely misappropriated"), not an
  adjudicated finding, and not this project's own assertion -- this project neither amplifies nor
  independently repeats the allegation in its own prose anywhere; it exists only inside the
  redistributed source document.
- Republishing an unmodified public court filing under these circumstances is the fair-report
  posture, not an edited or curated one -- the document is included as-is, like every other
  Special Master report in this folder, not singled out or redacted.
- Per the standing policy in `data/raw/NOTICE` and every state README, `me@sudhanshurai.org` is
  the contact for any correction or removal request from a rights holder or affected party.

## 2026-09-13 addition — 2 more Washington + 1 more Colorado

`Trueblood-Report-2026-07.pdf`, `Trueblood-Report-2026-08.pdf` (Washington), and
`fy2026-27_humbrf1.5b.pdf` (Colorado, JBC) were added to the archive on 2026-09-13 as new monthly/
periodic reports from the same two recurring publication series already fully reviewed above — not
a new document type. Reviewed by direct inspection (not just format-consistency inference): the 2
Washington reports' data tables (the only sections this project's own extractor reads from) contain
purely aggregate monthly counts, no individual names or case identifiers, matching every one of the
91 already-cleared Washington reports exactly in structure. The Colorado JBC document was read in
full during extraction-code development (its "waitlist," "consent decree fines," and RFI-response
sections) — aggregate figures and one named JBC staff author (a public official acting in an
official capacity, already the norm for this document type, e.g. `jbc_memo.pdf`'s own named
author), no individual-level PII. All 3 cleared on the same basis as the rest of this review.

## Combined verdict

All 141 reviewed source documents (93 WA + 18 OR + 15 CO + 6 TX + 9 CA) are cleared on PII/sealing
grounds, and all 141 are actually bundled in `data/raw/` as of this version — Colorado's JBC
memos were held back from the initial bundle for the separate, unrelated reason described above
(not a PII concern) and added once JBC staff confirmed no objection (2026-09-10); the two items
above are disclosed rather than silently carried forward regardless of bundling status.
