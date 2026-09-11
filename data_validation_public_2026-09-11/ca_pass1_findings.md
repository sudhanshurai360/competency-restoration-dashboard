# California DSH Data — Independent Audit Pass 1

Auditor: independent verification pass (fresh read of the raw PDFs, no reliance on
code comments, prior notes, or CSV metadata).

Scope: `data/derived/california.csv` — 25 rows, metric `ist_pending_placement`.
Method: extracted the exact cited `pdf_page` from each raw PDF in `data/raw/ca/`
with `pdftotext -layout` (page-accurate, matches physical PDF pagination), read the
printed text, and compared the printed number/date against the CSV `value` and
`period`. Also recomputed SHA-256 (first 12 hex chars) of every PDF on disk and
compared to the `source_sha` column. Also full-text-scanned every PDF for any
additional dated IST-waitlist figures not captured in the CSV.

## Result: all 25 rows verified CORRECT. No value errors, no mis-cited pages, no
provenance (hash/report) mismatches found.

## Per-PDF breakdown (25/25 rows CLEAN)

**may2024-25.pdf** — 4 rows, CLEAN
- 2019-06 = 849 (p125, Table 2, FY2018-19 column) — confirmed
- 2022-07 = 1,718 (p125, prose: "1,718 patients in July 2022") — confirmed
- 2023-06 = 894 (p125, Table 2 FY2022-23 column, and prose "894 patients in June 2023") — confirmed
- 2024-05 = 397 (p14, prose: "down to 397 as of May 6, 2024") — confirmed, dated footnote in-line

**may2025-26.pdf** — 6 rows, CLEAN
- 2020-02 = 850 (p66, prose: "in February 2020, DSH had 850 individuals pending placement") — confirmed
- 2020-06 = 1,212 (p127, Table 2 FY2019-20 column) — confirmed
- 2023-07 = 910 (p127, prose: "910 patients in July 2023") — confirmed
- 2024-06 = 425 (p127, Table 2 FY2023-24 column, prose "425 patients in June 2024") — confirmed
- 2024-09 = 384 (p127, prose: "384 patients pending placement as of September 30, 2024") — confirmed
- 2025-05 = 278 (p67, prose: "278 individuals on the waitlist," footnote 5 = "Data as of May 7, 2025") — **specially verified per task, CONFIRMED**

**may2026-27.pdf** — 7 rows, CLEAN
- 2021-06 = 1,454 (p125, Table 2 FY2020-21 column) — confirmed
- 2022-01 = 1,953 (p15, prose: "high of 1,953 ... as of January 2022") — confirmed
- 2022-06 = 1,779 (p125, Table 2 FY2021-22 column) — confirmed
- 2024-07 = 383 (p125, prose: "383 patients in July 2024") — confirmed
- 2025-06 = 287 (p125, Table 2 FY2024-25 column, prose "287 patients in June 2025") — confirmed
- 2025-08 = 277 (p125, prose: "277 patients pending placement as of August 25, 2025") — confirmed
- 2026-05 = 256 (p59, prose: "there are 256⁴ individuals on the waitlist," footnote 4 = "Data as of May 12, 2026") — **specially verified per task (dataset LATEST reading), CONFIRMED unambiguous.** The footnote marker "4" is attached directly to the "256" figure in two consecutive sentences ("there are 256⁴ individuals..." and "of the 256 individuals on the waitlist pending admission..."), and footnote 4 at the bottom of the page reads exactly "Data as of May 12, 2026." No other nearby number (129, 98, 6, 275) carries this footnote or this date. Unambiguous.

**may2022-23.pdf** — 1 row, CLEAN
- 2022-02 = 1,951 (p15, prose: "increased by 125 percent to 1,951 as of February 28, 2022") — confirmed

**gov2023-24.pdf** — 2 rows, CLEAN
- 2022-08 = 1,737 (p14, prose: "increased by almost 100 percent to 1,737 as of August 29, 2022") — confirmed
- 2022-12 = 1,473 (p91, prose: "As of December 12, 2022, the waitlist has declined to 1,473") — confirmed

**may2023-24.pdf** — 1 row, CLEAN
- 2023-04 = 804 (p91, prose: "declined to 804 as of April 3, 2023") — confirmed

**gov2024-25.pdf** — 2 rows, CLEAN
- 2023-11 = 549 (p17, prose: "down to 549 as of November 6, 2023") — confirmed
- 2024-01 = 501 (p69, prose: "the IST waitlist is currently at 501⁹," footnote 9 = "Data as of January 1, 2024.") — **specially verified per task, CONFIRMED**. Report is a "gov2024-25.pdf"-style file as expected.

**gov2025-26.pdf** — 1 row, CLEAN
- 2025-01 = 359 (p18, prose: "down to 359 as of January 1, 2025") — confirmed

**gov2026-27.pdf** — 1 row, CLEAN
- 2026-01 = 275 (p50, prose: "there are 275⁴ individuals on the waitlist," footnote 4 = "Data as of January 5, 2026") — **specially verified per task, CONFIRMED**

## Provenance / hash check

Recomputed SHA-256 of all 9 PDFs on disk and compared first 12 hex chars to the
`source_sha` column for every row citing that report. All match exactly, e.g.:

| file | sha256(12) | matches CSV rows citing it |
|---|---|---|
| gov2023-24.pdf | 22a233b5a56b | yes |
| gov2024-25.pdf | 2b6b2aea54e7 | yes |
| gov2025-26.pdf | 22afa42c6038 | yes |
| gov2026-27.pdf | 21b69d7476bd | yes |
| may2022-23.pdf | 33f881887503 | yes |
| may2023-24.pdf | 4548799cca7d | yes |
| may2024-25.pdf | 654f3ec78ae2 | yes |
| may2025-26.pdf | e1d747e0e150 | yes |
| may2026-27.pdf | f4933cdccac3 | yes |

No file/report swaps or stale hashes found.

## Completeness check — ONE GAP FOUND (not an error, an omission)

Full-text scan of all 9 PDFs for "waitlist"/"pending placement"/"Data as of"
mentions found no numeric discrepancies with any existing CSV row — every
recurring restatement of a historical figure (e.g. 1,953 cited repeatedly across
later reports; 501; 359; 278; 275; etc.) is internally consistent with the CSV.

However, **two independent PDFs contain a dated Table 1 ("Pre and Post SIP Order
Waitlist and Weekly Referral Averages") with two additional dated IST waitlist
point-readings that are NOT present as rows in the CSV**:

- **IST waitlist = 869, dated 3/16/2020** ("Pre-SIP Waitlist")
- **IST waitlist = 1,144, dated 5/25/2020** ("Post-SIP Waitlist")

Confirmed present, with identical values, in two separate reports:
- `gov2023-24.pdf`, page 15 (printed "Page 5 of 9", Section A3(c))
- `may2022-23.pdf`, page 16 (printed footer "2022-23 May Revision Estimate")

Both tables also restate the then-current waitlist figure in the same row format
(1,737 as of 8/29/2022 in gov2023-24.pdf; 1,951 as of 2/28/2022 in
may2022-23.pdf) — those current-waitlist figures are already correctly captured
in the CSV as the 2022-08 and 2022-02 rows respectively. It is only the two
older "Pre-SIP" (3/16/2020) and "Post-SIP" (5/25/2020) columns that are missing
as CSV rows.

This is a genuine completeness gap: the CSV currently jumps from 2019-06 (849)
to 2020-02 (850) to 2020-06 (1,212), skipping two dated intermediate readings
(2020-03 = 869 and 2020-05 = 1,144) that exist, cross-confirmed, in the source
material. Recommend either (a) adding these two rows with `table_ref = "Table 1"`
citing both source PDFs, or (b) if the "Pre-SIP"/"Post-SIP" snapshot dates were
deliberately excluded as a different measurement methodology than the other
snapshots (e.g., possibly a different counting rule tied specifically to the SIP-order
before/after comparison rather than the standard monthly-snapshot series), noting
that decision explicitly in the dataset README/methodology so a future auditor
does not flag it again.

No other omissions found. No other PDF in the archive contains a dated
IST-pending-placement reading absent from the CSV.

## Summary table

| Report | Rows in CSV | Status |
|---|---|---|
| may2024-25.pdf | 4 | CLEAN |
| may2025-26.pdf | 6 | CLEAN |
| may2026-27.pdf | 7 | CLEAN |
| may2022-23.pdf | 1 | CLEAN |
| gov2023-24.pdf | 2 | CLEAN — but see completeness gap above (Table 1, p15) |
| may2023-24.pdf | 1 | CLEAN |
| gov2024-25.pdf | 2 | CLEAN |
| gov2025-26.pdf | 1 | CLEAN |
| gov2026-27.pdf | 1 | CLEAN |
| **Total** | **25** | **25/25 rows verified correct; 1 completeness gap (2 missing datapoints) identified** |
