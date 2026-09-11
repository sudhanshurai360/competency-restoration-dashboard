# Washington Trueblood Monthly Reports — Data-Integrity Audit (Batch 1 of 2, 2016–2022)

Audit date: 2026-09-11
Scope: `data/derived/washington.csv` (412 rows) cited against `data/raw/wa/` PDFs — the 46 reports `Trueblood-Report-2016-05.pdf` through `Trueblood-Report-2022-07.pdf`.
Method: every CSV row citing one of these 46 reports was matched to its own `report`/`pdf_page`/`table_ref`, the source page was extracted from the actual PDF (`pdftotext -layout` text-layer extraction, cross-checked against a rendered image view wherever a value looked suspicious or the text layer looked garbled — no image-only/scanned pages were encountered in this batch), and every numeric field (`orders_signed`, `orders_completed`, `avg_days_to_completion`, `median_days_to_completion`, `pct_within_deadline`, `pct_within_alt2`, `pct_within_alt3`) was compared by hand against the printed table. Completeness (facility/stage/setting combinations printed in a PDF but absent from the whole CSV for that period) was checked systematically by diffing every (facility, stage, setting) series against the full period range 2018-01–2022-07, then confirming each apparent hole against the actual source PDF page.

**Bottom line: every numeric value cited from these 46 reports is correct.** Zero value-level (wrong-number) discrepancies were found across all 412 rows. Three genuine completeness gaps were found (detailed in "Confirmed completeness gaps" below) — all are extraction omissions, not wrong numbers, and all are narrow/bounded. Several other apparent gaps investigated in depth turned out **not** to be gaps once checked against the whole dataset (the pipeline deliberately keeps the value from the most recent report that covers a given period, so a specific report legitimately contributing zero or few rows is often normal, not a defect) — these are documented under "Investigated and ruled out" so the reasoning is auditable rather than asserted.

---

## Confirmed completeness gaps (real, actionable)

### Gap 1 — WSH jail-based evaluation (`facility=WSH, stage=evaluation, setting=jail`) missing for 2018-01 through 2018-08 (8 periods, all facility/stage/setting-consistent)

This is the single largest defect found in this batch. The old-format reports (`Trueblood-Report-2018-11.pdf`, `2018-12.pdf`, `2019-01.pdf`, `2019-02.pdf` through `2019-09.pdf`) each print a "**Table 1a**. Class Member Status Western State Hospital – Jail-based Competency Evaluations" table with a trailing ~13-month series. Every other table on those same pages/reports (Table 1b, 1c, 2a, 2b, 2c, 3a, 3b, 3c) was correctly extracted into the CSV — **Table 1a alone appears to have been skipped by the extraction code for this entire report-format era.** Once the report format switched to the numbered Table-2-through-10 scheme (`Trueblood-Report-2019-10.pdf` onward), the equivalent table (now "Table 2") started being captured correctly, and WSH-evaluation-jail data resumes at period 2018-09 (first captured from `Trueblood-Report-2019-10.pdf`). Periods 2018-01 through 2018-08 are consequently absent from `washington.csv` for this facility/stage/setting combination **everywhere in the entire dataset**, even though the values are printed in multiple reports in this archive.

Confirmed directly against the PDF. `Trueblood-Report-2019-02.pdf`, page 7, Table 1a (verbatim, columns: orders signed / avg completion days / median completion days / pct within 7-days-signature / pct alt2 / pct alt3):
- Jan-18: 227 / 9.0 / 8.5 / 69% / 69% / 69%
- Feb-18: 235 / 8.9 / 9.0 / 75% / 75% / 76%
- Mar-18: 270 / 9.0 / 9.0 / 76% / 76% / 76%

`Trueblood-Report-2019-01.pdf`, page 7, same table, additionally shows Dec-17: 180, and continues through Dec-18: 201, 270 (Apr-18), 304 (May-18), 284 (Jun-18), 306 (Jul-18), 312 (Aug-18) — confirming Apr–Aug-18 values are likewise printed and available, just never extracted.

**Recommendation**: re-run extraction of Table 1a from `Trueblood-Report-2019-02.pdf` through `2019-09.pdf` (or equivalently `2018-11.pdf`/`2018-12.pdf`/`2019-01.pdf`) to backfill WSH-evaluation-jail for 2018-01–2018-08.

### Gap 2 — WSH+ESH combined ("TOTAL") tables missing early-2018 rows

`Trueblood-Report-2019-02.pdf` is the **only** report in the archive whose Table 3a/3b/3c trailing window reaches back to January 2018 (later reports' windows start later, since the window rolls forward each month and no earlier "Totals" report exists). Its Jan-18 row was not extracted for any of the three Totals tables, and (for Table 3b, WSH+ESH inpatient-evaluation totals) neither were Feb-18 or Mar-18. Confirmed directly against the PDF, page 13 (Table 3a) and page ~14–15 (Table 3b/3c):

- `TOTAL, evaluation, jail`, period 2018-01: missing. PDF (Table 3a, p.13): 300 orders / avg 9.9 / median 9.0 / 67% / 68% / 68%.
- `TOTAL, evaluation, inpatient`, periods 2018-01/02/03: missing. PDF (Table 3b): Jan-18 = 24 / 33.0 / 24.5 / 19%/19%/19%; Feb-18 = 11 / 44.1 / 44.0 / 8%/8%/8%; Mar-18 = 25 / 35.2 / 22.0 / 13%/13%/13%.
- `TOTAL, restoration, inpatient`, period 2018-01: missing. PDF (Table 3c): 94 / 46.7 / 39.5 / 9%/10%/10%.

All other months of these three Totals series (from Feb-18 or Apr-18 onward, depending on the series) are present and correct in the CSV, sourced from later reports as expected.

**Recommendation**: backfill these 5 period-rows (2018-01 × 3 series, plus 2018-02 and 2018-03 for `TOTAL evaluation inpatient`) from `Trueblood-Report-2019-02.pdf` pages 13–15.

### Gap 3 — October–December 2017 data is printed in the archive but is entirely absent from the CSV (added on independent re-verification pass)

`Trueblood-Report-2018-11.pdf`'s Table 1a (WSH jail-based evaluation, **p.7** — corrected here from an earlier miscitation of p.6, which is actually the "Outlier Cases (Mature)" page; verified directly by this auditor) and Table 1b (WSH inpatient, **p.8**, corrected from p.7) both begin their trailing series at **Oct-2017**, not Jan-2018: Oct-17 = 256 orders signed / 7.9 avg-days / 6.0 median / 12.6 avg-days-completion / 11.0 median-completion / 52%/53%/53%; Nov-17 = 262 orders / 69%/69%/70%; Dec-17 = 180 orders / 70%/70%/71%. Dec-17 = 180 is independently corroborated in `Trueblood-Report-2019-01.pdf`'s own Table 1a (p.7 — also corrected from a likely off-by-one citation, consistent with the same table numbering in that report), which agrees exactly. `washington.csv`'s earliest `period` value system-wide is `2018-01` (confirmed against the full CSV — no `2017-*` period exists anywhere in it). No WA source PDF earlier than `Trueblood-Report-2018-11.pdf` exists in `data/raw/wa/` other than the structurally-different `Trueblood-Report-2016-05.pdf` (see below), so this Oct–Dec-2017 data — for WSH-jail-eval, WSH-inpatient-eval/restoration, and the analogous ESH tables (pages 9–10 of `2018-11.pdf`), all of which share the same Oct-17 start point — is real, printed, and archived, but was never extracted into the public CSV. This is a third, distinct, bounded completeness gap (3 periods × up to 6 facility/stage/setting series), fully recoverable from `Trueblood-Report-2018-11.pdf` pages 7–10.

### Not a data-completeness gap, but a citation-utilization anomaly worth flagging — `Trueblood-Report-2020-03.pdf` and `Trueblood-Report-2020-04.pdf` are never cited anywhere in the CSV

Both PDFs were confirmed (independently, by reading their own pages) to contain full, populated Table 2–10 timeliness data — this is **not** a COVID-19-related suppression; both reports' COVID mentions are narrative-only (admissions-practice changes at WSH), and the numeric tables are fully populated. Yet neither PDF is cited as a source anywhere in `washington.csv` — 0 of 412 rows in this batch, and 0 rows in the whole dataset, cite either file.

Cross-checked whether this actually cost the dataset any data points: it does not appear to. `Trueblood-Report-2020-02.pdf` is an unusually large "catch-up" report whose Table 2–10 trailing window already covers periods 2019-01 through 2019-04 (confirmed: all 9 core facility/stage/setting combinations for periods 2019-02 and 2019-03 are present in the CSV, entirely sourced from `2020-02.pdf`), and `Trueblood-Report-2020-06.pdf`/`2020-07.pdf` similarly catch up through 2019-05 through 2019-08. The periods that `2020-03.pdf` and `2020-04.pdf` would have newly contributed therefore appear to already be covered by the neighboring catch-up reports. This looks like a byproduct of the "most recent report wins" period-selection design (see Design Note below) rather than lost data — but because two entire source files go completely unused, it is flagged here so a maintainer can confirm no period/combination was silently dropped in the process.

---

## Investigated and ruled out (documented so the reasoning is auditable)

- **`Trueblood-Report-2019-09.pdf`** (format-transition report, old lettered scheme → new numbered scheme): a sub-audit initially flagged this as capturing only 1 of a much larger available row set (its Tables 2–10 print full 13-month series, not just one row). On cross-checking the whole dataset by period, every one of those series' Aug-18 (or Jul-18, for the one table whose window is offset) values turned out to already be present in the CSV, sourced from `2019-05.pdf` through `2019-09.pdf` — **except** the WSH-evaluation-jail row, which is exactly Gap 1 above (already counted there, not a separate issue). So this report's real, unique contribution is correctly limited to the single WSH-restoration Table 4 row the CSV captured.
- **`Trueblood-Report-2020-02.pdf`**: one row (`WSH evaluation jail`, period 2019-04, Table 2, p.9: 322/347/11.7/12.0/82%/86%/86%) looked at first like a missing row. It is not — the CSV's actual 2019-04 value for that combination (322/**346**/11.7/12.0/**83**%/86%/86%) is sourced from the later `Trueblood-Report-2020-05.pdf`, which prints a slightly revised figure (347→346 completed, 82%→83%) for the same month. Both source pages were independently confirmed to print exactly what their respective CSV rows say; the CSV correctly kept the more recent (revised) report's number per the dataset's documented "most recent report wins" design.
- **`Trueblood-Report-2021-02.pdf`**: lacks a Table 10 row in the CSV for its own period (2020-01), even though Table 10 exists and is populated on page 21 of that PDF. Confirmed the 2020-01 and 2020-02 Table 10 values are present and numerically correct in the CSV, just attributed to the neighboring reports (`2021-01.pdf`, `2021-03.pdf`) instead — a source-attribution quirk of the pipeline's period-deduplication, not missing data.
- **`Trueblood-Report-2021-08.pdf`** (3 CSV rows) and **`Trueblood-Report-2022-04.pdf`** (3 CSV rows): both look sparse relative to their full Table 2–10 content, but in both cases every other facility/stage/setting/period combination that report contains was confirmed present and numerically correct elsewhere in the CSV, cited from the immediately adjacent report. No gap.
- **`Trueblood-Report-2020-05.pdf`, `2020-08.pdf`, `2020-09.pdf`** (1 CSV row each, all just a revised WSH-eval-jail Table 2 figure): each period's full 10-table dataset was confirmed already captured from an earlier or later "mature" report; these three reports' sole contribution is a subsequently-revised single figure. No gap.
- **RTF (`facility=RTF, stage=restoration, setting=inpatient`) missing 2018-01 through 2018-07**: this is a genuine, disclosed **source-side** non-existence, not a pipeline defect — the PDFs themselves state "Data for January - July 2018 is not included because during those months, the RTF data was combined with the WSH data" (`Trueblood-Report-2019-02.pdf`, Table 1c footnote 1).
- **OCRP (`facility=OCRP, stage=restoration, setting=outpatient`) missing before 2020-07**: consistent with the Outpatient Competency Restoration Program's real-world 2020 launch; `Trueblood-Report-2021-05.pdf`'s Table 4c footnote confirms OCRP was not yet implemented for the period it covers (Apr-20), and the CSV's first OCRP row (period 2020-07) matches this.
- **`Trueblood-Report-2021-03.pdf`, Table 9, page 20**: the source PDF itself prints the identical average-days value ("14.8") on every single monthly row from Feb-20 through Feb-21, while the median and percent-complete columns vary normally — this looks like a DSHS data-entry defect in the *source* document, not an extraction error. The CSV's Feb-20 value (14.8) is a byte-for-byte faithful transcription of what the PDF prints. Flagged for awareness; not a dataset error. (Confirmed the defect is specific to this one report's printing — `Trueblood-Report-2021-04.pdf`'s equivalent Table 9 shows a normal, varying Mar-20 value of 48.8.)

**Design note (applies broadly across 2019-10 through 2022-07 reports):** each monthly report reprints a rolling ~13-month trailing table per facility/stage/setting. The pipeline consistently waits for a period's figures to mature (typically the report published ~12–14 months after the period) before recording it, and keeps whichever report most recently touched that period if the underlying DSHS figure was later revised (directly confirmed: `Trueblood-Report-2022-03.pdf` and `2022-04.pdf` print different avg-days values, 12.0 vs. 10.9, for the same Mar-21 WSH-jail-eval row). This is a legitimate methodological choice documented in `docs/PIPELINE.md` ("keeps the value from the most recent report that successfully covers a given period"), not a data error — but it does mean a report dated "202X-MM" should not be assumed to contribute data about month MM, and a report contributing few or zero rows is not, by itself, evidence of a defect (most of the "sparse report" cases investigated above turned out to be this pattern, not gaps).

---

## Per-report results

### 2016
- **Trueblood-Report-2016-05.pdf — 0 CSV rows. Confirmed completeness gap (dataset-scope, not this-report-specific).** This report's "Class Member Status Data Tables" (PDF pages 8–10) print full monthly Western State Hospital / Eastern State Hospital / Totals timeliness data (orders signed, avg/median days, percent complete within 7 days) for April 2015 through April 2016, broken out by Jail-based Evaluation, Inpatient Evaluation, and Inpatient Restoration. None of this is in `washington.csv` — the dataset's earliest period is 2018-01 system-wide (confirmed: no 2015/2016/2017 period exists anywhere in the CSV). This is evidently a deliberate scope boundary (2018-01 onward) rather than an extraction failure specific to this file, but it is worth the maintainer stating explicitly in `docs/PIPELINE.md`'s Coverage section, since the source PDF (assigned as in-scope for this archive) does contain usable pre-2018 data that a reader might reasonably expect to find.

### 2018–2019 (verified directly by this auditor)
- **Trueblood-Report-2018-11.pdf — 0 CSV rows. Confirmed completeness gap.** Contains Table 1a/1b/2a/2b (p.7–10) with a trailing Nov-17–Oct-18 series (WSH/ESH × jail-eval/inpatient — the inpatient tables combine evaluation and restoration sub-blocks in this report era). None captured. This report predates the CSV's 2018-01 floor for its newest month coverage in some series but contains Jan-18 through Oct-18 data relevant to Gap 1/Gap 2 above.
- **Trueblood-Report-2018-12.pdf — 0 CSV rows. Confirmed completeness gap**, same table structure (Table 1a/1b/2a/2b), trailing Dec-17–Nov-18.
- **Trueblood-Report-2019-01.pdf — 0 CSV rows. Confirmed completeness gap**, same table structure, trailing Dec-17–Dec-18 (full table read and transcribed above as supporting evidence for Gap 1).
- **Trueblood-Report-2019-02.pdf — CLEAN, 14 rows checked.** Tables 1b, 1c, 2a, 2b, 2c (pages 8–12), periods Jan/Feb/Mar-18 plus one Aug-18 RTF row. All 14 rows match the printed PDF exactly on every numeric field. (Table 1a, 3a, 3b, 3c on this same report are the source of Gap 1/Gap 2 above.)
- **Trueblood-Report-2019-03.pdf — CLEAN, 5 rows checked.** Tables 2a (p.10), 3a (p.13), 3c (p.15), periods Feb/Mar-18. All match exactly.
- **Trueblood-Report-2019-04.pdf — CLEAN, 1 row checked.** Table 3a (p.13), period Mar-18 (TOTAL eval/jail: 345/335/9.7/9.0/71%/72%/72%). Matches.
- **Trueblood-Report-2019-05.pdf — CLEAN, 15 rows checked.** Tables 1b/1c/2a/2b/2c/3a/3b/3c (pages 8–15), periods Apr–Aug 2018. All match exactly.
- **Trueblood-Report-2019-06.pdf — CLEAN, 9 rows checked.** Tables 1c/2a/2c/3c, periods May–Jul 2018. All match exactly.
- **Trueblood-Report-2019-07.pdf — CLEAN, 11 rows checked.** Tables 1b/2a/2b/3b/3c, periods Jun–Aug 2018. All match exactly.
- **Trueblood-Report-2019-08.pdf — CLEAN, 4 rows checked.** Tables 2a, 3c, periods Jul/Aug 2018. All match exactly.
- **Trueblood-Report-2019-09.pdf — CLEAN, 1 row checked.** Table 4 (WSH sub-table, p.10), period Aug-18 (WSH restoration/inpatient: 71/61/54.1/56.0/21%/20%/21%). Matches. (See "Investigated and ruled out" above re: this report's broader table content.)
- **Trueblood-Report-2019-10.pdf — CLEAN, 10 rows checked.** Tables 2–10 (pages 8–16), period Sep-18. All 10 rows match exactly. First report using the new numbered table scheme; format-transition tables (1, 11–18: outlier cases, monthly-summary rollups, RTF facility detail, implementation steps, court-order-status) correctly have no row-level CSV representation since they are a different data shape, not the same facility/stage/setting grain.
- **Trueblood-Report-2019-11.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Oct-18. All match exactly. (Row count corrected from an earlier miscount of 11 in a prior draft — verified directly against the CSV.)
- **Trueblood-Report-2019-12.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Nov-18. All match exactly. (Row count corrected from an earlier miscount of 11.)

### 2020
- **Trueblood-Report-2020-01.pdf — CLEAN, 10 rows checked.** Tables 2, 3, 4a, 4b, 5–10, period Dec-18. All match exactly. (Row count corrected from an earlier miscount of 11.)
- **Trueblood-Report-2020-02.pdf — CLEAN, 39 rows checked** (a "catch-up" report whose trailing tables cover Jan–Apr 2019 across all 9 core facility/stage/setting combinations). All 39 rows match the PDF exactly. (The one row that initially looked missing — Apr-19 WSH-eval-jail — is not missing; see "Investigated and ruled out.")
- **Trueblood-Report-2020-03.pdf — 0 CSV rows.** See "Confirmed completeness gap" note above (citation-utilization anomaly; underlying periods appear covered elsewhere).
- **Trueblood-Report-2020-04.pdf — 0 CSV rows.** Same as above.
- **Trueblood-Report-2020-05.pdf — CLEAN, 1 row checked.** Table 2, period Apr-19 (322/346/11.7/12.0/83%/86%/86%). Matches.
- **Trueblood-Report-2020-06.pdf — CLEAN, 10 rows checked.** Tables 2–10, period May-19. All match exactly. (Row count corrected from an earlier miscount of 11.)
- **Trueblood-Report-2020-07.pdf — CLEAN, 28 rows checked.** Tables 2–10, periods Jun/Jul/Aug-19 (a second catch-up report). All match exactly. (Row count corrected from an earlier miscount of 27.)
- **Trueblood-Report-2020-08.pdf — CLEAN, 1 row checked.** Table 2, period Jul-19 (388/379/12.3/13.0/75%/79%/80%). Matches.
- **Trueblood-Report-2020-09.pdf — CLEAN, 1 row checked.** Table 2, period Aug-19 (368/360/11.7/12.0/81%/86%/89%). Matches.
- **Trueblood-Report-2020-10.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Sep-19. All match exactly.
- **Trueblood-Report-2020-11.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Oct-19. All match exactly.
- **Trueblood-Report-2020-12.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Nov-19. All match exactly.

### 2021
- **Trueblood-Report-2021-01.pdf — CLEAN, 11 rows checked.** Tables 2–10, period Dec-19, plus one Jan-20 Table 10 row. All match exactly.
- **Trueblood-Report-2021-02.pdf — CLEAN, 9 rows checked.** Tables 2–9, period Jan-20. All match exactly. (Table 10 attribution — see "Investigated and ruled out.")
- **Trueblood-Report-2021-03.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Feb-20. All match exactly (including the Table 9 avg-days figure that is itself a likely source-side DSHS defect — see note above; the CSV faithfully transcribes what's printed).
- **Trueblood-Report-2021-04.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Mar-20. All match exactly.
- **Trueblood-Report-2021-05.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Apr-20. All match exactly. (Table 4c/OCRP correctly has no Apr-20 row — program not yet implemented.)
- **Trueblood-Report-2021-06.pdf — CLEAN, 10 rows checked.** Tables 2–10, period May-20. All match exactly.
- **Trueblood-Report-2021-07.pdf — CLEAN, 18 rows checked.** Tables 2–10, periods Jun/Jul-20. All match exactly.
- **Trueblood-Report-2021-08.pdf — CLEAN, 3 rows checked.** Table 4b, 4c, 10, period Jul-20 (OCRP's first-ever nonzero-eligible period, still 0 orders). All match exactly; full period coverage confirmed present via the adjacent report (see "Investigated and ruled out").
- **Trueblood-Report-2021-09.pdf — CLEAN, 11 rows checked.** Tables 2–10, period Aug-20 — first report where OCRP (Table 4c) has a genuine nonzero value (2 signed/1 completed/4.0/4.0/100%/100%/100%). Matches.
- **Trueblood-Report-2021-10.pdf — CLEAN, 10 rows checked.** Tables 2–10, period Sep-20. All match exactly.
- **Trueblood-Report-2021-11.pdf — CLEAN, 12 rows checked.** Tables 2–10 (11 sub-tables incl. 4a/4b/4c), period Oct-20, plus 1 additional OCRP (Table 4c) row for Sep-20 (2 signed/3 completed/6.3/7.0/100%/100%/100%, page 15). All 12 match exactly. (Corrected from an earlier miscount of "13 rows / 2 additional OCRP rows" in a prior draft of this file — verified directly against the CSV and PDF page 15.)
- **Trueblood-Report-2021-12.pdf — CLEAN, 11 rows checked.** Tables 2–10, period Nov-20. All match exactly.

### 2022
- **Trueblood-Report-2022-01.pdf — CLEAN, 11 rows checked.** Tables 2–10, period Dec-20. All match exactly.
- **Trueblood-Report-2022-02.pdf — CLEAN, 11 rows checked.** Tables 2, 3, 4a, 4b, 4c, 5–10 (pages 12–23), period Jan-21. Independently verified twice (once via a sub-audit, once via this auditor's own spot check of Table 2, p.12: 266/245/12.8/13.0/76%/79%/80% — matches). All 11 rows match exactly.
- **Trueblood-Report-2022-03.pdf — CLEAN, 19 rows checked** (periods Feb-21 and Mar-21, two-period structure reflecting the report's own "mature"/"first-look" split — Tables 2/5/10 carry only the Feb-21 row from this report, since their Mar-21 value is instead cited from `2022-04.pdf`, see below). All 19 values match exactly. A revision was confirmed between this report and the next month's report for the Mar-21 WSH-jail-eval avg-days figure (12.0 here vs. 10.9 in `2022-04.pdf`) — both cited values independently match their own source page; this is the underlying DSHS data being revised between reports, not a CSV error (see Design Note). Directly re-verified by this auditor.
- **Trueblood-Report-2022-04.pdf — CLEAN, 3 rows checked.** Table 2, 5, 10, period Mar-21 (345/310/10.9/12.0/91%/94%/95%; 83/81/12.0/11.0/68%/78%/88%; 121/176/48.9/43.0/9%/10%/10%). All match exactly; the other 8 combinations for Mar-21 are captured from `2022-03.pdf` with matching values — the two reports are complementary, not overlapping or gapped. Directly re-verified by this auditor, including checking all tables on this PDF's pages 12–23 for any unlisted combination — none found.
- **Trueblood-Report-2022-05.pdf — CLEAN, 11 rows checked.** Tables 2–10, period Apr-21. All match exactly. Directly re-verified by this auditor.
- **Trueblood-Report-2022-06.pdf — CLEAN, 11 rows checked.** Tables 2–10, period May-21. All match exactly.
- **Trueblood-Report-2022-07.pdf — CLEAN, 11 rows checked.** Tables 2–10, period Jun-21. All match exactly.

---

## Summary

| | Count |
|---|---|
| Reports in batch | 46 |
| CSV rows in batch | 412 |
| Rows checked, numeric value matched PDF exactly | 412 / 412 |
| Value-level (wrong-number) discrepancies | 0 |
| Confirmed completeness gaps (data printed in an in-scope PDF, never entered the CSV, and not recoverable from any other report) | 3 (WSH-evaluation-jail × 8 periods, Gap 1; WSH+ESH Totals × 5 period-rows, Gap 2; Oct–Dec-2017 data across up to 6 series, Gap 3) — Gap 1/2 traceable to `Trueblood-Report-2019-02.pdf` and its sibling old-format reports, Gap 3 to `Trueblood-Report-2018-11.pdf`/`2019-01.pdf` |
| Reports entirely un-cited despite containing real, populated data (`2020-03.pdf`, `2020-04.pdf`) | 2 — flagged, but underlying periods appear recoverable elsewhere in the dataset |
| Reports with 0 CSV rows because they predate the dataset's 2018-01 scope floor | 4 (`2016-05.pdf`, `2018-11.pdf`, `2018-12.pdf`, `2019-01.pdf`) |
| Likely source-side (DSHS) data defect, faithfully transcribed | 1 (`2021-03.pdf` Table 9 repeated avg-days value) |

No fabricated, mis-transcribed, or wrong-facility/wrong-period numbers were found anywhere in this batch. The three confirmed completeness gaps affect a bounded, identifiable set of period-rows (8 for WSH-evaluation-jail 2018-01–2018-08, 5 for the WSH+ESH Totals series in early 2018, plus Oct–Dec-2017 across the WSH/ESH jail-eval and inpatient series), all independently backfillable from `Trueblood-Report-2019-02.pdf` / `Trueblood-Report-2018-11.pdf` (and sibling reports for cross-confirmation), all cited above with the exact printed values.
