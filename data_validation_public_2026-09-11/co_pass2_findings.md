# Colorado Data Integrity Audit — Pass 2 (independent re-verification)

Scope: `data/derived/colorado_jbc.csv` (6 rows) and `data/derived/colorado_special_master.csv`
(95 rows), checked against `data/raw/co/*.pdf` (14 files). Every row's cited `pdf_page` was opened
with `pdftotext -f N -l N -layout` (and, where text extraction was unreliable or a visual check was
needed, rendered to PNG with `pdftoppm` and read directly). File integrity was also confirmed: the
sha256 prefix of every cited raw PDF matches the `source_sha` column exactly in both CSVs (11/11
files checked, no mismatches).

## Bottom line

- Every value in every row of both CSVs matches the printed number on the cited page. Zero value
  errors found.
- The specifically-flagged correction (2024-07 and 2024-10, `tier_wait_days_restoration`, both
  tiers, `sm_2025-05-28.pdf`, page 12) is CORRECT: values match, `is_multi_month_avg=True` is
  correct, and the page genuinely carries a 3-month-range header with a dash glued directly onto
  the first month name ("May– Jul 24", "Aug– Oct 24" — no space before the dash, space after).
  Confirmed by direct inspection of `pdftotext -layout` output for that page.
- One analogous, uncorrected instance of the same class of bug found in `sm_109331.pdf` (see
  below) — the value is right but the multi-month flag is wrong/missing.
- Two real completeness gaps found: usable monthly data sitting in the raw PDFs that never made
  it into either CSV (see Completeness section).

## Per-PDF results

### `fy2024-25_humbrf2.5.pdf` — CLEAN, 4 rows
- p.20: `restoration_waitlist_count=431.0` as of "September 30, 2023" — verbatim: "The Department
  reports that 431 individuals are on the waitlist ... as of September 30, 2023." ✓
- p.20: `avg_wait_days_restoration=110.0`, as_of "105-115 day range" — verbatim: "Average time on
  the waitlist is 105-115 days." Value 110 is the midpoint, correctly flagged as a range in `as_of`. ✓
- p.20: `decree_fines_capped_$M=12.0`, FY2023-24 — verbatim: "Fines were capped to $12.0 million
  General Fund in FY 2023-24." ✓
- p.10: `decree_fines_uncapped_est_$M=65.2`, FY2022-23 — verbatim: "fines would have totaled $65.2
  million in FY 2022-23." (Both this figure and the $12.0M figure also appear again on p.20; citing
  either page is fine since both are genuinely present on both pages.) ✓
- `pdf_page` numbering matches file-order page count, not the printed page-number in the footer
  (e.g. `pdf_page=20` prints footer "17" — the file has front-matter pages before the report's own
  numbering starts). Internally consistent throughout, not a bug.

### `fy2025-26_humbrf1.5.pdf` — 1 row CLEAN, but see Completeness (missing rows)
- p.45: `decree_fines_capped_$M=12.2`, FY2024-25 — verbatim: "Fines were capped to $12.2 million
  General Fund in FY 2024-25." ✓ (Appendix A, p.82, confirms $12,230,000 as the FY2024-25
  appropriation for "Consent Decree Fines and Costs" — consistent to the tenth of a million.)
- See Completeness section below — this PDF contains an entire unused monthly waitlist/wait-time
  table.

### `jbc_memo.pdf` — CLEAN, 1 row (with a source-document quirk noted)
- p.4: `restoration_waitlist_count=391.0` as of "January 9, 2024" — verbatim: "391 individuals are
  on the waitlist as of January 9, 2024." ✓ matches CSV exactly.
- Note (not a CSV error): p.5 of this same PDF has a chart caption that instead reads "...was 390 as
  of January 9, 2024" — a 1-person discrepancy *within the source document itself* between the body
  text (p.4, cited by the CSV) and the chart caption (p.5, not cited). The CSV correctly reflects the
  page it cites (p.4, "391"), so this is a source-document quirk to be aware of, not a dataset bug.

### `sm_109331.pdf` (June 2020 report) — values CLEAN, but `is_multi_month_avg` flag issue found
- p.12, tier_wait_days_restoration: table columns are "Nov – Jan 2019/20 | Feb 2020 | Mar 2020 |
  Apr 2020". Tier 1: 2.47, 1.6, 3.6, 10.3. Tier 2: 97.87, 80.2, 63.8, 72.0. All four CSV values for
  both tiers (period 2020-01..2020-04) match these exactly. ✓ values correct.
  - **Issue**: the CSV labels the first column as period `2020-01` — but per the table header that
    column is actually a 3-month average ("Nov 2019 – Jan 2020"), the same situation as the
    2024-07/2024-10 correction described in the task. Unlike that later fix, here
    `is_multi_month_avg` is left **blank** (not `True`) for the 2020-01 row (both tiers). The
    2020-02/03/04 rows (genuinely single-month) are also left blank rather than `False`, which is
    inconsistent with how the rest of the dataset flags single-month figures (explicit `False`).
    Net effect: no wrong numbers, but the multi-month nature of the 2020-01 figure is not flagged,
    unlike the (correctly flagged) 2024-07/2024-10 rows in `sm_2025-05-28.pdf`.
- p.14, tier_waitlist_count: table "March 2019 | Jan 2020 | Feb 2020 | Mar 2020 | Apr 2020" — Tier
  1: 1, 2, 3, 1; Tier 2: 112, 115, 124, 110. All 8 CSV rows match exactly, correctly flagged `False`
  (single-month point-in-time counts, not averages). ✓

### `sm_2023-11-28.pdf` — CLEAN, 12 rows
- p.14: "Nov 22 – Jan 23 | Feb – Apr 23 | May – Jul 23 | Aug – Oct 23" — Tier 1: 81.1, 84.2, 109.1,
  128.3; Tier 2: 131.4, 140.2, 131.5, 138. CSV's `2023-01` row (both tiers, 81.1/131.4,
  `is_multi_month_avg=True`) matches the first column exactly. ✓
- p.13: "May 2023-Jul 2023 | Aug 2023 | Sep 2023 | Oct 2023" — Tier 1: 109.1, 131.9, 103.4, 124.9;
  Tier 2: 131.5, 134.9, 121.7, 156.6. CSV's `2023-08`/`2023-09` rows (both tiers, `False`) match the
  Aug/Sep single-month columns exactly. ✓ (The Oct 2023 single-month figures 124.9/156.6 on this
  page are not used in the CSV; instead the CSV uses the Aug–Oct 2023 rolling average — see next.)
- p.16: waitlist table "May–Jul 23 | Aug 2023 | Sep 2023 | Oct 2023" — Tier 1: 55, 47, 45, 35; Tier
  2: 401, 395, 386, 392. CSV's `2023-08/09/10` `tier_waitlist_count` rows match Aug/Sep/Oct columns
  exactly for both tiers. ✓

### `sm_2024-02-28.pdf` — CLEAN, 12 rows
- p.12: "Aug 2023-Oct 2023 | Nov 2023 | Dec 2023 | Jan 2024" — Tier 1: 122.7, 50.5, 113.6, 95.4;
  Tier 2: 138.3, 135.9, 125.4, 126.6. CSV's `2023-11`/`2023-12` rows (both tiers, `False`) match the
  Nov/Dec columns exactly. ✓
- p.13: "Feb–Apr 23 | May–Jul 23 | Aug–Oct 23 | Nov23-Jan24" — Tier 1: 84.2, 109.1, 128.3, 92.0;
  Tier 2: 140.2, 131.5, 138, 129.7. CSV's `2023-04` row (both tiers, `True`) matches the Feb–Apr 23
  column exactly. ✓
- p.15: waitlist table "March2019 | Aug-Oct23 | Nov2023 | Dec2023 | Jan2024" — Tier 1: N/A, 42, 39,
  31, 23; Tier 2: N/A, 391, 372, 335, 351. CSV's `2023-11/12` and `2024-01` `tier_waitlist_count`
  rows match the Nov/Dec/Jan columns exactly for both tiers. ✓

### `sm_2024-05-28.pdf` — CLEAN, 12 rows
- p.11: "Nov2023-Jan2024 | Feb2024 | Mar2024 | Apr2024" — Tier 1: 92.0, 48.5, 58.1, 54.9; Tier 2:
  129.7, 111.2, 132.5, 106.1. CSV's `2024-02`/`2024-03` rows (both tiers, `False`) match exactly. ✓
- p.12: "May–Jul23 | Aug–Oct23 | Nov23-Jan24 | Feb–Apr24" — Tier 1: 109.1, 128.3, 92.0, 54.3; Tier
  2: 131.5, 138, 129.7, 115.1. CSV's `2023-07` row (both tiers, `True`) matches the May–Jul 23
  column exactly. ✓
- p.14: waitlist "Nov23-Jan24 | Feb2024 | Mar2024 | Apr2024" — Tier 1: 31, 15, 22, 30; Tier 2: 353,
  314, 302, 266. CSV's `2024-02/03/04` `tier_waitlist_count` rows match exactly for both tiers. ✓

### `sm_2024-08-28.pdf` — CLEAN, 10 rows
- p.12: "Aug–Oct23 | Nov23-Jan24 | Feb–Apr24 | May–Jul24" — Tier 1: 128.3, 92, 54.3, 69.2; Tier 2:
  138, 129.7, 115.1, 104.1. CSV's `2023-10` and `2024-01` rows (both tiers, `True`) match the
  Aug–Oct 23 and Nov23–Jan24 columns exactly. ✓
- p.14: waitlist "Feb–Apr24 | May2024 | Jun2024 | Jul2024" — Tier 1: 22, 18, 14, 12; Tier 2: 294,
  252, 227, 215. CSV's `2024-05/06/07` `tier_waitlist_count` rows match exactly for both tiers. ✓

### `sm_2025-02-28.pdf` — CLEAN, 8 rows
- p.12: "Feb24-Apr24 | May24-Jul24 | Aug-Oct24 | Nov24-Jan25" — Tier 1: 54.3, 69.2, 40.3, 47.5;
  Tier 2: 115.1, 104.1, 95.3, 80.3. CSV's `2024-04` row (both tiers, `True`) matches the Feb–Apr 24
  column exactly. ✓
- p.14: waitlist "Aug-Oct24 | Nov2024 | Dec2024 | Jan2025" — Tier 1: 16.7, 19, 23, 39; Tier 2:
  196.7, 198, 224, 245. CSV's `2024-11/12` and `2025-01` `tier_waitlist_count` rows match the
  Nov/Dec/Jan columns exactly for both tiers. ✓

### `sm_2025-05-28.pdf` — CLEAN, 14 rows — **includes the specifically-flagged re-verification**
- p.12 (`pdftotext -layout` raw output): header reads `May– Jul 24       Aug– Oct 24         Nov 24 –
  Jan 25            Feb - Apr 25` — confirmed: "May" and "Aug" have the en-dash glued directly to
  the month name with no space ("May–", "Aug–"), while "Nov 24 – Jan 25" and "Feb - Apr 25" have
  normal spacing. This is exactly the glued-dash pattern described as the historical bug trigger.
  Table values — Tier 1: 69.2, 40.3, 47.5, 59.7; Tier 2: 104.1, 95.3, 80.3, 70.8.
  - CSV `2024-07` (both tiers) = 69.2 / 104.1, `is_multi_month_avg=True` ✓ CORRECT
  - CSV `2024-10` (both tiers) = 40.3 / 95.3, `is_multi_month_avg=True` ✓ CORRECT
  - CSV `2025-01` (both tiers) = 47.5 / 80.3, `True` ✓; CSV `2025-04` (both tiers) = 59.7 / 70.8,
    `True` ✓
  - **Conclusion: the hand correction is verified correct.** Values, period assignment, and the
    multi-month flag all check out against the actual printed page.
- p.14: waitlist "March2019 | Nov24-Jan25 | Feb2025 | Mar2025 | Apr2025" — Tier 1: N/A, 27, 55, 51,
  47; Tier 2: N/A, 222.3, 259, 265, 310. CSV's `2025-02/03/04` `tier_waitlist_count` rows match the
  Feb/Mar/Apr 2025 columns exactly for both tiers. ✓

### `sm_2026-05-28.pdf` — CLEAN, 14 rows
- p.13: "May–July25 | Aug-Oct25 | Nov25-Jan26 | Feb-Apr26" — Tier 1: 61.5, 33.2, 65.0, 30.7; Tier
  2: 92.2, 92.7, 89.4, 82.4. CSV's `2025-07`, `2025-10`, `2026-01`, `2026-04` rows (both tiers,
  `True`) all match exactly. ✓
- p.16: waitlist "March2019 | Nov25-Jan26 | Feb2026 | Mar2026 | Apr2026" — Tier 1: N/A, 15, 17, 17,
  10; Tier 2: N/A, 324, 355, 359, 354. CSV's `2026-02/03/04` `tier_waitlist_count` rows match the
  Feb/Mar/Apr 2026 columns exactly for both tiers. ✓

### `sm_109305.pdf` (Dec 2018 Order Appointing Special Master) — not cited, correctly excluded
Full text reviewed. Contains a "Chart 1" of monthly wait-time data June 2017–August 2018, but this
predates the June 2019 Tier 1/Tier 2 triage system entirely (single combined average, no tier
split, no waitlist counts) — it does not fit either CSV's schema and its exclusion is appropriate,
not a completeness gap.

### `sm_109327.pdf` (March 2019 status report) — not cited, correctly excluded
Full text reviewed. Contains only evaluation/restoration order counts (no tier-based wait times, no
tier waitlist counts — predates the Tier system). Exclusion is appropriate.

## Completeness gaps (real, unindexed data found in the raw PDFs)

1. **`sm_2024-11-28.pdf` is not cited anywhere in either CSV**, yet page 14 has a monthly
   `Number of Defendants Waiting for Inpatient Restoration` table for **Aug 2024 / Sep 2024 / Oct
   2024** with tier splits: Tier 1 = 16, 18, 16; Tier 2 = 200, 198, 192 (visually confirmed by
   rendering the page to PNG, since `pdftotext` fails to extract this file's text — it returns
   garbled private-use-area characters, likely a font-encoding issue specific to this PDF).
   `colorado_special_master.csv` jumps directly from `2024-07` waitlist counts (sourced from
   `sm_2024-08-28.pdf`) to `2024-11` (sourced from `sm_2025-02-28.pdf`), skipping three real months
   that exist in the source material. (The same page's wait-*time* table, "Aug – Oct 24" quarterly
   average of 40.3/95.3, is captured in the CSV — but sourced from the later `sm_2025-05-28.pdf`
   instead, where the identical figures reappear. So only the *monthly waitlist-count* breakdown for
   these three months is missing, not the wait-time average.)

2. **`fy2025-26_humbrf1.5.pdf` contains an entire unused monthly dataset.** Page 57 (file page; PDF
   text says "p. 55" in its own footer) has a full FY2023-24 "Competency Restoration Waitlist" table
   with three columns per month (Individuals on Waitlist, Average Wait Time, Maximum Wait Time) for
   all 12 months July 2023–June 2024:
   - Jul 460/112/514, Aug 444/91/545, Sep 431/106/576, Oct 429/99/379, Nov 418/96/409,
     Dec 350/94/375, Jan 383/93/371, Feb 329/95/391, Mar 324/90/394, Apr 297/89/425, May 270/91/456,
     Jun 241/93/464.
   - None of this monthly table is reflected in `colorado_jbc.csv`, which has only two
     `restoration_waitlist_count` rows total (2023-09 and 2024-01) and one `avg_wait_days_restoration`
     row (a non-month-specific "105-115 day range" figure). This table alone would supply 12 precise
     monthly waitlist counts and 12 precise monthly average-wait-day figures that are currently
     either absent or only approximated.
   - Note: September 2023's waitlist count in this table (431) is consistent with the CSV's existing
     `2023-09` row (431, sourced from a different PDF) — good cross-report agreement. But the
     January 2024 waitlist count here (383, presumably end-of-month) differs from the CSV's `2024-01`
     value (391, explicitly "as of January 9, 2024" per its `as_of` field) — not a contradiction,
     just two different snapshot dates within the same month, correctly distinguished by the `as_of`
     field already in the CSV.
   - The same PDF's page 46 (prose, not the table) separately states waitlist=460 (Jul 2023),
     waitlist=241 (Jun 2024), average wait=95.8 days (FY2023-24 overall), max wait=576 days
     (Sep 2023) — consistent with the table above, also unused.
   - Also unused: page 82 (Appendix A) "Consent Decree Fines and Costs" actual appropriation figures
     — FY2022-23 $11,134,173, FY2023-24 $11,787,297, FY2024-25 $12,230,000 (consistent with the
     $12.2M already in the CSV), FY2025-26 request $7,230,000 — and a monthly FY2023-24
     fines/fees-paid table (pages 55-56 in the PDF's own numbering) totaling $11,787,298. These are a
     different accounting view (actual dollars paid vs. the annual cap/uncapped-estimate narrative
     figures already captured) and may be out of scope for the current schema, but are additional
     verifiable data sitting unused in the source.

## Minor source-document inconsistencies (not CSV bugs, flagged for awareness)
- `jbc_memo.pdf`: p.4 body text says "391 ... as of January 9, 2024"; p.5 chart caption says "390 ...
  as of January 9, 2024" — a 1-person discrepancy inside the same PDF. CSV cites p.4 correctly.
- Waitlist all-time-peak value (464) is consistently reported across `jbc_memo.pdf` and
  `fy2025-26_humbrf1.5.pdf`, but the *month* of that peak is reported inconsistently across the
  source documents (jbc_memo.pdf p.5 says "February 2023"; fy2025-26_humbrf1.5.pdf p.46 says "May
  2023"; other Special Master reports say "June 2023"). Neither the value nor any of these dates is
  used in either CSV, so this doesn't affect the dataset, but it's a real inconsistency in the
  underlying government source material worth knowing about if these narratives are ever quoted.

## File-integrity check
sha256 prefix of every cited raw PDF matches the `source_sha` column in both CSVs exactly (checked
all 11 distinct source files cited across both CSVs: `fy2024-25_humbrf2.5.pdf`,
`fy2025-26_humbrf1.5.pdf`, `jbc_memo.pdf`, `sm_109331.pdf`, `sm_2023-11-28.pdf`,
`sm_2024-02-28.pdf`, `sm_2024-05-28.pdf`, `sm_2024-08-28.pdf`, `sm_2025-02-28.pdf`,
`sm_2025-05-28.pdf`, `sm_2026-05-28.pdf`). No mismatches.
