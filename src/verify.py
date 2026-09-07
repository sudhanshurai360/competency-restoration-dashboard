"""Competency Restoration Dashboard Data — re-execution gate.

Seeded from `checks_multistate.RECOVERED_FRAGMENTS.md` (verbatim-recovered anchors, HIGH
confidence, two independent corpus corroborations for the TX/CO-JBC/OR/CA block) plus the CO
Special-Master §2 "superseded" point-value anchors (with the fragment's own documented correction:
2020-02, not the wrong 2020-01, per the transcript's own later fix) — plus new structural/value
anchors for WA, ported from code/pipeline/checks.py's own WA anchor (same source PDF, same
expected value: this tree's independently-run wa_trueblood.py should reproduce it exactly).

One anchor from the recovered fragment was a KNOWN, DISCLOSED gap for a while: CA's 2022-12
datapoint. It turned out not to be a cadence gap at all — the value (1,473) was sitting verbatim
in an already-downloaded PDF (gov2023-24.pdf) the whole time, in date-then-value word order
("As of December 12, 2022, ... declined to 1,473") that none of `ca_dsh.py`'s three prose regexes
matched. A 4th regex now recovers it; this is a real hard-checked anchor again, not a
known_gap placeholder.

The 2023-10 CO-SM anchor was ALSO a disclosed gap at first (a source PDF for that exact month
appeared never located) — but a subsequent phase-review found the real cause: `co_special_master.py`
had a systematic year-mis-dating bug (2-digit-year and cross-line column-wrap headers in the
2023+ report format weren't parsed), so the datapoint existed all along, just mis-dated to a
different period. Fixed via positional (word-coordinate) header reconstruction; 2023-10 is now
a real, passing check below, not a gap.
"""
import sys
import pandas as pd
import config as C

def main():
    fails = []

    def check(cond, msg):
        print(("  OK  " if cond else "  FAIL") + " " + msg)
        if not cond: fails.append(msg)

    def section(name, fn):
        # A missing derived parquet (extractor never run, or run against the wrong tree) is a
        # real gate failure, same as any other check() here -- it should NOT be silently
        # skipped the way build_data_page.py skips a missing dataset when rendering /data (that
        # page degrades gracefully by design; this gate's whole job is to catch exactly this).
        # But it also shouldn't crash the run with a raw FileNotFoundError traceback that hides
        # every OTHER section's results below it. Catch just that one exception, report it as a
        # normal FAIL line, and let every other section still run and report.
        print(f"--- {name} ---")
        try:
            fn()
        except FileNotFoundError as e:
            check(False, f"{name}: derived file missing ({e}) — run this state's extractor first")

    # ---------------- WA ----------------
    def _wa():
        wa = pd.read_parquet(C.DERIVED / "wa_trueblood_dashboard.parquet")
        check(wa["period"].notna().all(), "WA: every row has a period")
        check(wa["state"].eq("WA").all(), "WA: all rows state=WA")
        check(wa["facility"].eq("?").sum() == 0, f"WA: no unclassified facility (got {wa['facility'].eq('?').sum()})")
        dup = wa.duplicated(["facility", "stage", "setting", "period"]).sum()
        check(dup == 0, f"WA: no dup (facility,stage,setting,period) (got {dup})")
        ev = wa[(wa.facility == "WSH") & (wa.stage == "evaluation") & (wa.setting == "jail") & (wa.period == "2023-05")]
        if len(ev) == 1:
            r = ev.iloc[0]
            check(abs((r.orders_completed or 0) - 491) <= 1, f"WA WSH jail-eval 2023-05 completed≈491 (got {r.orders_completed})")
            check(abs((r.avg_days_to_completion or 0) - 12.7) <= 0.5, f"WA WSH jail-eval 2023-05 avg≈12.7 (got {r.avg_days_to_completion})")
            check(abs((r.median_days_to_completion or 0) - 13) <= 1, f"WA WSH jail-eval 2023-05 median≈13 (got {r.median_days_to_completion})")
        else:
            check(False, "WA WSH jail-eval 2023-05 anchor row present")
        # WSH/RTF cross-contamination anchor (a real, previously-shipped bug: two facility-sharing
        # tables on one page, RTF's true row absorbed and mislabeled as WSH's -- see
        # wa_trueblood.py's parse_report() docstring). Checks BOTH facilities' true, independently
        # PDF-verified values for the same disputed month so a regression back to either the old
        # cross-contaminated value or a new one can't silently pass.
        wsh0918 = wa[(wa.facility == "WSH") & (wa.stage == "restoration") & (wa.setting == "inpatient") & (wa.period == "2018-09")]
        rtf0918 = wa[(wa.facility == "RTF") & (wa.stage == "restoration") & (wa.setting == "inpatient") & (wa.period == "2018-09")]
        check(len(wsh0918) == 1 and wsh0918.iloc[0].orders_completed == 55,
              f"WA WSH restoration-inpatient 2018-09 completed=55 (got {wsh0918.iloc[0].orders_completed if len(wsh0918) else 'MISSING'})")
        check(len(rtf0918) == 1 and rtf0918.iloc[0].orders_completed == 22,
              f"WA RTF restoration-inpatient 2018-09 completed=22 (got {rtf0918.iloc[0].orders_completed if len(rtf0918) else 'MISSING'})")
        # Completeness: pdfplumber's table detection can return zero tables for a page with fully
        # legible tabular data (no vector-drawn lines to detect) -- confirmed on several 2019-2020
        # reports; the disclosed washington.html gap count comes from the same computation. Bound
        # it loosely rather than pin an exact count (new reports can only add rows, and a report
        # occasionally getting reprocessed could shift which report "wins" a period at the margin)
        # -- this check exists to catch a REGRESSION (the gap growing unexpectedly), not to demand
        # zero, which isn't achievable without inventing values this pipeline can't actually reach.
        def _missing_months(g):
            months = sorted(g.period.unique())
            if len(months) < 2:
                return 0
            y0, m0 = map(int, months[0].split("-")); y1, m1 = map(int, months[-1].split("-"))
            span = {f"{y:04d}-{m:02d}" for y in range(y0, y1 + 1) for m in range(1, 13)
                    if (y, m) >= (y0, m0) and (y, m) <= (y1, m1)}
            return len(span - set(months))
        gap_months = sum(_missing_months(g) for _, g in wa.groupby(["facility", "stage", "setting"]))
        check(gap_months <= 40, f"WA completeness gap bounded, not regressed (got {gap_months} missing facility/stage/setting-months, expect ~23)")
        # The check above bounds the WHOLE-PANEL gap total, but can't catch a fresh failure on
        # the newest report specifically: when an OLDER report's table fails to parse, the dedup
        # rule quietly falls back to a later report's successful read of the same month (see the
        # honest-disclosure text on washington.html) -- but the newest report has no later report
        # to fall back on yet, so a table-detection failure there would show up as a real, silent,
        # undisclosed missing month rather than self-healing. An independent audit (2026-09-07)
        # confirmed this failure mode is real (Trueblood-Report-2026-01.pdf yielded 64 rows vs.
        # ~142 in every neighboring report, from exactly this bug) -- it happened to land on an
        # already-superseded report, so nothing currently shown was wrong, but this check exists
        # so the same failure hitting a not-yet-superseded newest report gets caught, not masked.
        periods_sorted = sorted(wa.period.unique())
        latest_period = periods_sorted[-1]
        latest_n = (wa.period == latest_period).sum()
        prior_periods = periods_sorted[-13:-1] if len(periods_sorted) >= 13 else periods_sorted[:-1]
        prior_counts = sorted((wa.period == p).sum() for p in prior_periods)
        prior_median = prior_counts[len(prior_counts) // 2] if prior_counts else latest_n
        check(latest_n >= max(6, prior_median * 0.7),
              f"WA newest report ({latest_period}) completeness: {latest_n} facility/stage/setting rows "
              f"vs ~{prior_median} typical for recent reports -- no fallback exists yet for this period "
              f"if its own table extraction silently failed")
    section("WA", _wa)

    # ---------------- OR ----------------
    def _or():
        orp = pd.read_parquet(C.DERIVED / "or_osh_dashboard.parquet")
        def _org(period, metric):
            s = orp[(orp.period == period) & (orp.metric == metric)]["value"]
            return s.iloc[0] if len(s) else None
        check(abs((_org("2025-08", "admits") or 0) - 107) < 1, f"OR Aug-2025 admits=107 (got {_org('2025-08','admits')})")
        check(abs((_org("2024-04", "pct_within_7day") or 0) - 90.6) < 0.3, f"OR Apr-2024 within-7day=90.6% (got {_org('2024-04','pct_within_7day')})")
        check(abs((_org("2022-01", "waitlist_stock") or 0) - 93) < 1, f"OR 2022-01 stock=93 collision-fix (got {_org('2022-01','waitlist_stock')})")
        check(abs((_org("2025-11", "beds_licensed") or 0) - 738) < 1, f"OR 2025-11 beds_licensed=738 (got {_org('2025-11','beds_licensed')})")
        check(abs((_org("2026-03", "contempt_fines_accrued_musd") or 0) - 3.19) < 0.01, f"OR 2026-03 contempt=$3.19M (got {_org('2026-03','contempt_fines_accrued_musd')})")
        check(abs((_org("2025-08", "avg_wait_days") or 0) - 10.2) < 0.1, f"OR Aug-2025 avg_wait=10.2d (flow) (got {_org('2025-08','avg_wait_days')})")
        check(abs((_org("2025-08", "waitlist_count") or 0) - 34) < 1, f"OR Aug-2025 waitlist_count=34 (got {_org('2025-08','waitlist_count')})")
        check(abs((_org("2025-08", "pct_within_7day") or 0) - 7.5) < 0.2, f"OR Aug-2025 pct_within_7day=7.5 (got {_org('2025-08','pct_within_7day')})")
        check(abs((_org("2025-11", "avg_wait_days") or 0) - 19.1) < 0.1, f"OR Nov-2025 avg_wait=19.1d (flow) (got {_org('2025-11','avg_wait_days')})")
        check(abs((_org("2022-05", "waitlist_stock") or 0) - 67) < 1, f"OR baseline May-2022 stock~67 (got {_org('2022-05','waitlist_stock')})")
        check(abs((_org("2022-05", "waitlist_stock_avg_days") or 0) - 16.2) < 0.1, f"OR baseline May-2022 avg~16.2d (got {_org('2022-05','waitlist_stock_avg_days')})")
        check(abs((_org("2025-04", "admits") or 0) - 128) < 1, f"OR Apr-2025 admits=128 (got {_org('2025-04','admits')})")
        check(abs((_org("2025-10", "orders_received") or 0) - 100) < 1, f"OR 2025-10 orders=100 dedup-fix (got {_org('2025-10','orders_received')})")
        check(abs((_org("2023-11", "admits") or 0) - 108) < 1, f"OR Nov-2023 admits=108 recovered (got {_org('2023-11','admits')})")
        check(abs((_org("2023-11", "pct_within_7day") or 0) - 93.5) < 0.2, f"OR Nov-2023 within7=93.5 recovered (got {_org('2023-11','pct_within_7day')})")
        check(abs((_org("2026-03", "census_civil") or 0) - 35) < 1, f"OR 2026-03 census_civil=35 (got {_org('2026-03','census_civil')})")
    section("OR", _or)

    # ---------------- TX ----------------
    def _tx():
        tx = pd.read_parquet(C.DERIVED / "tx_hhsc_panel.parquet")
        rt = tx[(tx.security_level == "max") & (tx.period == "2023-08")]
        check(len(rt) == 1 and rt.iloc[0].waitlist_count == 968 and rt.iloc[0].avg_wait_days == 659,
              f"TX max FY2023-Q4 (2023-08): count=968/days=659 (got {rt[['waitlist_count','avg_wait_days']].values.tolist() if len(rt) else 'MISSING'})")
        # This anchor used to expect avg_wait_days=202 here -- that number was itself the bug (an
        # adversarial audit + direct PDF check confirmed 202 is Table 12's "Total" of a small,
        # already-facility-assigned population, not a wait-time measurement for the 419-person
        # statewide "Maximum Security" queue this row's count describes; HHSC's own footnote says
        # people "do not directly admit from the maximum security list"). The fix intentionally
        # leaves avg_wait_days unset here rather than substituting a different wrong number --
        # check for that gap explicitly so it can't silently regress back to the population-
        # mismatched fallback.
        rt25 = tx[(tx.security_level == "max") & (tx.period == "2025-08")]
        check(len(rt25) == 1 and rt25.iloc[0].waitlist_count == 419 and pd.isna(rt25.iloc[0].avg_wait_days),
              f"TX max FY2025-Q4 (2025-08): count=419/days=<disclosed gap, not a population mismatch> "
              f"(got {rt25[['waitlist_count','avg_wait_days']].values.tolist() if len(rt25) else 'MISSING'})")
        # non_max had ZERO gate coverage until now -- exactly the blind spot that let two real bugs
        # through undetected (an all-caps "TOTAL" row label the old exact-case regex never matched,
        # silently dropping mhs-waiting-lists-nov-2024.pdf's entire non_max series; and a
        # "Waitlist"/"Waiting List" wording mismatch that dropped mhs-waiting-lists-may-2023.pdf
        # entirely, both metrics). Anchors below are hand-verified against each source PDF's own
        # printed TOTAL row.
        rtnm = tx[(tx.security_level == "non_max") & (tx.period == "2023-11")]
        check(len(rtnm) == 1 and rtnm.iloc[0].waitlist_count == 1178 and abs(rtnm.iloc[0].avg_wait_days - 239.3) < 1e-6,
              f"TX non_max FY2024-Q1 (2023-11): count=1178/days=239.3 (got {rtnm[['waitlist_count','avg_wait_days']].values.tolist() if len(rtnm) else 'MISSING'})")
        rt2211 = tx[(tx.security_level == "max") & (tx.period == "2022-11")]
        check(len(rt2211) == 1 and rt2211.iloc[0].waitlist_count == 883 and rt2211.iloc[0].avg_wait_days == 519,
              f"TX max FY2023-Q1 (2022-11): count=883/days=519 (got {rt2211[['waitlist_count','avg_wait_days']].values.tolist() if len(rt2211) else 'MISSING'})")
        # Every downloaded PDF should contribute at least one row -- a silent 0-row parse (the exact
        # failure mode of both bugs above) should fail the gate, not just print a [warn] nobody reads.
        tx_reports_seen = set(tx.report.unique())
        tx_pdfs = sorted(p.name for p in (C.RAW / "tx").glob("mhs-waiting-lists-*.pdf"))
        tx_missing = [p for p in tx_pdfs if p not in tx_reports_seen
                      and p not in ("mhs-waiting-lists-may-2024.pdf", "mhs-waiting-lists-may-2025.pdf")]
        # may-2024/may-2025 are DISCLOSED exceptions: H1-only (2 quarters) reports _parse_new's NUM4
        # doesn't handle, but every period they'd cover is already present via the same-FY November
        # report -- confirmed no data loss, not silently ignored.
        check(not tx_missing, f"every TX PDF contributes rows except the disclosed H1-only ones (missing: {tx_missing})")
    section("TX", _tx)

    # ---------------- CO-JBC ----------------
    def _co_jbc():
        coj = pd.read_parquet(C.DERIVED / "co_jbc_snapshots.parquet")
        wl = coj[coj.metric == "restoration_waitlist_count"]["value"]
        check(wl.isin([431, 391]).any(), f"CO-JBC restoration waitlist anchor 431/391 (got {sorted(wl.tolist())})")
        check((coj[coj.metric == "decree_fines_capped_$M"]["value"] == 12.0).any(), "CO-JBC decree fines $12.0M cap present")
        avgwait = coj[coj.metric == "avg_wait_days_restoration"]["value"]
        check(len(avgwait) > 0 and avgwait.between(100, 120).any(),
              f"CO-JBC avg-wait ~100-120d anchor (got {sorted(avgwait.tolist())})")
    section("CO-JBC", _co_jbc)

    # ---------------- CO Special-Master (point-value anchors, §2 -- supersedes range checks) ----------------
    def _co_sm():
        sm = pd.read_parquet(C.DERIVED / "co_special_master.parquet")
        def _sm(period, tier, metric):
            s = sm[(sm.period == period) & (sm.tier == tier) & (sm.metric == metric)]["value"]
            return s.iloc[0] if len(s) else None
        check(abs((_sm("2020-02", 1, "tier_wait_days_restoration") or -1) - 1.6) < 0.5,
              f"CO-SM Tier-1 2020-02 wait=1.6d (corrected from the fragment's wrong 2020-01/1d, got {_sm('2020-02', 1, 'tier_wait_days_restoration')})")
        check(abs((_sm("2026-04", 1, "tier_wait_days_restoration") or -1) - 30.7) < 0.05,
              f"CO-SM Tier-1 2026-04 wait=30.7d (most recent, hand-verified, got {_sm('2026-04', 1, 'tier_wait_days_restoration')})")
        check(abs((_sm("2020-02", 2, "tier_wait_days_restoration") or -1) - 80.2) < 0.5,
              f"CO-SM Tier-2 2020-02 wait=80.2d, over the 49d limit (corrected from the fragment's wrong 2020-01/112d, got {_sm('2020-02', 2, 'tier_wait_days_restoration')})")
        check(abs((_sm("2026-04", 2, "tier_waitlist_count") or -1) - 354) < 0.5,
              f"CO-SM Tier-2 2026-04 waitlist count=354 (most recent, hand-verified, got {_sm('2026-04', 2, 'tier_waitlist_count')})")
        check(abs((_sm("2023-10", 1, "tier_wait_days_restoration") or -1) - 128.3) < 0.05,
              f"CO-SM Tier-1 2023-10 wait=128.3d (2023 crisis peak, got {_sm('2023-10', 1, 'tier_wait_days_restoration')})")
        check(abs((_sm("2023-10", 2, "tier_wait_days_restoration") or -1) - 138) < 0.05,
              f"CO-SM Tier-2 2023-10 wait=138d (2023 crisis peak, got {_sm('2023-10', 2, 'tier_wait_days_restoration')})")
    section("CO-SM", _co_sm)

    # ---------------- CA ----------------
    def _ca():
        ca_df = pd.read_parquet(C.DERIVED / "ca_dsh.parquet")
        ca = ca_df.set_index("period")["value"].to_dict()
        check(ca.get("2022-01") == 1953, f"CA Jan-2022 peak=1953 (got {ca.get('2022-01')})")
        check(ca.get("2024-05") == 397, f"CA May-2024=397 (got {ca.get('2024-05')})")
        check(ca_df["value"].isin([849, 1212, 1454, 1779]).sum() >= 2,
              "CA annual FY table values present (>=2 of the known set)")
        check(ca.get("2022-12") == 1473,
              f"CA 2022-12=1473 (got {ca.get('2022-12')}) — recovered via a 4th prose regex; was a "
              "disclosed gap, but the value was sitting in an already-downloaded PDF (gov2023-24.pdf) "
              "the whole time, just in date-then-value word order none of the other patterns matched")
    section("CA", _ca)

    # A "Changelog sync" section (diffing the live website's published CSVs against git history
    # and a changelog.json disclosure file) existed in the working tree's copy of this gate --
    # removed here, not adapted: it's a live-website-build concern (did a public page's number
    # change without disclosure) that doesn't apply to this archive, where each release is its own
    # versioned, immutable snapshot and changes between releases are tracked in CHANGELOG.md
    # instead.

    print(f"\n{'PASSED' if not fails else 'FAILED'} — {len(fails)} failure(s)")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
