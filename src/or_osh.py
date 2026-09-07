"""OR extractor — Oregon State Hospital aid-and-assist (IST) waitlist, from the Mink-Bowman
court-monitor / neutral-expert (Pinals) reports. Dashboard tree.

DUPLICATED (2026-08-28) from code/pipeline/or_osh.py, not imported from it — the paper and
dashboard trees are kept deliberately independent (see dashboard/code/config.py's docstring). All
parsing logic below is identical to the paper's copy. Unlike WA, this extractor already globs
C.RAW/"or"/*.pdf directly — no frozen-vs-open-ended month window to duplicate; pointing this
tree's own config.py at dashboard_data/raw/or/ is the only thing that changes its behavior.
Re-sync by hand if the paper-side parser changes (do not import across trees at runtime).

Oregon = the 2nd clean FEDERAL 7-day-decree state (Disability Rights Oregon v. Mink,
3:02-cv-00339 D.Or.): OSH must admit aid-and-assist defendants within 7 DAYS. Directly
comparable to WA (decree-vs-decree, same admit-time logic). June-2025 contempt = $500/
class-member/day; Dr. Debra Pinals = neutral expert -> court monitor.

WHAT IS EXTRACTABLE (all PROSE/TABLE text — no chart-OCR needed):
  FLOW (monthly, decree-relevant):
    admits           = A&A patients admitted that month
    avg_wait_days    = avg days-to-admission for those ADMITTED that month
    pct_within_7day  = % of that month's admissions admitted within the 7-day decree
    orders_received  = new A&A restoration orders received that month (demand, Table 4)
  STOCK (as-of-1st-of-month snapshot, cross-validated across 4+ reports — Table 1 / Table 3):
    waitlist_stock          = # A&A on OSH admission list with signed order
    waitlist_stock_avg_days = avg days those people have currently been waiting
    census_aa / census_total= OSH census (A&A / all) bed occupancy
  Plus prose end-of-month waitlist_count (the original anchor metric; kept intact).

FLOW vs STOCK is kept STRICTLY separate: avg_wait_days (flow, for the admitted cohort) is
NOT the same as waitlist_stock_avg_days (snapshot wait of those still waiting). Likewise
waitlist_count (prose, END-of-month, e.g. Aug-2025=34) differs from waitlist_stock (Table-1
1st-of-month snapshot, e.g. 8/1/25=33) — both are honest, different timepoints.

NOTE: PLD-*.pdf are compliance ACTION PLANS (benchmark target dates, no measured wait data)
-> skipped. Long-trend "Figure" dashboards are chart IMAGES, but every number we use here
is also present as TEXT in Tables 1/3/4 + the narrative, so nothing is lost to OCR.

Files: dashboard_data/raw/or/*.pdf (oregon.gov/oha/OSH/reports/). Decree threshold = 7 days.

QUALITATIVE TRAJECTORY (directionally stable, re-derive exact figures from the parquet before
quoting any number): an early crisis period gave way to a period of much better compliance,
which was then followed by a renewed backslide under demand pressure and a subsequent contempt
sanction — i.e. this is a genuine CONTRAST/BACKSLIDING case, not a one-way improvement story
the way Washington is. The redesign brief's own requirement (§2, OR): preserve this volatility on
the dashboard chart — do not let any default view smooth it into a clean trend line.

Re-run:  python or_osh.py   (cwd = dashboard/code/)
"""
from __future__ import annotations
import re
from pathlib import Path
import pdfplumber, pandas as pd
import config as C
import _util

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
MON = {m: i + 1 for i, m in enumerate(MONTHS)}

def _period(month_year: str):
    m = re.match(r'(\w+)\s+(\d{4})', month_year.strip())
    if not m or m.group(1).lower() not in MON:
        return None
    return f"{int(m.group(2)):04d}-{MON[m.group(1).lower()]:02d}"

def _period_md(m: int, y: int):
    return f"{y:04d}-{m:02d}"

def _prior_period(named_month: str, ref_idx: int, ref_year: int):
    """Resolve a bare month name (e.g. 'March', 'July') referenced relative to an
    admit-statement at (ref_idx, ref_year): take the most recent occurrence of that
    month at or before the reference month."""
    nm = named_month.lower()
    if nm not in MON:
        return None
    idx = MON[nm]
    yr = ref_year if idx <= ref_idx else ref_year - 1
    return _period_md(idx, yr)

def _nums_run(tokens, n, want_float):
    """First maximal run of >=n numeric tokens (ints if want_float=False, decimals if True);
    returns (first n values, index the run STARTED at, index just past that run) or
    (None, -1, -1). The start index matters for page citation (see its callers): the totals
    and avgs runs in a Table 1 block can straddle a page break in a wide report, so citing
    both to the same fixed position (the section header, far above either run) can point a
    reader at the wrong physical page for whichever run landed on the later page -- an
    independent audit caught exactly this for the avgs run in one report. Citing each run to
    where IT actually starts fixes that regardless of which side of a page break either run
    falls on."""
    run, start = [], None
    for i, t in enumerate(tokens):
        s = t.strip().rstrip("*")
        ok = (re.fullmatch(r'\d+\.\d+', s) is not None) if want_float else (re.fullmatch(r'\d+', s) is not None)
        if ok:
            if start is None:
                start, run = i, []
            run.append(float(s))
        else:
            if start is not None and len(run) >= n:
                return run[:n], start, i
            start, run = None, []
    if start is not None and len(run) >= n:
        return run[:n], start, len(tokens)
    return None, -1, -1

# [.:] not just \. -- an independent audit found every "Table N: OSH Bed Capacities..." heading
# (the beds-table caption, in every one of the 13 reports that contribute beds rows) uses a
# colon, not a period. The period-only regex never matched any of them, so `_table_at()` fell
# back to the nearest PRECEDING period-punctuated heading -- always the actual waitlist table's
# "Table 1."/"Table 2." caption -- silently mislabeling every beds row's table_ref by one table
# number (confirmed: pdf_page was always correct, only the table number was wrong). Checked
# directly against the full corpus before widening this: every additional match the colon
# variant picks up is a genuine table caption ("Table 2: OSH Bed Capacities...", "Table 9:
# Provisional Findings...", "Table 12: Outcomes..."), not a false positive from prose.
TABLE_REF_RE = re.compile(r'Table\s+(\d+)[.:]')

def parse_report(path: Path) -> list[dict]:
    sha = _util.sha12(path)
    with pdfplumber.open(path) as pdf:
        page_texts = [re.sub(r'\s+', ' ', pg.extract_text() or "").strip() for pg in pdf.pages]
    # Every regex below matches against `flat`, a single whitespace-collapsed string joining
    # every page -- page boundaries are otherwise invisible to this extractor's own logic (all
    # of it predates page-citation and stays untouched). To add a page/table citation WITHOUT
    # touching any of that logic: collapse+strip each page's text individually, then join the
    # NON-EMPTY ones with exactly one space (a page pdfplumber returns nothing for -- a genuine
    # blank page, seen in some CA reports -- must be skipped entirely, not joined-as-empty, or
    # it contributes a doubled separator space that a global collapse would have removed; this
    # was caught by a byte-identity check failing on 2 of 9 California PDFs before being caught
    # here too). This is PROVABLY byte-identical to the original
    # `re.sub(r'\s+', ' ', " ".join(raw_page_texts))` (verified empirically across every real OR
    # PDF in this tree) -- whitespace at a page boundary always collapses to exactly one space
    # either way -- so every existing match position is unaffected, and page_starts below gives
    # an exact (not approximate) offset->page mapping for free.
    page_starts = []  # (char_offset, 1-indexed physical page) for each non-empty page
    _pos = 0
    _parts = []
    for i, t in enumerate(page_texts):
        if not t:
            continue
        page_starts.append((_pos, i + 1))
        _parts.append(t)
        _pos += len(t) + 1
    flat = " ".join(_parts)
    def _page_at(charpos):
        p = page_starts[0][1] if page_starts else 1
        for s, pagenum in page_starts:
            if s <= charpos:
                p = pagenum
            else:
                break
        return p
    table_positions = [(m.start(), m.group(1)) for m in TABLE_REF_RE.finditer(flat)]
    def _table_at(charpos):
        ref = None
        for pos_, num in table_positions:
            if pos_ <= charpos:
                ref = f"Table {num}"
            else:
                break
        return ref
    rows = []

    def add(period, metric, value, pos=None, cite_table=True):
        # cite_table=False for every narrative/prose-derived metric below: a "Table N" heading
        # positioned earlier in the document is NOT where a prose sentence's number came from --
        # the same real bug already caught and fixed for CA's prose_snapshot rows (ca_dsh.py),
        # confirmed here too by direct inspection (e.g. an "In November 2023, OSH admitted 108
        # A&A patients..." sentence sits nowhere near the "Table 4" heading _table_at() would
        # otherwise attach to it -- Table 4 is orders received, an unrelated series). Only the
        # four genuinely table-sourced blocks (STOCK Table 1, CENSUS Table 3, ORDERS Table 4,
        # CAPACITY Table 2) pass cite_table=True.
        if period and value is not None:
            rows.append(dict(state="OR", period=period, metric=metric, value=float(value),
                             report=path.name, source_sha=sha,
                             pdf_page=(_page_at(pos) if pos is not None else None),
                             table_ref=(_table_at(pos) if (pos is not None and cite_table) else None)))

    # ---------------- FLOW (narrative) ----------------
    # (A) canonical admit form (allow a parenthetical between 'patients' and 'with an average...')
    for m in re.finditer(r'In\s+(\w+\s+\d{4}),?\s+OSH admitted\s+(\d+)\s+A\s*&\s*A patients'
                         r'[^.]{0,90}?with an average wait time of\s+([\d.]+)\s+days', flat, re.I):
        p = _period(m.group(1))
        add(p, "admits", m.group(2), pos=m.start(), cite_table=False)
        add(p, "avg_wait_days", m.group(3), pos=m.start(), cite_table=False)

    # (A2) prior-month flow refs co-stated with an admit sentence. Resolve the year of the
    # bare prior-month name from the NEAREST "In <Month YYYY>, OSH admitted" statement.
    admit_stmts = [(a.start(), MON[a.group(1).lower()], int(a.group(2)))
                   for a in re.finditer(r'In\s+(\w+)\s+(\d{4}),?\s+OSH admitted', flat, re.I)
                   if a.group(1).lower() in MON]
    def _nearest_ref(pos):
        return min(admit_stmts, key=lambda s: abs(s[0] - pos)) if admit_stmts else None
    for pat in (r'\(down from\s+([\d.]+)\s+days in\s+(\w+)\)',          # "...(down from 25.4 days in March)"
                r'increased from\s+(\w+)\s+\(which was at\s+([\d.]+)\s+days\)'):  # "...from July (which was at 9.7 days)"
        for m in re.finditer(pat, flat, re.I):
            ref = _nearest_ref(m.start())
            if not ref:
                continue
            # group order differs between the two patterns -> detect which group is the month name
            g1, g2 = m.group(1), m.group(2)
            month, val = (g2, g1) if re.fullmatch(r'[\d.]+', g1) else (g1, g2)
            add(_prior_period(month, ref[1], ref[2]), "avg_wait_days", val, pos=m.start(), cite_table=False)

    # (B) prose END-of-month waitlist stock (the original anchor metric): "of <Month YYYY>, N people ... were on the waitlist"
    for m in re.finditer(r'(?:As of|of)\s+(\w+\s+\d{4}),?\s+(\d+)\s+(?:people|individuals)'
                         r'[^.]{0,60}?were on the waitlist', flat, re.I):
        add(_period(m.group(1)), "waitlist_count", m.group(2), pos=m.start(), cite_table=False)

    # (C) 7-day compliance form 1: "(N) of the T admissions in <Month> were within the 7-day"
    for m in re.finditer(r'\(?(\d+)\)?\s+of the\s+(\d+)\s+admissions in\s+(\w+)\s+'
                         r'were within the 7[- ]day', flat, re.I):
        within, total, mon = int(m.group(1)), int(m.group(2)), m.group(3).lower()
        for r in rows:
            if r["metric"] == "admits" and r["value"] == total and r["period"][5:7] == f"{MON.get(mon, 0):02d}":
                add(r["period"], "pct_within_7day", round(100 * within / total, 1), pos=m.start(), cite_table=False)
                break
    # (C2) 7-day compliance form 2 (9th report): "In <Month YYYY>, N of the T admissions were admitted within 7 days"
    for m in re.finditer(r'In\s+(\w+\s+\d{4}),\s+(\d+)\s+of the\s+(\d+)\s+admissions were admitted within 7 days',
                         flat, re.I):
        p = _period(m.group(1)); within, total = int(m.group(2)), int(m.group(3))
        add(p, "admits", total, pos=m.start(), cite_table=False)
        add(p, "pct_within_7day", round(100 * within / total, 1), pos=m.start(), cite_table=False)

    # ---------------- STOCK: Table 1 (A&A admission-list snapshot series) ----------------
    # scope to section 1 (A&A) only — section 2 is "found GEI" (excluded)
    aa = flat
    gi = re.search(r'Regarding individuals found GEI', flat, re.I)
    h1 = re.search(r'Regarding individuals on OSH admission list', flat, re.I)
    if h1:
        aa = flat[h1.end(): gi.start() if gi else len(flat)]
        toks = aa.split()
        # The column-date header is the LONGEST CONTIGUOUS run of M/D/YY tokens; isolated
        # footer dates (e.g. "9/5/25", "12/6/25") form runs of length 1 and are ignored.
        DATE_RE = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{2})$')
        best, cur = (None, -1), []
        for i, t in enumerate(toks):
            if DATE_RE.match(t):
                if not cur:
                    cur_start = i
                cur.append(DATE_RE.match(t).groups())
            else:
                if len(cur) > len(best[0] or []):
                    best = (cur, cur_start + len(cur))
                cur = []
        if len(cur) > len(best[0] or []):
            best = (cur, cur_start + len(cur))
        dates, after_idx = best
        if dates and len(dates) >= 8:
            ndt = len(dates)
            tail = toks[after_idx:]
            totals, t_start, j = _nums_run(tail, ndt, want_float=False)
            avgs, a_start, _ = (_nums_run(tail[j:], ndt, want_float=True) if j >= 0 else (None, -1, -1))
            dts = [(int(mm), int(_d), 2000 + int(yy)) for (mm, _d, yy) in dates]
            # Char offset (within `aa`, then `flat`) of each token in `toks`, computed from
            # `aa`'s own single-space-joined text (already whitespace-normalized upstream) --
            # lets each metric's numbers be cited to the page THEY actually landed on, not the
            # page the section header happened to be on.
            tok_offset = []
            _o = 0
            for t in toks:
                tok_offset.append(_o)
                _o += len(t) + 1
            def _tok_pos(idx):
                return h1.end() + tok_offset[idx] if 0 <= idx < len(tok_offset) else h1.end()
            totals_pos = _tok_pos(after_idx + t_start) if t_start >= 0 else h1.end()
            avgs_pos = _tok_pos(after_idx + j + a_start) if (j >= 0 and a_start >= 0) else h1.end()
            for met, vals, mpos in (("waitlist_stock", totals, totals_pos),
                                     ("waitlist_stock_avg_days", avgs, avgs_pos)):
                if not vals:
                    continue
                # collapse same-MONTH snapshots to the LATEST day (e.g. 1/28/22 = 93 over 1/5/22 = 46),
                # matching the single-value convention the later reports use for that month
                best = {}
                for (mm, dd, yy), v in zip(dts, vals):
                    per = _period_md(mm, yy)
                    if per not in best or dd > best[per][0]:
                        best[per] = (dd, v)
                for per, (dd, v) in best.items():
                    add(per, met, v, pos=mpos)

    # ---------------- STOCK: Table 3 (OSH census) ----------------
    # scope to Table 3 region ("OSH Census as of ..." up to the next Table) to avoid other
    # M/D/YYYY tables. Rows: "<M/D/YYYY> <A&A> <PSRB> <Civil> <Other> <Total>" (Total > A&A).
    cm = re.search(r'OSH Census as of', flat, re.I)
    if cm:
        nxt = re.search(r'Table\s*4', flat[cm.end():], re.I)
        region = flat[cm.end(): cm.end() + (nxt.start() if nxt else 4000)]
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', region):
            aa_n, total_n = int(m.group(4)), int(m.group(8))
            if total_n > aa_n:   # guard: real census rows have Total > A&A subset
                p = _period_md(int(m.group(1)), int(m.group(3)))
                abs_pos = cm.end() + m.start()   # region is a substring of flat -- translate back
                add(p, "census_aa", aa_n, pos=abs_pos)
                add(p, "census_psrb", int(m.group(5)), pos=abs_pos)
                add(p, "census_civil", int(m.group(6)), pos=abs_pos)
                add(p, "census_other", int(m.group(7)), pos=abs_pos)
                add(p, "census_total", total_n, pos=abs_pos)

    # ---------------- FLOW: Table 4 (A&A orders received) ----------------
    mname = "(?:" + "|".join(MONTHS) + ")"
    for m in re.finditer(rf'({mname})\s+(20\d\d)\s+(\d+)\s+\d+\s*\(', flat, re.I):
        add(_period(f"{m.group(1)} {m.group(2)}"), "orders_received", m.group(3), pos=m.start())

    # ---------------- CAPACITY: Table 2 (OSH bed capacities, as-of snapshot) ----------------
    for m in re.finditer(r'OSH Bed Capacities as of\s+(\d{1,2})/(\d{1,2})/(\d{2,4})\*?.{0,400}?OSH Total\s+(\d+)\s+(\d+)', flat, re.I):
        yy = m.group(3); yr = int(yy) if len(yy) == 4 else 2000 + int(yy)
        p = _period_md(int(m.group(1)), yr)
        add(p, "beds_licensed", int(m.group(4)), pos=m.start())
        add(p, "beds_active", int(m.group(5)), pos=m.start())

    # ---------------- ENFORCEMENT: contempt fines accrued (mapped to the report's census as-of month) ----------------
    mc = re.search(r'OSH Census as of\s+(\d{1,2})/\d{1,2}/(\d{2,4})', flat, re.I)
    if mc:
        yy = mc.group(2); asof = _period_md(int(mc.group(1)), int(yy) if len(yy) == 4 else 2000 + int(yy))
    else:
        asof = None
    for m in re.finditer(r'fines have accrued to approximately\s+\$?([\d.]+)\s*million', flat, re.I):
        add(asof, "contempt_fines_accrued_musd", float(m.group(1)), pos=m.start(), cite_table=False)

    # ---------------- FLOW recovery (C3): "Of the N admissions in <Month YYYY>, X% (Y people) ... within the 7-day" ----------------
    for m in re.finditer(r'Of the\s+(\d+)\s+admissions in\s+(\w+\s+\d{4}),?\s+([\d.]+)%\s+\(\d+\s+people\)\s+were admitted within the 7[- ]day', flat, re.I):
        p = _period(m.group(2))
        add(p, "admits", int(m.group(1)), pos=m.start(), cite_table=False)
        add(p, "pct_within_7day", float(m.group(3)), pos=m.start(), cite_table=False)

    return rows

def _report_rank(name):
    """Recency rank for date-aware dedup: dated court-monitor reports are the most recent /
    authoritative consolidated source; among neutral-expert reports, higher ordinal = more recent."""
    md = re.search(r'(20\d\d)\.(\d\d)\.(\d\d)', name)
    if md:
        return (2, int(md.group(1) + md.group(2) + md.group(3)))
    mo = re.search(r'_(\d+)(?:st|nd|rd|th)_Neutral', name, re.I)
    if mo:
        return (1, int(mo.group(1)))
    return (0, 0)

def build() -> pd.DataFrame:
    rows, prov = [], {}
    for p in sorted((C.RAW / "or").glob("*.pdf")):
        if "PLD" in p.name:           # PLD = compliance ACTION PLANS, not measured data
            continue
        rr = parse_report(p)
        # cross-report consistency: flag (don't silently drop) disagreements on shared (period,metric)
        for r in rr:
            k = (r["period"], r["metric"])
            if k in prov and abs(prov[k][0] - r["value"]) > 1e-6:
                print(f"  [conflict] {k}: {prov[k][0]} ({prov[k][1]}) vs {r['value']} ({p.name})")
            prov.setdefault(k, (r["value"], p.name))
        print(f"  [ok] {p.name}: {len(rr)} datapoints")
        rows += rr
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # date-aware dedup: keep the value from the MOST RECENT report (court-monitor > higher neutral
    # ordinal); ties (same report) break to later row order. Replaces the old keep-first-by-filename.
    df = df.reset_index().rename(columns={"index": "_i"})
    df["_r"] = df["report"].map(_report_rank)
    return (df.sort_values(["_r", "_i"])
              .drop_duplicates(["period", "metric"], keep="last")
              .drop(columns=["_i", "_r"])
              .sort_values(["metric", "period"]).reset_index(drop=True))

if __name__ == "__main__":
    df = build()
    out = C.DERIVED / "or_osh_dashboard.parquet"
    df.to_parquet(out, index=False)
    print(f"\nsaved {out} ({len(df)} rows)\n")
    with pd.option_context("display.max_rows", None):
        print(df.to_string(index=False))

    print("\n=== SERIES COVERAGE ===")
    for met in sorted(df.metric.unique()):
        s = df[df.metric == met]
        print(f"  {met:24s} n={len(s):2d}  span {s.period.min()}..{s.period.max()}")
