# Texas HHSC Competency-Restoration Waitlist — Independent Pass-1 Verification

Date of review: 2026-09-11
Reviewer: independent audit pass (Sonnet 5 agent), no reliance on code comments/metadata
Target file: `data/derived/texas.csv` (24 rows)
Method: rendered each cited physical PDF page at 200 DPI with `pdftoppm` and visually read the
printed table cells directly against the CSV values (no OCR/text-extraction trusted for the
verified numbers themselves — `pdftotext` was used only for locating table locations and for the
supplementary May-2024/May-2025 cross-check). Also independently recomputed SHA-256 of every raw
PDF and diffed against `source_sha` (CSV) and `SOURCES.csv` (full hash + byte size).

## Overall verdict: CLEAN — all 24 rows verified, 0 discrepancies, 0 critical bugs found

The previously-fixed "Maximum Security bucket vs. Total row" bug is **correctly fixed** in this
public repo's copy for all 8 affected rows (periods 2023-11 through 2025-08). No regression found.

---

## Per-PDF results

### 1. `mhs-waiting-lists-may-2023.pdf` — CLEAN — 4 rows
- SHA-256 (full): `a61be388385e4ed3a3c93f2078fb1a233a1c1cb3b87d8b689c2a256400b54eb3` — matches `source_sha` prefix `a61be388385e` and matches `SOURCES.csv` (size 377,526 bytes) exactly.
- Physical PDF page 12 (footer prints "10") — opened and read directly.
  - Table 5 (Non-Maximum Security): Q3 = 1,481 people / 252 avg days; Q4 = 1,526 / 264.
  - Table 6 (Maximum Security): Q3 = 883 people / 519 avg days; Q4 = 991 / 617.
- CSV rows checked:
  - `2022-11,max,883,519.0` ✓ exact match
  - `2023-02,max,991,617.0` ✓ exact match
  - `2022-11,non_max,1481,252.0` ✓ exact match
  - `2023-02,non_max,1526,264.0` ✓ exact match
- Note: this early report format has a single combined figure per security level (no separate
  "Maximum Security bucket" vs. "Total" split yet — that distinction only appears starting with
  the Nov-2024 report format). The critical bucket-vs-Total check does not apply to this file.

### 2. `mhs-waiting-lists-nov-2023.pdf` — CLEAN — 4 rows
- SHA-256 (full): `cde9e1595b0d0ca193dd60c53874ca92787642c2516e2621692ae068508be19d` — matches `source_sha` prefix `cde9e1595b0d` and `SOURCES.csv` (size 370,232 bytes) exactly.
- Physical PDF page 12 (footer prints "10") — opened and read directly.
  - Table 5 (Non-Maximum Security): Q3 = 1,345 / 288; Q4 = 1,200 / 233.
  - Table 6 (Maximum Security): Q3 = 1,053 / 690; Q4 = 968 / 659.
- CSV rows checked:
  - `2023-05,max,1053,690.0` ✓ exact match
  - `2023-08,max,968,659.0` ✓ exact match
  - `2023-05,non_max,1345,288.0` ✓ exact match
  - `2023-08,non_max,1200,233.0` ✓ exact match
- Same note as above: single combined figure per security level, no bucket/Total split.

### 3. `mhs-waiting-lists-nov-2024.pdf` — CLEAN — 8 rows (critical check PASSED for all 4 max rows)
- SHA-256 (full): `d67b989ad3bf4e2d1fa3a288f97ce4dca06541ee7cd0ab3086a4bb63643d1801` — matches `source_sha` prefix `d67b989ad3bf` and `SOURCES.csv` (size 563,134 bytes) exactly.
- Physical PDF page 13 (footer "12"): Table 7 (Non-MSU count), TOTAL row: FY24 Q1=1,178, Q2=1,249, Q3=1,159, Q4=1,208.
- Physical PDF page 14 (footer "13"): Table 9 (Non-MSU avg days), TOTAL row: Q1=239.3, Q2=200.6, Q3=223.9, Q4=185.1. Table 10 (MSU/max count) has rows for Vernon, Kerrville, **Maximum Security** (bucket), Rusk, Wichita Falls, and a **Total** row:
  - Q1: Vernon 44, Kerrville 3, **Maximum Security bucket 792**, Rusk 11, Wichita Falls 7 → **Total 857**
  - Q2: 21, 0, **684**, 13, 2 → **Total 720**
  - Q3: 34, 3, **637**, 17, 2 → **Total 693**
  - Q4: 35, 3, **524**, 12, 8 → **Total 582**
- CSV rows checked (FY24 Q1=2023-11, Q2=2024-02, Q3=2024-05, Q4=2024-08):
  - `2023-11,max,857` ✓ matches **Total** row (bucket alone would have been 792 — CSV correctly does NOT use the bucket value)
  - `2024-02,max,720` ✓ matches Total (bucket was 684)
  - `2024-05,max,693` ✓ matches Total (bucket was 637)
  - `2024-08,max,582` ✓ matches Total (bucket was 524)
  - `2023-11,non_max,1178,239.3` ✓ / `2024-02,non_max,1249,200.6` ✓ / `2024-05,non_max,1159,223.9` ✓ / `2024-08,non_max,1208,185.1` ✓ — all exact matches.
- avg_wait_days is correctly left **blank** in the CSV for all 4 max rows in this report: the
  source report's Table 12 (avg days on MSU list) only reports per-facility averages (Vernon,
  Kerrville, Rusk, Wichita Falls) and never publishes an average for the "Maximum Security" bucket
  itself or for the combined Total. There is no legitimate number to cite here, so leaving it
  blank is the correct handling, not a gap.
- **Critical bucket-vs-Total check: PASSED for all 4 rows.**

### 4. `mhs-waiting-lists-nov-2025.pdf` — CLEAN — 8 rows (critical check PASSED for all 4 max rows)
- SHA-256 (full): `00529cb0ab8b1c34299fb459ffd16d586c9652ecc06872abaa5ce32315ce6bef` — matches `source_sha` prefix `00529cb0ab8b` and `SOURCES.csv` (size 543,855 bytes) exactly.
- Physical PDF page 14 (footer "13"): Table 7 (Non-MSU count), Total row: FY25 Q1=1,247, Q2=1,195, Q3=1,205, Q4=1,285.
- Physical PDF page 15/16 (footer "14"/"15"): Table 9 (Non-MSU avg days) Total row: Q1=198, Q2=198, Q3=190, Q4=178. Table 10 (MSU/max count), rows for Kerrville, Rusk, Vernon, Wichita Falls, **Maximum Security** (bucket, footnoted¹⁷), and **Total**:
  - Q1: bucket **457** → **Total 518**
  - Q2: bucket **423** → **Total 505**
  - Q3: bucket **408** → **Total 482**
  - Q4: bucket **419** → **Total 484**
- CSV rows checked (FY25 Q1=2024-11, Q2=2025-02, Q3=2025-05, Q4=2025-08):
  - `2024-11,max,518` ✓ matches Total (bucket alone would have been 457)
  - `2025-02,max,505` ✓ matches Total (bucket 423)
  - `2025-05,max,482` ✓ matches Total (bucket 408)
  - `2025-08,max,484` ✓ matches Total (bucket 419)
  - `2024-11,non_max,1247,198.0` ✓ / `2025-02,non_max,1195,198.0` ✓ / `2025-05,non_max,1205,190.0` ✓ / `2025-08,non_max,1285,178.0` ✓ — all exact matches.
- avg_wait_days correctly blank for max rows here too — same reason as nov-2024 (Table 12 in this
  report is "Average Number of Days from notification to admission on MSU Forensic Inpatient
  Waiting List," reported only per facility, no Maximum-Security-bucket or combined figure).
- **Critical bucket-vs-Total check: PASSED for all 4 rows.**

---

## Completeness check

- 24/24 rows present. Periods run quarterly and continuously from 2022-11 through 2025-08 (12
  periods × 2 security levels), no gaps, no duplicates.
- `data/raw/tx/` contains 6 PDFs but the CSV only cites 4 of them
  (`mhs-waiting-lists-may-2024.pdf` and `mhs-waiting-lists-may-2025.pdf` are never referenced).
  This is **not a completeness bug** — verified directly:
  - `mhs-waiting-lists-may-2024.pdf` contains only FY24 Q1 (2023-11) and FY24 Q2 (2024-02) data
    (`pdftotext` dump of Tables 7/9/10 confirmed), values 1178/1249 (non-max) and 857/720 (max,
    Total row) — identical to what `mhs-waiting-lists-nov-2024.pdf` reports for those same two
    quarters. Fully superseded/subsumed; no unique data lost by not citing it.
  - `mhs-waiting-lists-may-2025.pdf` contains only FY25 Q1 (2024-11) and FY25 Q2 (2025-02).
    Non-max Table 7 Total (1247, 1195) and Table 9 avg-days Total (197.6→rounds to 198, 198.1→198)
    agree with `mhs-waiting-lists-nov-2025.pdf`. This is documented in
    `data/raw/tx/README.md` and in `SOURCES.csv` as intentional (both files "superseded by the
    following November report for every period they'd otherwise cover").
  - SHA-256 and byte size for all 6 raw PDFs (used and unused) were independently recomputed and
    match `SOURCES.csv` exactly.

## Secondary finding (not a CSV error — flagging for awareness only)

`mhs-waiting-lists-may-2025.pdf` Table 10 (max/MSU count) reports **FY25 Q1 Total = 523**, but
`mhs-waiting-lists-nov-2025.pdf` Table 10 reports **FY25 Q1 (same period, 2024-11) Total = 518** —
a 5-person difference in HHSC's own source data between the two reports for the identical quarter.
This is *not* a bucket-vs-Total confusion (both totals were compared to totals) and *not* a bug in
this repo — it is HHSC's own restatement, explicitly disclosed in `mhs-waiting-lists-nov-2025.pdf`
footnote 16 (physical page 16): "HHSC included San Antonio State Hospital, Rio Grande State
Center, Terrell State Hospital, and Perimeter Hospital in Table 10 in the May 2025 report, and has
updated the November 2025 report to reflect the appropriate facilities." I.e., the May 2025 report
mis-assigned some non-max facilities' waitlist entries into the Table 10 (max) facility breakdown,
inflating that quarter's max total by 5; HHSC corrected this in the November 2025 report. The CSV
correctly cites the corrected report (`mhs-waiting-lists-nov-2025.pdf`, value 518) for period
2024-11, which is the right choice — flagging only so this restatement is documented and doesn't
surprise anyone diffing the two source PDFs directly. No other quarter showed a similar
Table-10 restatement between the May and November reports that overlap it (FY24 Q1/Q2 May-2024 vs.
Nov-2024 Table 10 figures were identical: 792/684 bucket, 857/720 Total).

## Integrity/provenance checks

- All 6 raw PDF files' full SHA-256 hashes and byte sizes independently recomputed and cross-checked
  against both `data/derived/texas.csv` (`source_sha`, first-12-hex-char prefix) and the archive-root
  `SOURCES.csv` (full hash + size) — **all match exactly**, no substitution/corruption.
- `pdf_page` in the CSV is confirmed to be the **physical PDF page index** (1-based, matching what
  `pdftoppm -f N -l N` renders), not the number printed in the page footer (which runs 2 pages
  behind, e.g. physical page 12 = footer "10"). This convention is consistent across all 4 cited
  PDFs and was directly verified by opening each cited page and confirming table content, so it is
  not a citation bug — just noting the convention for anyone auditing pdf_page values by eyeballing
  footer numbers instead of physical page count.

## Bottom line

- **No critical bug found.** The max-security bucket-vs-Total row bug is correctly fixed for all
  8 affected rows in this public repo's copy.
- **No numeric discrepancies of any kind** across all 24 rows — every waitlist_count and every
  avg_wait_days value was read directly off the cited physical page/table and matches the CSV
  exactly.
- Completeness confirmed: 24/24 expected rows present, contiguous quarterly coverage 2022-11
  through 2025-08, no gaps or duplicates.
- One noteworthy but non-blocking finding: HHSC itself restated the 2024-11 max-security total
  (523 → 518) between its May-2025 and Nov-2025 reports; the CSV correctly uses the corrected
  November figure.
