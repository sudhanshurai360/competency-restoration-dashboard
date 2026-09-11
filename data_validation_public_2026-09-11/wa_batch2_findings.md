# Washington Trueblood Data-Integrity Audit — Batch 2 of 2

**Scope:** 45 PDFs, chronologically 2022-08 through 2026-06 (per assignment list).
**Target:** `/Users/sudhanshu/git_clone/competency-restoration-dashboard/data/derived/washington.csv`
**Audit date:** 2026-09-11
**Method:** For every CSV row whose `report` matched an assigned PDF, the cited `pdf_page` was extracted with `pdftotext -layout` and every numeric field (`orders_signed`, `orders_completed`, `avg_days_to_completion`, `median_days_to_completion`, `pct_within_deadline`, `pct_within_alt2`, `pct_within_alt3`) was compared against the printed table row for that month. A small Python harness (parsing the `pdftotext -layout` output and diffing field-by-field, `%` signs stripped, `n/a`/blank treated as null) was built and validated against ~15 PDFs of hand-eyeballed output before being run across the remaining reports — every row it flagged as a "mismatch" on the first pass turned out to be a harness bug (a stray `%` token miscounting columns), fixed and reconfirmed against the hand-checked set with 0 discrepancies before trusting it on the rest. **649 CSV rows were checked in total across the 45 PDFs. Zero numeric discrepancies were found.**

For completeness, every (facility, stage, setting, period) combination visible in each PDF's own tables was also checked against the *entire* CSV (not just rows attributed to that specific report) to confirm no genuine, permanent data loss — see the "Background: how sourcing works" section and the flagged-report deep dives below.

---

## Background: how the CSV sources each row (established during this audit)

Each monthly Trueblood report contains, per facility/stage/setting combination, a 13-month trailing table: the oldest row is (report month − 13), the newest ("first look," subject to revision) is (report month − 1). The CSV picks, for each (facility, stage, setting, period), the **most mature available** report — normally the report published exactly 13 months after the period, because that is the last time the period appears in any table before rolling off the bottom.

Two things can push the source to an earlier (less mature) report:
1. **The ideal report doesn't exist.** `Trueblood-Report-2022-12.pdf` and `Trueblood-Report-2023-03.pdf` are absent from `data/raw/wa/` — confirmed by directory listing — they were apparently never published/archived. This is a real, permanent source gap, not an extraction bug, and the CSV correctly falls back to the next available report.
2. **The ideal report's own table for that specific facility/stage/setting failed pdfplumber structural detection** (the 7 reports flagged in this assignment, some also outside the flagged list — see below), so ETL fell back to an earlier report that had the same (already-mature, unchanged) value.

Both fallback mechanisms were observed working correctly and losslessly in this batch.

---

## Per-PDF results

All 45 PDFs: **CLEAN**. Row counts below are the number of CSV rows attributed to that report, and all matched the PDF exactly.

| Report | Rows checked | Result |
|---|---|---|
| Trueblood-Report-2022-08.pdf | 11 | CLEAN |
| Trueblood-Report-2022-09.pdf | 12 | CLEAN |
| Trueblood-Report-2022-10.pdf | 20 | CLEAN (see note below) |
| Trueblood-Report-2022-11.pdf | 12 | CLEAN — flagged report, deep-dive below |
| Trueblood-Report-2023-01.pdf | 11 | CLEAN |
| Trueblood-Report-2023-02.pdf | 22 | CLEAN |
| Trueblood-Report-2023-04.pdf | 11 | CLEAN |
| Trueblood-Report-2023-05.pdf | 11 | CLEAN |
| Trueblood-Report-2023-06.pdf | 18 | CLEAN |
| Trueblood-Report-2023-07.pdf | 4 | CLEAN — flagged report, deep-dive below |
| Trueblood-Report-2023-08.pdf | 11 | CLEAN |
| Trueblood-Report-2023-09.pdf | 11 | CLEAN |
| Trueblood-Report-2023-10.pdf | 11 | CLEAN |
| Trueblood-Report-2023-11.pdf | 11 | CLEAN |
| Trueblood-Report-2023-12.pdf | 11 | CLEAN |
| Trueblood-Report-2024-01.pdf | 11 | CLEAN |
| Trueblood-Report-2024-02.pdf | 11 | CLEAN |
| Trueblood-Report-2024-03.pdf | 11 | CLEAN |
| Trueblood-Report-2024-04.pdf | 11 | CLEAN |
| Trueblood-Report-2024-05.pdf | 26 | CLEAN — flagged report, deep-dive below |
| Trueblood-Report-2024-06.pdf | 5 | CLEAN — flagged report, deep-dive below |
| Trueblood-Report-2024-07.pdf | 2 | CLEAN — flagged report, deep-dive below |
| Trueblood-Report-2024-08.pdf | 11 | CLEAN |
| Trueblood-Report-2024-09.pdf | 11 | CLEAN |
| Trueblood-Report-2024-10.pdf | 11 | CLEAN |
| Trueblood-Report-2024-11.pdf | 11 | CLEAN |
| Trueblood-Report-2024-12.pdf | 11 | CLEAN |
| Trueblood-Report-2025-01.pdf | 11 | CLEAN |
| Trueblood-Report-2025-02.pdf | 11 | CLEAN |
| Trueblood-Report-2025-03.pdf | 11 | CLEAN |
| Trueblood-Report-2025-04.pdf | 11 | CLEAN |
| Trueblood-Report-2025-05.pdf | 11 | CLEAN |
| Trueblood-Report-2025-06.pdf | 11 | CLEAN |
| Trueblood-Report-2025-07.pdf | 11 | CLEAN |
| Trueblood-Report-2025-08.pdf | 11 | CLEAN |
| Trueblood-Report-2025-09.pdf | 11 | CLEAN |
| Trueblood-Report-2025-10.pdf | 11 | CLEAN |
| Trueblood-Report-2025-11.pdf | 11 | CLEAN |
| Trueblood-Report-2025-12.pdf | 17 | CLEAN |
| Trueblood-Report-2026-01.pdf | 5 | CLEAN — flagged report, deep-dive below |
| Trueblood-Report-2026-02.pdf | 11 | CLEAN |
| Trueblood-Report-2026-03.pdf | 11 | CLEAN |
| Trueblood-Report-2026-04.pdf | 11 | CLEAN |
| Trueblood-Report-2026-05.pdf | 11 | CLEAN |
| Trueblood-Report-2026-06.pdf | 143 | CLEAN — flagged report (most recent PDF in archive), deep-dive below |

**Total: 649/649 rows verified correct, 0 discrepancies.**

---

## Deep dives: the 7 flagged (known pdfplumber `find_tables()` failure) reports

For each of these, I checked (a) the numeric accuracy of every row the CSV *does* attribute to that report (all correct, see table above), and (b) whether every (facility, stage, setting, period) combination visible in that PDF's own tables is present *somewhere* in the CSV with correct values — i.e., whether the "fall back to a different report" recovery claim actually holds. **In all 7 cases, it does. No permanent data loss was found for any of the flagged reports in this batch.**

### Trueblood-Report-2022-11.pdf
CSV attributes only 12 of the 22 possible rows (2021-10 and 2021-11 × 6 of 11 facility/stage/setting combos: OCRP, RTF, TOTAL eval jail, TOTAL restoration inpatient, WSH eval inpatient, WSH eval jail) directly to this report. The other 5 combos (ESH eval inpatient, ESH eval jail, ESH restoration inpatient, TOTAL eval inpatient, WSH restoration inpatient) for the same two periods are instead sourced from `Trueblood-Report-2022-10.pdf`.
- Confirmed via `pdftotext` on `Trueblood-Report-2022-11.pdf` page 19 (Table 6, ESH eval inpatient) and page 14 (Table 4a, WSH restoration inpatient) that the **raw text of the failed tables is actually present and readable** (pdftotext succeeds where pdfplumber's structural `find_tables()` apparently did not) — and the values are byte-for-byte identical to what `Trueblood-Report-2022-10.pdf` supplied for the same months (e.g. Oct-21 WSH restoration: 123 signed / 119 completed / 44.9 avg / 49.0 median / 7%,8%,10% — identical in both PDFs).
- Cross-checked all 11 combos × periods {2021-10, 2021-11} against the full CSV: **all 22 cells present, all correct.**

### Trueblood-Report-2023-07.pdf
CSV attributes only 4 of 11 combos for period 2022-06 (WSH eval jail, ESH eval jail, TOTAL eval jail, TOTAL restoration inpatient) directly to this report. The other 7 combos for 2022-06 are sourced from `Trueblood-Report-2023-06.pdf` instead.
- Verified all 7 fallback values against `Trueblood-Report-2023-06.pdf`'s own pages (13–23) directly — all match exactly (e.g. ESH eval inpatient Jun-22: 12/7/44.7/12.0/0%,0%,0%; WSH restoration inpatient Jun-22: 114/77/65.9/70.0/8%,8%,8%).
- Cross-checked all 11 combos for period 2022-06 against the full CSV: **all 11 present, all correct.**

### Trueblood-Report-2024-05.pdf, Trueblood-Report-2024-06.pdf, Trueblood-Report-2024-07.pdf
These three consecutive flagged reports jointly cover periods 2023-04, 2023-05, 2023-06 (the "oldest, about-to-roll-off" rows for these three reports respectively). Coverage is split across all three PDFs:
- 2023-04: all 11 combos sourced from `2024-05.pdf` — complete.
- 2023-05: 8 combos from `2024-05.pdf`, 2 combos (ESH restoration inpatient, WSH restoration inpatient — actually 3: also WSH evaluation jail) from `2024-06.pdf` — complete, all 11 present.
- 2023-06: mixed across all three (`2024-05.pdf`: 6 combos; `2024-06.pdf`: ESH restoration inpatient, WSH restoration inpatient; `2024-07.pdf`: WSH eval inpatient, WSH eval jail) — complete, all 11 present.
- Checked the full CSV for periods 2023-04 / 2023-05 / 2023-06 × all 11 combos: **33/33 cells present, all correct**, consistent with the numeric row-checks already reported in the summary table.

### Trueblood-Report-2026-01.pdf
CSV attributes only 5 of 11 combos for period 2024-12 (OCRP, RTF, WSH eval inpatient, WSH eval jail, WSH restoration inpatient) directly to this report. The other 6 (all ESH combos + all TOTAL combos) are sourced from `Trueblood-Report-2025-12.pdf`.
- Cross-checked all 11 combos for period 2024-12 against the full CSV: **all 11 present, all correct.**

### Trueblood-Report-2026-06.pdf
This is the most recent PDF in the archive (as of this audit), so unlike the other flagged reports it has **no later report available to fall back to** — this is the one case where a genuine table-detection failure here could mean real, currently-unrecoverable data loss (until WA republishes a later monthly report).
- This report supplies 143 CSV rows: 13 periods (2025-05 through 2026-05) × 11 facility/stage/setting combos = 143 — a complete, gap-free grid. All 143 rows were individually checked against the PDF and matched exactly (0 mismatches).
- Only one row in this report's set has null `avg`/`median`/`pct` fields (2025-06, OCRP restoration outpatient, signed=3, completed=0) — this is a legitimate "n/a because zero completions" case, confirmed identical in the PDF itself, not a symptom of the pdfplumber detection failure.
- **No missing or incomplete data was found for this report.** Whatever caused pdfplumber's `find_tables()` to fail on this PDF did not, in the end, prevent any of its 143 expected cells from being correctly extracted and recorded (via the row-level "all n/a" recovery fix mentioned in the task brief, and/or successful extraction of the remaining tables).

---

## Minor observation (not a data-accuracy issue)

While verifying `Trueblood-Report-2022-10.pdf`, I noticed the CSV sources period 2021-09 / WSH evaluation inpatient (Table 3) from `Trueblood-Report-2022-09.pdf` rather than from `Trueblood-Report-2022-10.pdf`, even though `2022-10.pdf`'s own Table 3 (page 13) clearly contains an identical Sep-21 row (17 signed / 16 completed / 29.1 avg / 28.0 median / 25%,25%,25% — confirmed by direct `pdftotext` read of that page). This suggests `2022-10.pdf`'s Table 3 also had a partial pdfplumber detection issue for that one row, even though `2022-10.pdf` is not on the officially flagged 7-report list. **This has zero effect on data correctness** — the value used in the CSV is byte-for-byte identical either way — but it's worth noting as a provenance quirk (the `report`/`pdf_page` citation for this one cell points to a technically-earlier-than-ideal but numerically-correct source) in case it's useful for future ETL hardening. This is the only such attribution anomaly noticed in this batch; I did not exhaustively hunt for more since it has no bearing on the printed numbers a reader would see.

---

## Conclusion

All 45 assigned PDFs are **CLEAN**: every one of the 649 CSV rows sourced from them was checked against the actual printed PDF table and matches exactly (orders signed, orders completed, average days, median days, and all three percent-within-deadline columns). All 7 specially-flagged reports with known pdfplumber table-detection failures were deep-dive checked for true data loss, and in every case the missing cells were confirmed to have been correctly recovered from an adjacent report with identical (already-mature) values — including the two hardest cases (2022-11.pdf and 2023-07.pdf, verified via direct comparison of the "failed" page's raw text against the fallback report's page) and the one case with no fallback available (2026-06.pdf, the newest report, found to have a complete, gap-free 143-row grid with 0 mismatches).

No numeric discrepancies and no unrecovered data loss were found anywhere in this batch.

---

## Independent re-verification (second pass, same auditor's coordinating agent)

A second, independent pass was run over this same batch (same 45 PDFs) using a separately-written harness (Python, `pdftotext -layout` extraction, same 13-numeric-token row layout independently derived and confirmed by a full manual page-by-page read of `Trueblood-Report-2022-08.pdf` and `Trueblood-Report-2023-08.pdf` before being trusted on the rest). Result: **identical conclusion** — all 45 PDFs CLEAN, 649/649 rows checked, 0 mismatches. The 7 flagged reports were independently re-checked for recoverability using a script that reads every table page a report cites and diffs all 13 visible month-rows (not just the CSV-attributed ones) against the full CSV; this independently confirmed zero permanent data loss for all 7, with the same fallback reports identified in each case (`2022-11.pdf`→`2022-10.pdf`; `2023-07.pdf`→`2023-06.pdf`; `2024-06.pdf`→`2024-05.pdf`; `2024-07.pdf`→`2024-05.pdf`/`2024-06.pdf`; `2026-01.pdf`→`2025-12.pdf`; `2024-05.pdf` and `2026-06.pdf` found to have no missing tables at all in the current CSV).

One additional detail worth recording: WA renumbered its data tables at some point between the 2025 and 2026 reports (old scheme Table 2/3/4a/4b/4c/5/6/7/8/9/10 → new scheme Table 3/4/5a/5b/5c/6/7/8/9/10/11), apparently while also folding Eastern State Hospital into the same unified table sequence rather than a later, separately-numbered section. `Trueblood-Report-2026-01.pdf` onward use the new numbering. This is already correctly reflected in the CSV's `table_ref` column per-row (each row cites whatever numbering was actually in force in its own source PDF) and is not a data-quality defect — noted here only so a human spot-checking `table_ref` values across years isn't confused by the renumbering. The new-format row layout (13 numeric tokens, "Days from order signature to" 3-column block, completed, avg/median days-to-completion, 3 compliance percentages) is identical to the old format; this was directly confirmed by eye against `Trueblood-Report-2026-06.pdf` page 16 (Table 3, WSH evaluation/jail), whose May-2026 "first look" row (480 signed / 456 completed / 11.7 avg / 12.0 median / 90%/93%/93%) matches the CSV exactly.
