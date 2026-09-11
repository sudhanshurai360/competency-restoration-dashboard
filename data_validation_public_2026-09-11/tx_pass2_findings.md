# Texas HHSC Competency-Restoration Waitlist Data — Independent Audit Pass 2

Auditor: independent second-pass agent (parallel to another independent pass).
Scope: `data/derived/texas.csv` (24 data rows) vs. the 6 raw PDFs in `data/raw/tx/`.
Method: rendered each cited PDF page to a 150-dpi PNG with `pdftoppm` (from the exact archived
file, physical page index = CSV `pdf_page`/`pdf_page_days`), visually read the printed table,
and compared every field cell-by-cell against the CSV. Also independently recomputed SHA-256 of
each PDF and diffed against `source_sha`. No number was accepted from a code comment or from
metadata — only from the rendered page image.

## Overall verdict: CLEAN — all 24 rows verified correct. No discrepancies found.

## Per-file results

### mhs-waiting-lists-may-2023.pdf (2 periods: 2022-11, 2023-02) — CLEAN, 4 rows
- Physical page 12 (printed footer "10") holds both Table 5 (Non-Maximum Security) and Table 6
  (Maximum Security). This report format has **no separate "Total" vs "Maximum Security" row** —
  Table 6 is a single homogeneous table entirely about the maximum-security list, with "People on
  the Waitlist" and "Average Number of Days..." as its own rows (Q3/Q4 columns).
- Table 5 (non_max): Q3 waitlist=1,481, avg days=252 → CSV `2022-11,non_max,1481,252.0` ✓. Q4
  waitlist=1,526, avg days=264 → CSV `2023-02,non_max,1526,264.0` ✓.
- Table 6 (max): Q3 waitlist=883, avg days=519 → CSV `2022-11,max,883,519.0` ✓. Q4 waitlist=991,
  avg days=617 → CSV `2023-02,max,991,617.0` ✓.
- `source_sha` `a61be388385e` matches actual file SHA-256 prefix (`a61be388385e4ed3...`) ✓.

### mhs-waiting-lists-nov-2023.pdf (2 periods: 2023-05, 2023-08) — CLEAN, 4 rows
- Physical page 12 (printed footer "10") holds Table 5 and Table 6, same single-table-per-security-level
  format as the May 2023 report (no Total-vs-Maximum-Security ambiguity here either).
- Table 5 (non_max): Q3 waitlist=1,345, avg=288 → CSV `2023-05,non_max,1345,288.0` ✓. Q4
  waitlist=1,200, avg=233 → CSV `2023-08,non_max,1200,233.0` ✓.
- Table 6 (max): Q3 waitlist=1,053, avg=690 → CSV `2023-05,max,1053,690.0` ✓. Q4 waitlist=968,
  avg=659 → CSV `2023-08,max,968,659.0` ✓.
- `source_sha` `cde9e1595b0d` matches actual file SHA-256 prefix ✓.

### mhs-waiting-lists-nov-2024.pdf (4 periods: 2023-11, 2024-02, 2024-05, 2024-08) — CLEAN, 8 rows
- This report introduces the multi-facility table format. Physical page 13 (printed "12") = Table 7
  (Number of People on Non-MSU Forensic Inpatient Waiting List, by facility, FY24 Q1–Q4). Physical
  page 14 (printed "13") = Table 9 (Average Days, Non-MSU, by facility) and Table 10 (Number of
  People on MSU Forensic Inpatient Bed Waiting List).
- Table 7 TOTAL row: Q1=1,178, Q2=1,249, Q3=1,159, Q4=1,208 → matches CSV non_max waitlist_count
  for 2023-11/2024-02/2024-05/2024-08 exactly ✓ (1178, 1249, 1159, 1208).
- Table 9 TOTAL row: Q1=239.3, Q2=200.6, Q3=223.9, Q4=185.1 → matches CSV non_max avg_wait_days
  exactly ✓.
- **Table 10 (max) — Total vs. "Maximum Security" row check (adversarial, per instructions):**
  Table 10 lists five facility rows — North Texas State Hospital Vernon, Kerrville State Hospital,
  **Maximum Security** (792/684/637/524), Rusk State Hospital, North Texas State Hospital Wichita
  Falls — and a **TOTAL** row (857/720/693/582). The CSV's `waitlist_count` for 2023-11/2024-02/
  2024-05/2024-08 is 857/720/693/582 — this is the **TOTAL row, correctly, not** the
  "Maximum Security" facility-only sub-row (792/684/637/524). Confirmed CORRECT — CSV does not
  conflate the "Maximum Security" line item with the true total max-security waitlist.
- **avg_wait_days blank check for max rows:** Table 12 in this report ("Average Number of Days on
  MSU Forensic Inpatient Waiting List") has rows for Vernon, Kerrville, Rusk, and Wichita Falls
  only — it contains **no "Maximum Security" row at all** in this report edition, so there is no
  comparable, disclosable average-wait-days figure for the max-security population. CSV correctly
  leaves `avg_wait_days` blank for all 4 max rows from this report (2023-11, 2024-02, 2024-05,
  2024-08 all show empty avg_wait_days) — confirmed correct, not silently populated with the wrong
  (facility-level or Total) number.
- `source_sha` `d67b989ad3bf` matches actual file SHA-256 prefix ✓.

### mhs-waiting-lists-nov-2025.pdf (4 periods: 2024-11, 2025-02, 2025-05, 2025-08) — CLEAN, 8 rows
- Physical page 14 (printed "13") = Table 7 (Non-MSU waitlist by facility) start. Physical page 15
  (printed "14") = Table 7 continuation/Total + Table 8 + Table 9 start. Physical page 16 (printed
  "15") = Table 9 continuation/Total + Table 10 + Table 11 + Table 12 start.
- Table 7 TOTAL row: Q1=1,247, Q2=1,195, Q3=1,205, Q4=1,285 → matches CSV non_max waitlist_count
  for 2024-11/2025-02/2025-05/2025-08 exactly ✓.
- Table 9 TOTAL row (on physical page 16, matching CSV's `pdf_page_days=16`): Q1=198, Q2=198,
  Q3=190, Q4=178 → matches CSV non_max avg_wait_days exactly ✓.
- **Table 10 (max) — Total vs. "Maximum Security" row check:** Facility rows — Kerrville State
  Hospital, Rusk State Hospital, Vernon State Hospital, Wichita Falls State Hospital,
  **Maximum Security** (457/423/408/419) — and **Total** row (518/505/482/484). CSV
  `waitlist_count` for 2024-11/2025-02/2025-05/2025-08 = 518/505/482/484 — the **TOTAL row,
  correctly**, not the Maximum Security sub-row (457/423/408/419). Confirmed CORRECT.
- **avg_wait_days blank check for max rows:** Table 12 in this report ("Average Number of Days
  from notification to admission on MSU Forensic Inpatient Waiting List") *does* carry a
  "Maximum Security" row here, but it reads **0, 0, 0, 0** for all four quarters, with an explicit
  footnote (footnote 18 on the printed page): *"Table 12 covers admissions to specific hospitals.
  Maximum Security is not a physical location. Because of this, people do not directly admit from
  the maximum security list."* I.e., the 0s are a structural non-applicable placeholder, not a
  real average-wait figure, and the Total row (302/247/253/202) is a different population mix, not
  specific to max-security. CSV correctly leaves `avg_wait_days` blank rather than reporting either
  the misleading "0" or the mismatched Total — confirmed correct and, if anything, better
  substantiated in this report edition than in the Nov-2024 edition.
- `source_sha` `00529cb0ab8b` matches actual file SHA-256 prefix ✓.

## Cross-cutting checks

- **Completeness**: 24 rows = 12 unique periods (2022-11 through 2025-08, all quarter-end months
  Nov/Feb/May/Aug) × 2 security levels each, no duplicate (period, security_level) keys, no gaps.
- **avg_wait_days blank pattern**: blank for exactly the 8 max rows sourced from Table 10 (nov-2024
  and nov-2025 reports); populated for the 4 max rows sourced from the single-table May-2023/
  Nov-2023 report format (where the average-days figure is unambiguous and printed directly in the
  same table as the count). This pattern is consistent and correctly justified by the underlying
  source structure in every case checked above — not a silent/uniform gap.
- **File hash integrity**: all 4 referenced PDFs' independently recomputed SHA-256 prefixes match
  the CSV's `source_sha` values exactly (`a61be388385e`, `cde9e1595b0d`, `d67b989ad3bf`,
  `00529cb0ab8b`).
- **Unreferenced raw files**: `mhs-waiting-lists-may-2024.pdf` and `mhs-waiting-lists-may-2025.pdf`
  are present in `data/raw/tx/` but never cited by any CSV row. This is expected/documented, not a
  gap: `data/raw/tx/README.md` states both are "superseded by the following November report for
  every period they'd otherwise cover," so the corresponding Nov reports were used as the CSV
  source instead. No data loss.
- **table_ref / pdf_page_days / table_ref_days columns**: verified against the actual page/table
  each cited value came from in every row above (Table 5/6 for the 2023 reports; Table 7/9/10 with
  distinct page numbers for the 2024/2025 reports where the average-days table sits on a different
  physical page than the count table) — all citations point to the correct page and correct table.

## CRITICAL findings

None. No max-security row was found using the "Maximum Security" facility sub-total instead of the
table's true Total. No max-security avg_wait_days was found silently populated with a wrong value.
