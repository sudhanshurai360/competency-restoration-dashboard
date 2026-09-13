# Data dictionary and pipeline

Six files under `data/derived/`, one or two per state, each in a long schema with an explicit
per-row source citation. Every row's `report`/`pdf_page`/`table_ref` (or `_days`-suffixed sibling,
for Texas) columns point at the exact source document and location a value came from — cross-
reference against `data/raw/<state>/` and `SOURCES.csv`.

## `washington.csv`
One row per (facility, stage, setting, period). Washington republishes each month's data across
roughly a dozen subsequent monthly reports; the harmonized panel keeps the value from the most
recent report that successfully covers a given period.

| Column | Meaning |
|---|---|
| `facility` | WSH, ESH, RTF, OCRP, or TOTAL |
| `stage` | `evaluation` or `restoration` |
| `setting` | `jail`, `inpatient`, or `outpatient` |
| `orders_signed` | Court orders signed that month (demand) |
| `orders_completed` | Orders completed that month |
| `avg_days_to_completion` / `median_days_to_completion` | Days from order signature to completion |
| `pct_within_deadline` | % completed within 7 days of order **signature** (this project's primary/strictest published clock-start) |
| `pct_within_alt2` / `pct_within_alt3` | Two looser published alternative clock-starts (DSHS receipt of order; referral to DSHS) |
| `report` / `pdf_page` / `table_ref` | Source citation |

## `oregon.csv`
One row per (period, metric). Metrics include admission flow (`admits`, `avg_wait`,
`pct_within_7day`), waitlist stock (`waitlist_count`, its own `avg_days` companion), and facility
capacity/census/contempt-fine figures. A metric's basis (flow vs. stock) is not interchangeable —
see `README.md`'s "Coverage" section.

## `colorado_special_master.csv`
One row per (period, tier, metric). `tier` is 1 (acute, 7-day standard) or 2 (28-day standard,
phased down over time — the historical standard in force for a given period is NOT always today's
28 days; see `src/co_special_master.py` for the exact phase-down schedule). `metric` is
`tier_wait_days_restoration` or `tier_waitlist_count`. **Note**: the wait-days value and the
waitlist-count value for the same (period, tier) can come from different source
report/page — check both columns' own citation, don't assume they share one source.

## `colorado_jbc.csv`
One row per (period, metric). Metrics: `restoration_waitlist_count` (a point-in-time snapshot, not
a monthly series), `decree_fines_capped_$M` / `decree_fines_uncapped_est_$M` (contempt-fine
figures under the consent decree). Uses `source` (not `report`) as its citation-filename column —
a schema quirk from `co_jbc.py`, not an error.

## `texas.csv`
One row per (period, security_level). `security_level` is `max` (maximum-security queue) or
`non_max`. `waitlist_count` and `avg_wait_days` can cite **different** source pages within the same
report (`pdf_page`/`table_ref` for the count, `pdf_page_days`/`table_ref_days` for the wait-days
figure) — Texas's own source tables split these across separate tables. `avg_wait_days` is
sometimes empty for `max` in recent periods — Texas's own source explicitly states the
maximum-security queue is not a physical location people admit directly from, so no wait-day figure
is published for it in those periods; this is a disclosed source-side gap, not a pipeline defect.
`removed_count` (added v1.0.3) is the number of people removed from that security level's waitlist
that quarter (its own `pdf_page_removed`/`table_ref_removed` citation columns, since HHSC's newer
report format also tables this separately) — a flow figure, not a restatement of `waitlist_count`.

## `california.csv`
One row per (period, metric). `metric` is `ist_pending_placement` (the only metric currently
tracked). `kind` distinguishes `annual_fy_table` (a clean fiscal-year-end table row) from
`prose_snapshot` (a dated reading extracted from budget narrative prose — genuinely irregular
cadence, not a monthly series). The extractor still deliberately does not resolve a bare
budget-cycle-relative phrase ("as of the 2026-27 Governor's Budget") to a calendar month on its
own — but as of v1.0.2, it separately recovers the same figures from a distinct "Justification"
section each report also carries, which pairs the reading with an unambiguous dated footnote
("Data as of May 12, 2026"). This closed what was previously the dataset's largest staleness gap.

`colorado_special_master.csv` also carries an `is_multi_month_avg` column (added v1.0.2), for
`tier_wait_days_restoration` rows only (blank/NA for `tier_waitlist_count`): `True` if that reading
is a 3-month rolling average dated to its own end month rather than a true single-month figure —
the source reports mix both, and their own prose treats the rolling average as the headline
compliance figure, not a lesser one. `False` means a true single month. As of v1.0.3, every row
resolves to `True` or `False` — the handful that shipped blank in v1.0.2 (period couldn't be
determined from that row's own header) were traced to 2 header-parsing bugs and fixed; no
underlying `value` changed, only the flag.

## The re-execution gate — `src/verify.py`

Rebuilds each state's dataset from `data/raw/<state>/*.pdf` and asserts:
- structural invariants (every row has a period, no unclassified facility/category, no duplicate
  keys),
- a handful of hand-verified value anchors against the source PDFs (so a systematic extraction
  regression is caught, not just a structural one),
- for Washington specifically, a targeted completeness check on the **newest** report's own row
  count — the one period with no later report to silently recover from if its own table extraction
  ever failed (a real, independently-confirmed pdfplumber failure mode on this document corpus;
  see `src/wa_trueblood.py`'s own docstring for the two known failure patterns).

Run `python src/verify.py` from the archive root after installing `requirements.txt`; a clean run
prints `PASSED — 0 failure(s)`.
