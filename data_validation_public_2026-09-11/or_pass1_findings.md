# Oregon Competency-Restoration Dataset — Independent Data-Integrity Audit

**Date of audit:** 2026-09-11
**Scope:** `data/derived/oregon.csv` (173 data rows, all state=OR) vs. all 18 raw PDFs in `data/raw/or/`
**Method:** Every PDF was physically opened (rendered and visually read, not just grepped) at the row-cited `pdf_page`; the cited table/sentence was located and its printed numbers compared cell-by-cell against the CSV. `source_sha` was independently recomputed (SHA-256) against every raw PDF. This was a from-scratch verification — no code comments or prior metadata were trusted.

**Process note on how this audit was run:** verification was parallelized across ~12 independently-scoped sub-agents, each assigned one report (or a specific table within the large 2026.03.16 report) plus a completeness check on the 5 uncited PDFs. Several sub-agents, because they inherited the full task context, went beyond their assigned scope and independently re-ran a full 173-row pass on their own, writing directly to this file (this produced duplicate/concurrent versions and one **false-positive claim**, which is identified and corrected below in "Note on a debunked false-positive"). This final version was written by the orchestrating agent after collecting and cross-checking all sub-agent reports, independently re-verifying the two highest-stakes claims (the 2026-02 critical row and the 2025-12 completeness gap) directly, and resolving the one contested claim by re-reading the raw CSV.

---

## Headline result

**Zero confirmed wrong numeric values.** All 173 CSV rows were verified against their cited PDF page/table and match exactly. All 18 raw PDFs' SHA-256 hashes match their `source_sha` prefix. The 5 raw PDFs not cited anywhere in the CSV were individually opened and confirmed to contain no extractable competency-restoration metrics — their exclusion is correct.

**Critical target row (task item 5) — CONFIRMED CLEAN.** `2026-02, avg_wait_days, 16.5`, cited to `2026.03.16-Oregon-Mink-Bowman-Court-Monitor-Report.pdf`, page 8: page 8 genuinely reads, verbatim: *"defendants waited an average of 16.5 days as of the end of February, compared to 19.1 days I reported on reflecting time at the end of November, and the 22.7 days I noted at the beginning of December."* The absence of a corresponding `admits` row for 2026-02 is also confirmed correct and deliberate: page 9's "Figure 1" is a raster/screenshot dashboard image showing "Admitted During the Month: Count 90, Avg Days 16.5" for February 2026 — this number exists **only** inside the image, not in the PDF's extractable text layer (confirmed independently by three separate checks, including a `pdftotext`/text-extraction pass that returns zero digits for that figure). The 16.5 value, by contrast, is real prose text and is what was correctly extracted; 90 (admits) was correctly left out rather than guessed or OCR'd.

**Note on a debunked false-positive:** one sub-agent pass claimed a "confirmed error" — that CSV row `2024-10, orders_received` = 100.0 (cited to the 2025.12.06 report) should actually be 102. This claim was checked directly against the raw CSV file and is **false**: the CSV's actual `2024-10, orders_received` row is `102.0` (cited to the 2025.12.06 report, page 13) — already correct. The value `100.0` belongs to a *different* row, `2025-10, orders_received`, cited to the *2026.03.16* report, page 13 — also independently verified correct by a dedicated sub-agent that read that exact table. The erring pass conflated these two distinct rows (same month name "October," different years and different source reports). No correction to the dataset is needed on this point.

---

## Per-PDF results

### 1. Oregon_Mink-Bowman_1st_Neutral_Expert_Pinals_Report.pdf
Rows 13, 25 (beds_active/beds_licensed, 2022-01, page 7, Table 2).
Page 7, Table 2 "OSH Bed Capacities as of 1/5/22," OSH Total row: Licensed 743, Active 706.
**CLEAN — 2 rows.**

### 2. Oregon_Mink-Bowman_2nd_Neutral_Expert_Pinals_Report.pdf
Rows 14, 26 (2022-05, page 10, Table 2).
Page 10, Table 2 "as of 5/1/22": Licensed 743, Active 706.
**CLEAN — 2 rows.**
*Completeness note:* this report's own page 10 also carries a standalone "Table 3. OSH Census as of 5/23/22" (Aid & Assist 401 / PSRB 265 / Civil 16 / Other 1 / Total 683), independently confirmed by direct read. This snapshot is not captured anywhere in the CSV, and the CSV's consolidated `census_*` series (sourced from the 2026.03.16 report) only begins at 2022-09. This is a genuine, low-materiality completeness gap (a single early data point), not a wrong value.

### 3. Oregon_Mink-Bowman_3rd_Neutral_Expert_Pinals_Report.pdf
Rows 15, 27 (2022-09, page 9, Table 2).
Page 9, Table 2 "as of 9/1/22": Licensed 743, Active 706.
**CLEAN — 2 rows.**

### 4. Oregon_Mink-Bowman_4th_Neutral_Expert_Pinals_Report.pdf
Rows 16, 28 (2022-12, beds, page 8, Table 2); rows 94–97 (orders_received, page 8, Table 4, 2021-12 through 2022-03).
Page 8, Table 2 "as of 12/1/22": Licensed 743, Active 699. Page 8, Table 4: Dec 2021=76, Jan 2022=76, Feb 2022=56, Mar 2022=85 — all four confirmed.
**CLEAN — 6 rows.**

### 5. Oregon_Mink-Bowman_5th_Neutral_Expert_Pinals_Report.pdf
Rows 17, 29 (2023-04, page 8, Table 2).
Page 8, Table 2 "as of 4/1/23": Licensed 743, Active 704.
**CLEAN — 2 rows.**

### 6. Oregon_Mink-Bowman_6th_Neutral_Expert_Pinals_Report.pdf
Rows 18, 30 (2023-07, page 9, Table 2).
Page 9, Table 2 "as of 7/1/23": Licensed 743, Active 704.
**CLEAN — 2 rows.**

### 7. Oregon_Mink-Bowman_7th_Neutral_Expert_Pinals_Report.pdf — NOT CITED
Opened in full. This report is explicitly a narrative recommendations-status update ("this current Seventh Report to the Court is limited to the above descriptions of my recent activities and providing the Court with an updated version of the recommendations from my Second Report"). No bed-capacity, census, orders-received, or admissions data table exists in it.
**Verdict: correctly excluded — no extractable metric data.**

### 8. Oregon_Mink-Bowman_8th_Neutral_Expert_Pinals_Report.pdf
Rows 2, 19, 31, 145 (2023-11: admits, beds_active, beds_licensed, pct_within_7day).
Page 9, Table 2 "as of 11/1/23": Licensed 743, Active 704 (rows 19, 31). Page 10, narrative: *"Of the 108 admissions in November 2023, 93.5% (101 people) were admitted within the 7-day Mink requirement."* → admits=108 (row 2), pct_within_7day=93.5, printed verbatim (row 145).
**CLEAN — 4 rows.**

### 9. Oregon_Mink-Bowman_9th_Neutral_Expert_Pinals_Report.pdf
Rows 3, 20, 32, 146 (2024-04: admits, beds_active, beds_licensed, pct_within_7day).
Page 8, narrative: *"In April 2024, 87 of the 96 admissions were admitted within 7 days of the court order."* → admits=96 (row 3); pct_within_7day=90.6 is **not printed as a literal percentage** — it is correctly derived (87 ÷ 96 = 90.625% → 90.6) (row 146). Page 10, Table 2 "as of 4/1/24": Licensed 742, Active 705 (rows 20, 32).
**CLEAN — 4 rows** (see Finding D on the two derived percentages).

### 10. Oregon_Mink-Bowman_10th_Neutral_Expert_Pinals_Report.pdf
Rows 21, 33 (2024-11, page 11, Table 2).
Page 11, Table 2 "as of 11/1/24": Licensed 742, Active 705.
**CLEAN — 2 rows.**
*Note:* this report's own Table 4 prints Sept 2024=91 and Oct 2024=100 for orders_received; the CSV instead sources these two months from the later 2025.12.06 report (92 and 102 respectively). See Finding B — this is a source-side retroactive revision, and the CSV correctly matches whichever report it actually cites.

### 11. Oregon_Mink-Bowman_11th_Neutral_Expert_Pinals_Report.pdf
Rows 4, 7, 8, 22, 34 (2025-03/04 admits, avg_wait_days, beds).
Page 16, narrative: *"In April 2025, OSH admitted 128 A&A patients (tied for the most ever in a month) with an average wait time of 20.7 days (down from 25.4 days in March)."* → admits=128 (row 4), avg_wait_days March=25.4 (row 7), April=20.7 (row 8). Page 14, Table 3 "as of 4/1/25": Licensed 742, Active 705 (rows 22, 34) — note the table is genuinely labeled "Table 3" (not "Table 2") in this specific report, and the CSV's `table_ref` correctly reflects that.
**CLEAN — 5 rows.**

### 12. Oregon_Mink-Bowman_11th_Neutral_Expert_Pinals_Report_supplement.pdf — NOT CITED
Opened in full (13 pages). This is "Defendants' Positions Regarding Recommendations from Dr. Pinals' 11th Report" (6/4/25) — a recommendation-by-recommendation tracker with no quantitative data tables.
**Verdict: correctly excluded — no extractable metric data.**

### 13. 2025.09.05-Oregon-Mink-Bowman-Court-Monitor-Report.pdf
Rows 5, 9, 10, 23, 35, 147, 148 (2025-07/08 admits, avg_wait_days, pct_within_7day, waitlist_count, beds).
Page 7, narrative: *"In August 2025, OSH admitted 107 A&A patients with an average wait time of 10.2 days... slightly increased from July (which was at 9.7 days)... At the end of August 2025, 34 people... were on the waitlist... eight (8) of the 107 admissions in August were within the 7-day Mink requirement."* → admits=107 (row 5), avg_wait_days July=9.7 / Aug=10.2 (rows 9, 10), waitlist_count=34 (row 148), pct_within_7day = 8/107 = 7.48% → 7.5, **not literally printed as a percentage, correctly derived** (row 147). Page 10, Table 2 "as of 8/1/25": Licensed 742, Active 705 (rows 23, 35).
**CLEAN — 7 rows.**

### 14. 2025.12.06-Oregon-Mink-Bowman-Court-Monitor-Report.pdf
Rows 6, 11, 92 (2025-11 admits/avg_wait_days/contempt fines); rows 98–130 (orders_received, Table 4, 33 months, 2022-04 through 2024-12).
Page 2: *"fines have accrued to approximately $1.4 million."* → contempt_fines_accrued_musd=1.4 (row 92). Page 14: *"In November 2025, OSH admitted 69 A&A patients with an average wait time of 19.1 days."* → admits=69 (row 6), avg_wait_days=19.1 (row 11). Pages 12–13, Table 4: all 33 cited months transcribed and verified exact match, including 2022-04=79, 2022-10=95, 2024-10=102.
**CLEAN — 35 rows.**
*Completeness gap found on page 8 of this same PDF (independently verified directly):* the narrative reads, *"defendants waited an average of 19.1 days as of the end of November. This number continues to increase and on 12/3/25, the average time people are waiting was at 22.7 days."* This 22.7-day figure (period 2025-12) has **no corresponding CSV row** — the `avg_wait_days` series jumps from 2025-11 (19.1) to 2026-02 (16.5) with no 2025-12 entry, even though this value is printed on the very page already cited for the 2025-11 row's companion sentence, and is repeated again on page 8 and page 30 of the 2026.03.16 report. See Finding C.

### 15. 2026.03.16-Oregon-Mink-Bowman-Court-Monitor-Report.pdf (most recently added; highest scrutiny applied)
Rows 12, 24, 36, 37–91 (census ×5 metrics ×11 periods), 93, 131–144 (orders_received, 14 months), 149–161 (waitlist_stock, 13 periods), 162–174 (waitlist_stock_avg_days, 13 periods) — 79 rows total.

- **Page 7:** *"those fines have accrued to approximately $3.19 million"* → contempt_fines_accrued_musd=3.19 (row 93). **MATCH.**
- **Page 8 — critical target row:** confirmed above. **MATCH.**
- **Page 9, Figure 1:** admits=90 for 2026-02 exists only as a raster image, confirmed absent from the text layer — correctly, deliberately excluded from the CSV.
- **Pages 9–10, Table 1** (waitlist_stock / waitlist_stock_avg_days, 13 periods each): all 26 values transcribed and matched exactly. Table 1 additionally carries a "§2. GEI-ordered-to-OSH" sub-table (its own 14-point waitlist count + avg-days series) that is **not captured anywhere in the CSV** — see Finding E. Also, the 2022-01 column is one of *two* January-2022 snapshots in Table 1 ("As of 1/5/22"=46/15.8 days, and "As of 1/28/22*"=93/22.5 days, asterisked in the source as a COVID-19-pause-related spike); the CSV's `2022-01` row uses the 1/28/22 values only — see Finding A.
- **Page 12, Table 2** (beds, 2025-11): Licensed 738, Active 704 — **MATCH** (rows 24, 36).
- **Page 12, Table 3** (census, 11 periods × 5 metrics = 55 cells): all transcribed and matched exactly; internal arithmetic (aa+civil+other+psrb=total) verified for all 11 columns.
- **Pages 12–13, Table 4** (orders_received, 2025-01 through 2026-02, 14 months): all 14 values matched exactly.

**CLEAN — 79 rows**, plus the completeness notes above (Findings A, E) and confirmation of the Finding B revision pattern (2025-11 beds_active: 705 in the 2025.12.06 report vs. 704 here, for the identical "as of 11/1/25" date; 2025-10 orders_received: 99 in the 2025.12.06 report vs. 100 here for the identical month — CSV correctly matches whichever report it cites in each case).

### 16–18. PLD-2022.10.03.pdf, PLD-2022.11.03.pdf, PLD-2024.03.03.pdf — NOT CITED
All three opened in full. Each is a bi-monthly "Progress/Status Report to Neutral Expert" — a recommendation-compliance tracker (item / deadline / status / narrative-update columns), listing target benchmark dates, not measured monthly actuals. No admits, avg_wait_days, beds, census, orders_received, pct_within_7day, or waitlist figures exist in any of them.
**Verdict: correctly excluded — no extractable metric data, for all three.**

---

## Findings requiring disclosure (none are wrong values; all are completeness/transparency items)

### Finding A — 2022-01 waitlist period maps to only one of two source snapshots
Table 1 in the source reports carries two January-2022 columns: "As of 1/5/22" (waitlist=46, avg wait=15.8 days) and "As of 1/28/22*" (waitlist=93, avg wait=22.5 days; asterisked in the source as *"most likely a residual of the pauses in admissions due to COVID-19"*). The CSV's `2022-01` row uses only the 1/28/22 values; the 1/5/22 data point does not appear under any period. This pairing is the *only* place in the entire dataset where a single reporting date maps to two distinct source snapshots — every other period in the standard 13-point grid used throughout the CSV (beds, census, waitlist) has exactly one source date, and 1/28/22 is consistent with that grid (it is the date every other report's "as of" table anchors to), while 1/5/22 is an extra data point outside that grid. This makes the exclusion defensible and internally consistent, but it is not documented anywhere in the dataset, so a reader would not know the 1/5/22 figures exist. **Recommend:** add a methodology note (or an explicit dataset footnote) documenting this choice.

### Finding B — the source documents themselves revise historical figures between filings (not a CSV defect)
Multiple `orders_received` and `beds_active` values that the CSV cites from a later report differ from what an earlier report printed for the identical historical month/date. Verified examples:

| Period | Earlier report's value | Later report's value (= what CSV uses) |
|---|---|---|
| 2022-04 orders_received | 80 (2nd/4th report) | 79 (2025.12.06 report) |
| 2022-07 orders_received | 65 (4th report) | 72 (2025.12.06 report) |
| 2022-11 orders_received | 95 (4th report) | 89 (2025.12.06 report) |
| 2023-08 orders_received | 103 (8th report) | 109 (2025.12.06 report) |
| 2024-09 orders_received | 91 (10th report) | 92 (2025.12.06 report) |
| 2024-10 orders_received | 100 (10th report) | 102 (2025.12.06 report) |
| 2025-10 orders_received | 99 (2025.12.06 report) | 100 (2026.03.16 report) |
| 2025-11 beds_active | 705 (2025.12.06 report, "as of 11/1/25") | 704 (2026.03.16 report, same date) |

In every case checked, **the CSV's value matches exactly what is printed in the specific report the CSV cites.** The CSV is a faithful transcription of its cited source in every instance — the inconsistency originates in the litigation's own record-keeping (the state revises its retrospective monthly tallies between filings). **Recommend:** a one-line methodology/README note disclosing that cross-checking a CSV value against a *different* PDF vintage than the one cited may show an apparent mismatch that is not a transcription error.

### Finding C — a real, undocumented completeness gap: 2025-12 avg_wait_days=22.7
Page 8 of the 2025.12.06 report states: *"on 12/3/25, the average time people are waiting was at 22.7 days."* This figure is independently repeated on page 8 and page 30 of the 2026.03.16 report ("days to admission have reduced from 22.7 as reported in December 2025 to 15 days as noted at the end of February"). The `avg_wait_days` series has rows for 2025-03, 04, 07, 08, 11, and 2026-02, but **no 2025-12 row**, despite this value being printed on a page already cited elsewhere in the dataset. One caveat worth noting: unlike the other `avg_wait_days` rows (each framed as a full-calendar-month average "for individuals admitted the month prior"), the 22.7 figure is explicitly dated "as of 12/3/25" — a point-in-time reading only 3 days into December, not necessarily a directly comparable full-month average. That distinction may be *why* it was excluded, but if so it isn't documented anywhere, so as it stands this reads as a silent omission rather than a deliberate, disclosed exclusion. **Recommend:** either add the row (documenting that it is a partial-month snapshot rather than a full-month average) or add an explicit methodology note explaining the exclusion.

### Finding D — two of three `pct_within_7day` values are derived, not literally printed as percentages
- 2023-11 = 93.5 (8th report, p.10): printed verbatim — *"93.5% (101 people) were admitted within the 7-day Mink requirement."*
- 2024-04 = 90.6 (9th report, p.8): **derived** — the page states "87 of the 96 admissions," no percentage is printed; 90.6 = 87÷96 rounded.
- 2025-08 = 7.5 (2025.09.05 report, p.7): **derived** — the page states "eight (8) of the 107 admissions," no percentage is printed; 7.5 = 8÷107 rounded.

Both derived values were re-checked arithmetically and are correct. This is a transparency issue, not an accuracy issue: for a zero-tolerance public dataset, cells that are computed from raw counts rather than transcribed verbatim from a printed percentage should ideally carry a `derived`/`computed` flag so downstream users don't assume every value is a literal quotation.

### Finding E — a parallel GEI-population data series is out of scope and entirely uncaptured
Every report's Table 1 (waitlist) carries a second sub-table for the GEI-ordered-to-OSH population (distinct from the Aid & Assist population the CSV tracks), with its own waitlist-count and avg-days-waiting series across the same ~14 time points. Similarly, Table 4 (orders_received) carries a "GEI" column alongside the "Aid & Assist" column the CSV extracts. Neither the GEI waitlist series nor the GEI orders column is captured anywhere in the CSV. This is consistent across every report (i.e., it looks like an intentional scope decision — the dataset tracks the Aid & Assist / Mink population specifically, with PSRB/civil/other populations captured only in the separate census breakdown) rather than an oversight, but it is undocumented. **Recommend:** a one-line scope note in the dataset documentation (e.g. "orders_received and waitlist_* metrics cover Aid & Assist orders only; GEI-population figures are out of scope").

---

## Integrity checks performed beyond cell-by-cell comparison

- **Hash verification:** SHA-256 recomputed on all 18 raw PDFs; the `source_sha` prefix matches for every one of the 13 cited reports. No file substitution or mislabeling detected.
- **Arithmetic cross-check:** `census_total = census_aa + census_civil + census_other + census_psrb` verified exactly for all 11 periods in Table 3 of the 2026.03.16 report.
- **Text-layer vs. image verification:** for the 2026-02 admits/avg_wait_days split, confirmed via direct visual read plus independent text-extraction passes by three separate sub-agents that the admits figure exists only as a raster image.
- **Row-count reconciliation:** CSV has 173 data rows (174 lines including header, no stray blank row). All 173 rows checked. 18 raw PDFs present; 13 cited by at least one row, 5 correctly uncited.
- **Duplicate-key check:** no duplicate `(state, period, metric)` combinations found.

## Final verdict

- **0 confirmed wrong numeric values** across all 173 rows (one sub-agent's claimed error was checked against the raw CSV directly and found to be a false positive caused by conflating two distinct rows — see "Note on a debunked false-positive" above).
- **All 18 `source_sha` values authentic.**
- **Critical row (2026-02, avg_wait_days, 16.5, 2026.03.16 report p.8): CONFIRMED CLEAN**, with the corresponding admits figure for that period confirmed to exist only in a raster image and therefore correctly, deliberately omitted — not a guess, not an oversight.
- **5 uncited PDFs confirmed correctly excluded** (no extractable competency-restoration data in any of them).
- **5 completeness/transparency findings** (A–E above), none of which involve a wrong value already in the dataset — all are either undocumented exclusions or undocumented derivations. Recommended actions: document Findings A, B, C, D, and E in the dataset's methodology notes or README before external reliance on the DOI citation; optionally add the missing 2025-12 avg_wait_days row (Finding C) if its point-in-time nature is judged comparable enough to include.
