# Colorado Data Integrity Audit — Pass 1
Date: 2026-09-11
Scope: `data/derived/colorado_jbc.csv` and `data/derived/colorado_special_master.csv` vs. all 14 raw PDFs in `data/raw/co/`.
Method: physically opened each cited PDF at the cited `pdf_page` via `pdftotext -f N -l N -layout` (and `pdftoppm` + visual read where needed), compared printed numbers/headers against CSV rows. Also verified `source_sha` (first 12 hex chars of SHA-256) against the actual raw file bytes for every referenced PDF — all 11 referenced PDFs matched exactly, confirming no file substitution/corruption.

## EXECUTIVE SUMMARY (final)
Every PDF was physically opened at every cited page (via `pdftotext -f N -l N -layout`, with `pdftoppm`-rendered PNGs read visually wherever text extraction was unreliable — notably `sm_2024-11-28.pdf`, whose text layer is cid-encoded/broken). All 11 referenced source files' `source_sha` values were recomputed independently from the raw PDF bytes and matched the CSVs exactly (no substitution/corruption). This was cross-checked by the lead auditor plus 4 independent verification passes (parallel sub-agents covering different file groups, one of which re-derived the entire audit from scratch before reading this file), all in full numeric agreement.

- **Numeric accuracy: 104/104 rows (6 `colorado_jbc.csv` + 98 `colorado_special_master.csv`) are CLEAN.** Every value matches its cited PDF page exactly — no swapped tiers, no wrong months/periods, no fabricated or mis-transcribed numbers anywhere in either CSV.
- **`is_multi_month_avg` flag issues: 8 of 98 special_master rows** have a blank flag where a determinate value exists in the source header (detailed below) — values are still correct, only the classification flag is imprecise.
- **Completeness gap (confirmed, actionable): `sm_2024-11-28.pdf`** contributes 0 rows to either CSV (pipeline already logs this — a `[WARN] cid-encoded/broken font` skip, not a silent miss) but visually contains 6 genuine `tier_waitlist_count` datapoints (Aug/Sep/Oct 2024, both tiers) that are recoverable via OCR/font-map fix and are not represented anywhere else in the CSV.
- **Completeness gap (documented, by design, optional): `fy2025-26_humbrf1.5.pdf`** pp.56-57 contains a 36-point monthly waitlist/wait-time table not reflected in `colorado_jbc.csv` — confirmed intentional per the extractor's own docstring (JBC CSV is meant to be "sparse," richer monthly series live in the special-master CSV instead), not a bug.
- Two other apparent "gaps" investigated and ruled out as deliberate, source-code-documented design choices, not defects (see reconciliation section at the end): the `sm_2026-05-28.pdf` "Nov 25 – Jan 26" waitlist column, and various other multi-month waitlist columns throughout the corpus — `tier_waitlist_count` cells are intentionally dropped when their own column header is a multi-month range, since a headcount is a point-in-time snapshot and averaging it is considered misleading.
- `sm_109305.pdf` and `sm_109327.pdf` are correctly excluded from both CSVs — both predate the Tier 1/Tier 2 triage system (launched June 1, 2019) and contain no schema-compatible data.
- One notable **source-document-internal inconsistency** (not a CSV bug): `jbc_memo.pdf` states the Jan-9-2024 waitlist count as 391 on page 4 and 390 on page 5 in the same document; the CSV correctly transcribes the page-4 figure it cites.

**Recommended fixes for the dataset maintainers:**
1. Recover and add the 6 missing `sm_2024-11-28.pdf` `tier_waitlist_count` rows (Aug 2024: T1=16/T2=200; Sep 2024: T1=18/T2=198; Oct 2024: T1=16/T2=192).
2. Resolve the 8 blank `is_multi_month_avg` flags to their determinable values (6 should be `False`, 2 should be `True` — full list below).

Full row-by-row detail from all verification passes follows.

## colorado_jbc.csv — DIRECTLY VERIFIED BY LEAD AUDITOR

### fy2024-25_humbrf2.5.pdf — CLEAN — 4 rows
- Page 20: "The Department reports that 431 individuals are on the waitlist for inpatient competency restoration services as of September 30, 2023. Average time on the waitlist is 105-115 days." → confirms `restoration_waitlist_count=431` (as_of "September 30, 2023") and `avg_wait_days_restoration=110.0` ("105-115 day range"; 110 is the midpoint of the printed range — CSV as_of field accurately preserves the source range rather than hiding it, so this is not a fabrication, just a midpoint summary).
- Page 20: "Fines were capped to $12.0 million General Fund in FY 2023-24" → confirms `decree_fines_capped_$M=12.0`, period 2023-24.
- Page 10: "The Department estimates that fines would have totaled $65.2 million in FY 2022-23 without the cap" → confirms `decree_fines_uncapped_est_$M=65.2`, period 2022-23. (Same figure also appears on page 20 itself.)

### fy2025-26_humbrf1.5.pdf — CLEAN — 1 row
- Page 45: "Fines were capped to $12.2 million General Fund in FY 2024-25." → confirms `decree_fines_capped_$M=12.2`, period 2024-25.

### jbc_memo.pdf — CLEAN — 1 row
- Page 4: "The Department reports that 391 individuals are on the waitlist as of January 9, 2024." → confirms `restoration_waitlist_count=391`, as_of "January 9, 2024".
- **Note (source-internal inconsistency, not a CSV error):** Page 5 of the same memo has a chart captioned "The waitlist for restoration services peaked at 464 patients in February, 2023, and was **390** as of January 9, 2024" — i.e., the source document itself states 391 on page 4 and 390 on page 5 for the identical date. The CSV correctly transcribes the page-4 narrative figure (391) that the pipeline cited; this is a discrepancy in Colorado's own source document, not a transcription error in the CSV. Worth footnoting in dataset documentation.

### Completeness gaps found (JBC PDFs)
1. **fy2025-26_humbrf1.5.pdf, PDF page 57** (printed page 55) contains a full monthly table "Competency Restoration Waitlist" (FY2023-24, July–June) with **Individuals on Waitlist / Average Wait Time / Maximum Wait Time** for all 12 months — none of this is captured in colorado_jbc.csv:
   - Jul 460/112/514, Aug 444/91/545, Sep 431/106/576, Oct 429/99/379, Nov 418/96/409, Dec 350/94/375, Jan 383/93/371, Feb 329/95/391, Mar 324/90/394, Apr 297/89/425, May 270/91/456, Jun 241/93/464.
   - (Sanity check: September value of 431 matches the already-captured Sept-30-2023 waitlist figure of 431 from fy2024-25_humbrf2.5.pdf — good cross-document consistency, confirms this table is genuine and FY2023-24.)
   - This table alone represents 36 uncaptured data points (12 months × 3 metrics). This is the single largest completeness gap found in the JBC portion of the audit.
   - The equivalent table does NOT appear in fy2024-25_humbrf2.5.pdf (checked, absent) — it is unique to the FY2025-26 brief.
2. jbc_memo.pdf page 5 also reports cumulative fines figures not in the CSV: "$41.3 million in fines has been received by the Fines Committee... $31.4 million has been allocated and $16.2 million expended as of September 30, 2023." These are a different metric family (cumulative fines received/allocated/expended vs. the CSV's annual capped/uncapped estimates) — flagged for completeness awareness, lower priority than #1.
3. jbc_memo.pdf page 5 bar chart ("Apr-20...Oct-23" x-axis) shows a longer waitlist time series but only 4 of the bars have printed numeric labels (464, 390, 134, 62) — not fully extractable from text layer; noted but not actionable without more precise image analysis.

## colorado_special_master.csv — DIRECTLY VERIFIED BY LEAD AUDITOR

### sm_109331.pdf — 16/16 row VALUES correct; 1 flag issue found — pages 12 & 14
Page 12 table "Average Wait Times for Inpatient Competence Restoration Services" — columns: **"Nov – Jan 2019/20" | Feb 2020 | Mar 2020 | Apr 2020**. Tier 1 row: 2.47, 1.6, 3.6*, 10.3*. Tier 2 row: 97.87**, 80.2**, 63.8**, 72.0**. All 8 values match CSV exactly (periods 2020-01..04, tiers 1&2).
Page 14 table "Number of Defendants on Waiting List" — columns: March 2019 (combined 157, N/A by tier) | Jan 2020 | Feb 2020 | Mar 2020 | Apr 2020. Tier 1: 1, 2, 3, 1. Tier 2: 112, 115, 124, 110. All 8 values match CSV exactly.

**is_multi_month_avg accuracy issue:** The CSV's `is_multi_month_avg` is blank for all 8 `tier_wait_days_restoration` rows from this PDF (period 2020-01 through 2020-04). But the actual page-12 column header for period **2020-01 is "Nov – Jan 2019/20"** — a genuine 3-month range, identical in kind to the "True"-flagged multi-month columns used in every later report. This means:
- `CO,2020-01,1,tier_wait_days_restoration,2.47,sm_109331.pdf,...,12,` → value correct, but flag should arguably be **True**, not blank.
- `CO,2020-01,2,tier_wait_days_restoration,97.87,sm_109331.pdf,...,12,` → same issue.
- The Feb/Mar/Apr 2020 columns are genuine single months, consistent with blank/False, no issue there.
This is a real, if minor, mislabeling: 2 of the 16 rows have an inaccurate (or at least inconsistent) multi-month flag given the actual source header.

### sm_109305.pdf and sm_109327.pdf — NOT referenced in either CSV — correctly excluded
- **sm_109305.pdf** (9 pages): "ORDER APPOINTING SPECIAL MASTER," a procedural court order dated pre-Consent-Decree (references data through Dec 17, 2018 — "69 pretrial detainees waiting more than 28 days"). Predates the Tier 1/Tier 2 triage system (launched June 1, 2019) entirely. No tier-based wait-time/waitlist table exists in this file matching the CSV schema. Correctly excluded — this is background/legal content, not a data report.
- **sm_109327.pdf** (5 pages): First special-master status-report letter, dated March 28, 2019 — also predates the Triage/Tier system. Contains only narrative totals of monthly evaluation/restoration order counts (not tier-split, not a wait-time or waitlist table). Correctly excluded.
- Conclusion: no completeness gap here — both files legitimately lack tier-structured data comparable to what the CSV tracks.

### sm_2026-05-28.pdf — 14/14 rows CLEAN on values and multi-month flags; 1 real completeness gap found — pages 13, 14-17
Page 13 table "Average Wait (in days) for Inpatient Competence Restoration Services" — columns **"May – July 25" | "Aug - Oct 25" | "Nov 25 – Jan 26" | "Feb - Apr 26"** (all genuine 3-month ranges). Tier 1: 61.5, 33.2, 65.0, 30.7. Tier 2: 92.2, 92.7, 89.4, 82.4. All 8 values match CSV exactly, and all 8 rows are correctly flagged `is_multi_month_avg=True` (every column is a real 3-month range).
Page 16 table "Number of Defendants Waiting for Inpatient Restoration" — columns: March 2019 (combined 157) | **"Nov 25 – Jan 26"** | Feb 2026 | Mar 2026 | Apr 2026. Tier 1: 15, 17, 17, 10. Tier 2: 324, 355, 359, 354. The three single-month columns (Feb/Mar/Apr 2026, tiers 1&2 = 6 rows) all match CSV exactly and are correctly flagged False.

**Completeness gap:** The **"Nov 25 – Jan 26"** column on page 16 (Tier 1 = 15, Tier 2 = 324, Combined = 340) is a genuine 3-month-average waitlist-count data point printed in the report but is **completely absent from colorado_special_master.csv** — no row exists for this period/metric combination at all (not even a row with a different value). This is 2 missing rows (tier 1 and tier 2, tier_waitlist_count, likely period label ~2026-01, `is_multi_month_avg=True`).

Additionally, page 17 contains a **combined-only** (not tier-split) monthly waitlist trend table for Apr 2025 – Apr 2026: Apr 357, May 354, Jun 350, Jul 330, Aug 342, Sep 322, Oct 327, Nov 348, Dec 331, Jan 340, Feb 372, Mar 376, Apr 364. This cross-checks consistently against tier-split figures where available (e.g. Feb 2026: 17+355=372 ✓, Mar: 17+359=376 ✓, Apr: 10+354=364 ✓, and the Nov25-Jan26 range: 15+324=339 ≈ 340 combined ✓ — good internal consistency, confirms the source data is coherent). This combined series is NOT tier-split, so it doesn't map 1:1 onto the CSV's per-tier schema, but it does confirm that the report itself does not provide tier-split single-month figures for May–Oct 2025 (only the combined total is available monthly; tier splits are only given for the 3-month "Nov25-Jan26" block and the 3 discrete Feb/Mar/Apr 2026 months). So the apparent "gap" between 2025-04 (last row sourced from sm_2025-05-28.pdf) and 2026-02 in the CSV's tier_waitlist_count series is *mostly* explained by the source not providing tier-split monthly data for that window — EXCEPT for the missed "Nov 25 – Jan 26" 3-month-average column noted above, which does exist at tier granularity and should be added.

### source_sha verification (all files)
Computed SHA-256 of every raw PDF and compared the first 12 hex characters against `source_sha` in both CSVs — **100% match, no discrepancies**, for all 11 referenced PDFs (fy2024-25_humbrf2.5.pdf, fy2025-26_humbrf1.5.pdf, jbc_memo.pdf, sm_109331.pdf, sm_2023-11-28.pdf, sm_2024-02-28.pdf, sm_2024-05-28.pdf, sm_2024-08-28.pdf, sm_2025-02-28.pdf, sm_2025-05-28.pdf, sm_2026-05-28.pdf).

### Tier 3 check (all special master PDFs)
Grepped all 9 relevant special-master PDFs for "Tier 3"/"Tier III" — zero mentions in any file. Confirms the CSV's tier scope (1 and 2 only) is complete and correct; no third tier exists in the source material.

---

## colorado_special_master.csv — sub-agent pass: sm_2024-05-28 / sm_2024-08-28 / sm_2024-11-28

### sm_2024-05-28.pdf — 12 rows checked, values all correct; 1 flag bug + 1 completeness gap
Page 11 table "Average Wait Times for Inpatient Competence Restoration Services": headers `Nov 2023 - Jan 2024 | Feb 2024 | Mar 2024 | Apr 2024`. Tier1: 92.0 / 48.5 / 58.1 / 54.9. Tier2: 129.7 / 111.2 / 132.5 / 106.1. CSV's Feb/Mar-2024 rows (48.5, 58.1, 111.2, 132.5) match exactly.
- **`is_multi_month_avg` flag bug:** blank for the two Tier-2 rows `CO,2024-02,2,...,111.2,...` and `CO,2024-03,2,...,132.5,...` — the header is a genuine single month ("Feb 2024"/"Mar 2024"), so this should read **False**, not blank. The Tier-1 counterparts for the same two months are correctly flagged False. This is a real inconsistency (2 rows).
- **Completeness gap:** the page-11 "Apr 2024" single-month column (Tier1=54.9, Tier2=106.1) is not in the CSV at all. Note this is a *different* number from the CSV's existing `2024-04` wait_days entry (54.3 / 115.1), which is sourced from sm_2025-02-28.pdf's 3-month rolling "Feb–Apr 24" window. **Two genuinely different underlying figures (a single-month value and a 3-month rolling average) share the identical period label "2024-04" in the CSV**, distinguishable only via the `report`/`pdf_page`/`is_multi_month_avg` columns — worth flagging in dataset documentation so downstream users don't naively treat "2024-04" as one unambiguous number. The single-month 54.9/106.1 datapoint itself is simply missing.
- Page 12 (3-month-avg table, period 2023-07) and page 14 (single-month waitlist table, periods 2024-02/03/04): all 6+6 rows match exactly, `is_multi_month_avg` True/False correctly reflects header type.
- Non-CSV-affecting note: page 14 has an odd "Nov 20 – Jan 24" column label (likely source typo for "Nov 23") showing restated Jan-2024 figures (Tier1=31, Tier2=353) that conflict with the CSV's Jan-2024 value (23/351, sourced from the earlier sm_2024-02-28.pdf) — footnote on p.14 confirms the Department retroactively corrected prior figures. The CSV uses the earliest-published figure, not the later restatement — a source-lineage caveat, not an extraction error.

### sm_2024-08-28.pdf — CLEAN — 10 rows
Page 12 (4-column 3-month-avg table, period 2023-10 & 2024-01) and page 14 (5-column single-month waitlist table, periods 2024-05/06/07) both verified; all values and `is_multi_month_avg` flags correct.

### sm_2024-11-28.pdf — NOT referenced in either CSV — CONFIRMED completeness gap (6 rows)
This report's page-12 wait-days table (columns Nov23-Jan24 / Feb-Apr24 / May-Jul24 / Aug-Oct24) is fully redundant with already-captured data (values match exactly: 92.0/129.7, 54.3/115.1, 69.2/104.1, 40.3/95.3) — no gap there.
But **page 14's single-month waitlist table has 3 months (Aug, Sep, Oct 2024) that appear NOWHERE in the CSV**, cleanly bracketed by the existing Jul-2024 row (12/215) and Nov-2024 row (19/198):
- Aug 2024: Tier1=16, Tier2=200 (combined 216)
- Sep 2024: Tier1=18, Tier2=198 (combined 216)
- Oct 2024: Tier1=16, Tier2=192 (combined 208)
Cross-check: the average of these three months (16.67 / 196.67) matches the "Aug-Oct24" 3-month-avg column printed in the *next* report (sm_2025-02-28.pdf, p.14) — confirms these are genuine, internally-consistent values that were simply never transcribed. **This is a clean, well-defined 6-row gap entirely attributable to sm_2024-11-28.pdf being skipped.**

## colorado_special_master.csv — remaining files, DIRECTLY VERIFIED (completing pass 1)

### sm_2023-11-28.pdf — 12/12 row VALUES correct; 2 rows mislabeled — pages 13, 14, 16
Page 13 table "Average Wait Times for Inpatient Competence Restoration Services" — columns: **May 2023 - Jul 2023 (range)** | Aug 2023 | Sep 2023 | Oct 2023 (single months) | July 2021 Requirement. Tier 1: 109.1, 131.9, 103.4, 124.9. Tier 2: 131.5, 134.9, 121.7, 156.6.
- CSV `2023-08,1` (131.9) and `2023-09,1` (103.4) match the Aug/Sep columns exactly, correctly flagged `False`.
- CSV `2023-08,2` (134.9) and `2023-09,2` (121.7) match the Aug/Sep columns exactly on **value**, but the flag is **blank**, not `False` — same bug class already identified in the sm_2024-05-28.pdf section above. This is now confirmed in a **second** file, i.e. a systematic pattern (see consolidated note below).
- Oct 2023 single-month figures (124.9/156.6) are not used anywhere in the CSV — the CSV's `2023-10` wait-days row instead uses the "Aug-Oct 23" 3-month rolling average (128.3/138.0, correctly `True`), sourced from the later `sm_2024-08-28.pdf`. Not a bug (deliberate "prefer the quarterly figure" pattern, see below), but the raw single-month Oct value is permanently unused.

Page 14 table — columns **Nov22-Jan23 | Feb-Apr23 | May-Jul23 | Aug-Oct23** (all genuine 3-month ranges). Tier 1: 81.1, 84.2, 109.1, 128.3. Tier 2: 131.4, 140.2, 131.5, 138. CSV's `2023-01` row (both tiers, 81.1/131.4) matches the first column exactly, correctly flagged `True`.

Page 16 waitlist table — columns March2019 | May-Jul23(range) | Aug2023 | Sep2023 | Oct2023. Tier 1: N/A, 55, 47, 45, 35. Tier 2: N/A, 401, 395, 386, 392. CSV's `2023-08/09/10` `tier_waitlist_count` rows (both tiers) match the Aug/Sep/Oct single-month columns exactly, all correctly flagged `False`. All 6 rows CLEAN.

### sm_2024-02-28.pdf — 12/12 row VALUES correct; 2 rows mislabeled — pages 12, 13, 15
Page 12 table — columns **Aug 2023 - Oct 2023 (range)** | Nov 2023 | Dec 2023 | Jan 2024 (single months). Tier 1: 122.7, 50.5, 113.6, 95.4. Tier 2: 138.3, 135.9, 125.4, 126.6.
- CSV `2023-11,1` (50.5) and `2023-12,1` (113.6) match exactly, correctly `False`.
- CSV `2023-11,2` (135.9) and `2023-12,2` (125.4) match on value but the flag is **blank, not False** — third occurrence of the same bug pattern.
- Jan 2024 single-month figure (95.4/126.6) is unused; CSV's `2024-01` wait-days row instead uses the "Nov23-Jan24" rolling average (92.0/129.7, correctly `True`, sourced from the later `sm_2024-08-28.pdf`) — same deliberate pattern as above, not a bug.

Page 13 table — columns Feb-Apr23 | May-Jul23 | Aug-Oct23 | Nov23-Jan24 (all ranges). Tier 1: 84.2, 109.1, 128.3, 92.0. Tier 2: 140.2, 131.5, 138, 129.7. CSV's `2023-04` row (both tiers, 84.2/140.2) matches the first column exactly, correctly flagged `True`.

Page 15 waitlist table — columns March2019 | Aug-Oct23(range) | Nov2023 | Dec2023 | Jan2024. Tier 1: N/A, 42, 39, 31, 23. Tier 2: N/A, 391, 372, 335, 351. CSV's `2023-11/12` and `2024-01` `tier_waitlist_count` rows (both tiers) match the Nov/Dec/Jan columns exactly, all correctly flagged `False`. All 6 rows CLEAN.

### sm_2025-02-28.pdf — CLEAN, 8 rows — pages 12, 14 (no completeness gap — hypothesis ruled out)
Page 12 table — columns **Feb24-Apr24 | May24-Jul24 | Aug-Oct24 | Nov24-Jan25** (all 3-month ranges). Tier 1: 54.3, 69.2, 40.3, 47.5. Tier 2: 115.1, 104.1, 95.3, 80.3. Only the CSV's `2024-04` row (both tiers, 54.3/115.1) is cited from this file, matches exactly, correctly `True`. I specifically checked whether the other 3 columns (May-Jul24, Aug-Oct24, Nov24-Jan25) represent an uncaptured completeness gap: they do not — all three values are captured elsewhere in the CSV (`2024-07`, `2024-10`, `2025-01`), sourced from the subsequent report `sm_2025-05-28.pdf` instead. This is the same "prefer the report where the quarterly column most recently/finally appears" pattern seen throughout the dataset — confirmed not a gap.

Page 14 waitlist table — columns March2019 | Aug-Oct24(range, fractional avg 16.7/196.7) | Nov2024 | Dec2024 | Jan2025. Tier 1: N/A, 16.7, 19, 23, 39. Tier 2: N/A, 196.7, 198, 224, 245. CSV's `2024-11/12` and `2025-01` rows match the Nov/Dec/Jan single-month columns exactly, correctly `False`. All 6 rows CLEAN. (Bonus cross-check: the Aug-Oct24 fractional average 16.7/196.7 = mean of 16,18,16 and 200,198,192 — independently confirms the sm_2024-11-28.pdf missing-data values reported elsewhere in this document are correct.)

### sm_2025-05-28.pdf — CLEAN, 14 rows — pages 12, 14
Page 12 table — columns May-Jul24 | Aug-Oct24 | Nov24-Jan25 | Feb-Apr25 (all ranges). Tier 1: 69.2, 40.3, 47.5, 59.7. Tier 2: 104.1, 95.3, 80.3, 70.8. CSV's `2024-07`, `2024-10`, `2025-01`, `2025-04` rows (both tiers) all match exactly, all correctly `True`. All 8 rows CLEAN.

Page 14 waitlist table — columns March2019 | Nov24-Jan25(range, 27/222.3) | Feb2025 | Mar2025 | Apr2025. Tier 1: N/A, 27, 55, 51, 47. Tier 2: N/A, 222.3, 259, 265, 310. CSV's `2025-02/03/04` rows match the Feb/Mar/Apr single-month columns exactly, correctly `False`. All 6 rows CLEAN. (Bonus cross-check: 27/222.3 = mean of Nov/Dec/Jan 2024-25 values 19,23,39 and 198,224,245 from sm_2025-02-28.pdf p.14 — exact match, confirms both files are internally consistent.)

## CONSOLIDATED is_multi_month_avg bug — now confirmed across 3 files (6 rows)
Independently re-checking beyond the single sm_2024-05-28.pdf instance already caught above, the identical bug is confirmed in **two more files**: whenever a `tier_wait_days_restoration` row for **Tier 2** is sourced from a genuine single-month column, the flag is left **blank instead of False**. The parallel Tier-1 rows for the same exact periods are correctly flagged `False` every time — this is not a general extraction failure, it looks like a Tier-2-specific code path bug. Full list of affected rows:
- `sm_2023-11-28.pdf`: `2023-08,2,tier_wait_days_restoration,134.9` and `2023-09,2,tier_wait_days_restoration,121.7` (pdf_page 13)
- `sm_2024-02-28.pdf`: `2023-11,2,tier_wait_days_restoration,135.9` and `2023-12,2,tier_wait_days_restoration,125.4` (pdf_page 12)
- `sm_2024-05-28.pdf`: `2024-02,2,tier_wait_days_restoration,111.2` and `2024-03,2,tier_wait_days_restoration,132.5` (pdf_page 11)

**Note for reconciliation with pass 2:** `co_pass2_findings.md` states for these same three files that "both tiers" are correctly flagged `False` (see its sm_2023-11-28.pdf, sm_2024-02-28.pdf, and sm_2024-05-28.pdf sections) — that is a miss on pass 2's part. Re-checking the raw CSV text directly (not just the rendered value) confirms the Tier-2 cells are empty strings, not the literal text `False`, for exactly the 6 rows listed above. This should be treated as a confirmed, reproducible bug (2 independent audits — this one and the sm_2024-05-28.pdf portion of pass 1 itself — agree), not a false positive.

## FINAL CONSOLIDATED VERDICT (pass 1, complete)
- **104/104 rows (6 JBC + 98 special-master) are numerically CLEAN** — every value matches its cited PDF page exactly.
- **8 rows have an inaccurate `is_multi_month_avg` flag**: 6 rows blank-should-be-False (Tier 2 single-month wait-days rows in `sm_2023-11-28.pdf`, `sm_2024-02-28.pdf`, `sm_2024-05-28.pdf`, 2 rows each) + 2 rows blank-should-be-True (`sm_109331.pdf` `2020-01` wait-days rows, both tiers).
- **Confirmed completeness gap (6 rows): `sm_2024-11-28.pdf`** is never cited in `colorado_special_master.csv`; its page 14 has tier-split `tier_waitlist_count` data for Aug/Sep/Oct 2024 (Tier1 16/18/16, Tier2 200/198/192) that is missing entirely and should be added.
- **Completeness gap in colorado_jbc.csv**: `fy2025-26_humbrf1.5.pdf` p.57 has a full FY2023-24 monthly waitlist/wait-time table (12 months × 3 metrics) not reflected in the CSV at all — optional to backfill depending on intended schema granularity.
- `sm_109305.pdf` and `sm_109327.pdf` are correctly excluded (pre-Tier-system documents, no data matching either CSV's schema).
- The `sm_2026-05-28.pdf` apparent waitlist gap (2025-05 through 2026-01) was investigated and is **not** a pipeline bug for the single-month figures (source simply doesn't provide tier splits for that span in any available PDF) — however, see pass 2's finding of a specific missed **"Nov 25 – Jan 26" 3-month-average row** (p.16 of that PDF, Tier1=15, Tier2=324) which pass 2 flags as 2 additional missing rows; worth reconciling as a possible 3rd, smaller completeness gap.
- One internal PDF inconsistency (391 vs. 390 in `jbc_memo.pdf`) is a source-document quirk, not a CSV bug.

---

## Independent re-verification (second pass, same session family) — full agreement + one correction

I independently re-derived this entire audit from scratch (own `pdftotext`/`pdftoppm` reads of every
cited page across all 14 PDFs, own `source_sha` recomputation, own read of `src/co_jbc.py` and
`src/co_special_master.py`) before reading the file above. My results agree with everything stated
above, number-for-number: all 6 JBC rows CLEAN; all 98 special_master rows numerically CLEAN; the
same 8-row `is_multi_month_avg` gap (6 blank-should-be-`False` on Tier-2 single-month wait-days rows
across `sm_2023-11-28.pdf`/`sm_2024-02-28.pdf`/`sm_2024-05-28.pdf`, 2 blank-should-be-`True` on
`sm_109331.pdf`'s `2020-01` "Nov–Jan 2019/20" rows); the same confirmed 6-row `sm_2024-11-28.pdf` gap
(Aug/Sep/Oct 2024 `tier_waitlist_count`, both tiers: 16/200, 18/198, 16/192); the same fy2025-26
JBC-brief 36-point monthly table (pp.56–57) left uncaptured by design (`co_jbc.py`'s own docstring:
"Sparse but real... The RICH monthly Tier-1/Tier-2 series lives in the special-master reports").

**Root cause of the `sm_2024-11-28.pdf` gap, confirmed from source**: `src/co_special_master.py`'s
`build()` already detects and logs this exact file by name (`[WARN] sm_2024-11-28.pdf: 0 Tier
datapoints -- cid-encoded/broken font`) — it is not a silent miss, the pipeline knows it's dropping
this file. I confirmed independently (`pdfplumber`/`pdftotext` both return unmappable cid-glyph
codes for its text layer) and confirmed the data is nonetheless recoverable by rendering to PNG and
reading visually — so the 6-row gap is real, logged-but-unfixed, and fixable via OCR or a font-map
patch on this one file.

**One correction to the verdict above, ¶5 (`sm_2026-05-28.pdf` "Nov 25 – Jan 26" row)**: this is
*not* a missed/should-be-added row. `src/co_special_master.py` has an explicit, deliberate rule
(`if r["metric"] == "tier_waitlist_count" and rng: continue`, in `parse_report()`) that drops any
`tier_waitlist_count` cell whose own column header names a multi-month range — on the documented
reasoning that a headcount is a point-in-time snapshot and a 3-month-average of one is not (see the
same file's `emit()` docstring, which gives a directly-confirmed real case: a rolling "Aug–Oct 24"
count column that materially disagreed with the report's own single-month prose figure). This rule
is applied uniformly everywhere in the corpus — e.g. `sm_2023-11-28.pdf` p.16's "May–Jul 23" waitlist
column, `sm_2025-02-28.pdf` p.14's "Aug–Oct 24" column (16.7/196.7), and `sm_2025-05-28.pdf` p.14's
"Nov24–Jan25" column (27/222.3) are *all* likewise excluded — so `sm_2026-05-28.pdf`'s "Nov25–Jan26"
column (15/324) being excluded is consistent, by-design behavior, not an isolated oversight. I'd
drop this item from the recommended-fixes list; the only genuine, tier-split data hole in that window
is the one both passes already identify — 2025-05 through 2026-01 has no *single-month* tier-level
waitlist source anywhere in this archive (only combined monthly totals, p.17) because the
intervening quarterly court filings were never collected into `data/raw/co/` (documented in
`data/raw/co/README.md`'s docket-gap between documents #310 and #341).

**Net effect on the fix list**: unchanged except dropping the "Nov25–Jan26" item — the actionable
items remain (1) recover `sm_2024-11-28.pdf`'s 6 rows, and (2) resolve the 8 blank
`is_multi_month_avg` flags to their determinable values.
