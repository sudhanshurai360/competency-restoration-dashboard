# California DSH Data — Independent Audit Pass 2

Date: 2026-09-11
Scope: `/Users/sudhanshu/git_clone/competency-restoration-dashboard/data/derived/california.csv` (25 rows), all 9 PDFs in `data/raw/ca/`.

Method: computed SHA-256 of every raw PDF and confirmed all 9 `source_sha` values in the CSV match the first 12 hex chars of the actual file hash (no swapped/stale files). Extracted full text with `pdftotext -layout`, split into per-page files, and manually read every cited page's printed text against the CSV `value`/`period`. Then ran corpus-wide adversarial sweeps: (a) every page containing 2+ "Data as of" footnotes, to hunt for the footnote-digit-glue bug; (b) every page matching waitlist/pending-placement snapshot language, to check for uncited dated readings; (c) every page containing a "Table 2: IST System-wide Pending Placement List" (or equivalent), to check the annual FY table is captured everywhere it appears and consistently.

## Result: CLEAN — all 25 rows verified correct, no discrepancies found.

### Per-PDF breakdown

**may2024-25.pdf (654f3ec78ae2) — CLEAN, 4 rows**
- p.125, Table 2: FY2018-19=849 → row `2019-06,849` ✓. Prose: "1,718 patients in July 2022" → `2022-07,1718` ✓; "894 patients in June 2023" → `2023-06,894` ✓ (also = Table 2 FY2022-23 cell).
- p.14: "397 as of May 6, 2024" → `2024-05,397` ✓.

**may2025-26.pdf (e1d747e0e150) — CLEAN, 5 rows**
- p.66: "850 individuals pending placement" (Feb 2020) → `2020-02,850` ✓.
- p.127, Table 2: FY2019-20=1212 → `2020-06,1212` ✓. Prose: "910 patients in July 2023" → `2023-07,910` ✓; "425 patients in June 2024" → `2024-06,425` ✓; "384 patients pending placement as of September 30, 2024" → `2024-09,384` ✓.
- p.67: **This is the adversarial trap page** — two footnotes on one page: footnote 4 "Data as of January 1, 2025" attached to the value 359 (a recap of the Governor's Budget figure), and footnote 5 "Data as of May 7, 2025" attached to the new May Revision figure. The raw extracted text literally glues the footnote marker onto the number with no separator: *"there are 2785 individuals on the waitlist"* (= "278" + footnote-5 marker "5"). The very next sentence disambiguates: "of the **278** individuals on the waitlist pending admission to a treatment bed, 121 are receiving..." confirming the true printed value is **278**, dated May 7, 2025. CSV row `2025-05,278` is **correct** — the pipeline correctly split the digit-glued "2785" back to 278 and did not mis-key it to the 359/January-2025 footnote. This confirms the specific historical bug class did NOT reproduce here.

**may2026-27.pdf (f4933cdccac3) — CLEAN, 7 rows**
- p.125, Table 2: FY2020-21=1454 → `2021-06,1454` ✓; FY2021-22=1779 → `2022-06,1779` ✓. Prose: "383 patients in July 2024" → `2024-07,383` ✓; "287 patients in June 2025" → `2025-06,287` ✓ (=Table2 FY2024-25); "277 patients pending placement as of August 25, 2025" → `2025-08,277` ✓.
- p.15: "the IST waitlist reached a high of 1,953 ... as of January 2022" → `2022-01,1953` ✓ (single footnote-free sentence, unambiguous).
- p.59: single footnote 4 "Data as of May 12, 2026" attached to "there are 256 4 individuals on the waitlist" → `2026-05,256` ✓. No ambiguity (only one footnote on this page).

**may2022-23.pdf (33f881887503) — CLEAN, 1 row**
- p.15: "IST waitlist has increased by 125 percent to 1,951 as of February 28, 2022" → `2022-02,1951` ✓.

**gov2023-24.pdf (22a233b5a56b) — CLEAN, 2 rows**
- p.14: "increased ... to 1,737 as of August 29, 2022" → `2022-08,1737` ✓.
- p.91: "As of December 12, 2022, the waitlist has declined to 1,473" → `2022-12,1473` ✓.

**may2023-24.pdf (4548799cca7d) — CLEAN, 1 row**
- p.91: "declined to 804 as of April 3, 2023" → `2023-04,804` ✓.

**gov2024-25.pdf (2b6b2aea54e7) — CLEAN, 2 rows**
- p.17: "down to 549 as of November 6, 2023" → `2023-11,549` ✓.
- p.69: single footnote 9 "Data as of January 1, 2024" on "the IST waitlist is currently at 501 9" → `2024-01,501` ✓. No second footnote on this page (footnotes 10/11 continue onto the next page for an unrelated topic — verified, not a collision).

**gov2025-26.pdf (22afa42c6038) — CLEAN, 1 row**
- p.18: "down to 359 as of January 1, 2025" → `2025-01,359` ✓. (Same figure/date also recapped on p.69 with an explicit footnote 5 "Data as of January 1, 2025" alongside a *different* footnoted figure, footnote 4 = 397/"Data as of May 6, 2024" — both values already independently captured elsewhere in the CSV from their primary source pages; no collision, no double-count, no mis-assignment.)

**gov2026-27.pdf (21b69d7476bd) — CLEAN, 1 row**
- p.50: footnote 4 "Data as of January 5, 2026" on "there are 275 4 individuals on the waitlist" → `2026-01,275` ✓. Only one footnote on this page (the 278 and 1,953 figures mentioned in the same paragraph are unfootnoted recaps of prior-report figures already captured elsewhere).

## Adversarial footnote-collision sweep

Every page in the 9-PDF corpus containing 2+ "Data as of" footnotes was individually opened and read:

| Page | Topic | IST waitlist row affected? |
|---|---|---|
| may2025-26 p.67 | IST waitlist (278/359) | Yes — verified correct, see above |
| gov2025-26 p.69 | IST waitlist (397/359, recap) | Yes — both values already correctly captured from their primary pages; no error |
| may2024-25 p.72 | IST waitlist (501/397, recap) | Yes — both values already correctly captured from their primary pages; no error |
| gov2025-26 p.32 | LPS census (122/246) | No — different metric (LPS, not IST) |
| gov2026-27 p.29 | LPS census (65/134) | No — different metric (LPS) |
| may2024-25 p.89 | LPS referral list (136/285) | No — different metric (LPS) |
| may2024-25 p.78 | County LOI contract counts (24/32) | No — unrelated |
| may2025-26 p.30 | LPS/NR-MT reimbursement (103/249) | No — different metric (LPS) |
| may2026-27 p.29 | LPS reimbursement (84/162) | No — different metric (LPS) |

No footnote-digit-glue mis-assignment was found anywhere else in the corpus. The one page engineered to trigger this exact bug (may2025-26 p.67, "2785") was handled correctly by the current pipeline.

## Completeness sweep

- Grepped the full corpus for every waitlist/pending-placement snapshot sentence pattern ("waitlist is currently at", "declined to", "reached a high of", "individuals on the waitlist", "IST PPL decreased/increased", "pending placement list as of", etc.). Every dated reading found across all 9 PDFs is a duplicate/recap of a value already present in the CSV under its primary source page — no orphan dated readings were found.
- Confirmed the annual "Table 2: IST System-wide Pending Placement List" (FY-end snapshots) recurs identically across gov2024-25 p.125, gov2025-26 p.127, gov2026-27 p.123, may2024-25 p.125, may2025-26 p.127, and may2026-27 p.125 — all five FY-end values (849, 1212, 1454, 1779, 894, 425, 287) are numerically identical everywhere they recur, and all are present in the CSV via one authoritative source page each (no duplicate rows, no conflicting values across reports).
- Confirmed the LPS and NGI "Table 2/3/5" pending-placement tables (e.g. gov2024-25 p.135, p.141) are a distinct metric family and correctly excluded from this `ist_pending_placement` extraction.
- No PDF has a dated IST-waitlist reading that is missing from the CSV.

## Overall verdict

**All 25 rows in california.csv are CLEAN.** All 9 `source_sha` values match their physical files. No value/period/page mismatches, no footnote mis-assignments, no missing readings, no duplicate/conflicting rows.
