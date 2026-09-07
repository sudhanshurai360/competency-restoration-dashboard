"""CA extractor — California DSH IST pending-placement waitlist, from DSH budget Estimate PDFs.

CA decree: *Stiavetti v. Clendenin* — commence restoration within 28 DAYS (phased 60->45->33->28).
DSH publishes the IST pending-placement waitlist (STOCK, like TX) in its semiannual budget
"Estimate" PDFs (Governor's Budget ~Jan + May Revision ~May), as (a) a clean annual FY table
[IST System-wide Pending Placement List, as-of June 30] and (b) dated prose snapshots
("1,953 ... as of January 2022; down to 397 as of May 6, 2024"). Born-digital TEXT, no charts.
Wait-days/28-day-compliance live in Stiavetti court reports (enrichment, not here).
Files: data/raw/ca/*.pdf (DSH hub; Wayback id_ fallback for the blocked server).
"""
from __future__ import annotations
import re
from pathlib import Path
import pdfplumber, pandas as pd
import config as C
import _util

MON = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}

def _num(s): return int(s.replace(",", ""))
def _month_period(mname, year): return f"{int(year):04d}-{MON[mname.lower()]:02d}"
def _fy_to_period(fy):  # "2018-19" -> as-of June 30 of the end year -> 2019-06
    end = int(fy[:2] + fy[-2:])
    return f"{end:04d}-06"

TABLE_REF_RE = re.compile(r'Table\s+(\d+)[.:]')

def parse_estimate(path: Path) -> list[dict]:
    sha = _util.sha12(path)
    with pdfplumber.open(path) as pdf:
        page_texts = [re.sub(r'\s+', ' ', pg.extract_text() or "").strip() for pg in pdf.pages]
    # Page/table citation, built from the SAME whitespace-collapsed text every regex below
    # matches against. Collapsing+stripping each page individually, then joining only the
    # NON-EMPTY ones with a single space, is PROVABLE byte-identical to the original
    # `re.sub(r'\s+', ' ', " ".join(raw_page_texts))` (verified empirically across all 9 raw CA
    # PDFs) -- a genuine blank page (2 of these 9 budget PDFs have any: may2024-25.pdf has 1,
    # gov2025-26.pdf has 8) must be skipped entirely, not joined-as-empty, or it contributes a
    # doubled separator space a global
    # collapse would have removed. Every existing match position is unaffected either way, and
    # page_starts gives an exact (not approximate) offset->page mapping for free.
    page_starts, pos, parts = [], 0, []  # (char_offset, 1-indexed physical page) per non-empty page
    for i, t in enumerate(page_texts):
        if not t:
            continue
        page_starts.append((pos, i + 1))
        parts.append(t)
        pos += len(t) + 1
    flat = " ".join(parts)
    def _page_at(charpos):
        p = page_starts[0][1] if page_starts else 1
        for s, pagenum in page_starts:
            if s <= charpos: p = pagenum
            else: break
        return p
    table_positions = [(m.start(), m.group(1)) for m in TABLE_REF_RE.finditer(flat)]
    def _table_at(charpos):
        ref = None
        for pos_, num in table_positions:
            if pos_ <= charpos: ref = f"Table {num}"
            else: break
        return ref
    rows = []
    def add(period, value, kind, pos=None, cite_table=True):
        # cite_table=False for prose_snapshot rows: a "Table N" heading positioned earlier on
        # the same page as a prose sentence is NOT where that sentence's number came from --
        # confirmed directly (may2024-25.pdf p.14 has both "Table 3: Patient Census" AND, in
        # unrelated prose elsewhere on the same page, "397 as of May 6, 2024" -- attributing
        # the prose figure to Table 3 would be a real, false precision claim, not a citation).
        # The page number is still accurate and useful; only the table label is suppressed.
        if period:
            rows.append(dict(state="CA", period=period, metric="ist_pending_placement", value=float(value),
                             kind=kind, report=path.name, source_sha=sha,
                             pdf_page=(_page_at(pos) if pos is not None else None),
                             table_ref=(_table_at(pos) if (pos is not None and cite_table) else None)))

    # (1) the IST annual FY table: "...Pending 2018-19 2019-20 ... Placement 849 1,212 1,454 1,779 894 ..."
    m = re.search(r'IST System-wide Pending Placement List(.{0,250})', flat, re.I)
    if m:
        seg = m.group(1)
        fys = re.findall(r'20\d\d-\d\d', seg)                       # the FY column headers
        vm = re.search(r'\bPlacement\s+([\d,]+(?:\s+[\d,]+)+)', seg)  # the data row right after "Placement"
        if fys and vm:
            vals = re.findall(r'[\d,]+', vm.group(1))
            for fy, v in zip(fys, vals):
                add(_fy_to_period(fy), _num(v), "annual_fy_table", pos=m.start())

    # (2) dated prose snapshots
    for m in re.finditer(r'([\d,]{3,5})\s+IST patients on the pending placement list as of\s+(\w+)\s+(\d{4})', flat, re.I):
        add(_month_period(m.group(2), m.group(3)), _num(m.group(1)), "prose_snapshot", pos=m.start(), cite_table=False)
    for m in re.finditer(r'down to\s+([\d,]{3,5})\s+as of\s+(\w+)\s+\d{1,2},?\s+(\d{4})', flat, re.I):
        add(_month_period(m.group(2), m.group(3)), _num(m.group(1)), "prose_snapshot", pos=m.start(), cite_table=False)
    # date-then-value order (the reverse of the "down to <value> as of <date>" pattern above) --
    # e.g. gov2023-24.pdf: "As of December 12, 2022, the waitlist has declined to 1,473." This
    # value was confirmed present verbatim in an already-downloaded raw PDF but silently
    # uncaptured by every other pattern here (all value-then-date, or date-only with a different
    # verb) -- closes a real extraction gap, not a newly-sourced document. `[^.]*?` (not `.*?`)
    # between the date and "declined to" is load-bearing: some of these budget PDFs also contain
    # long runs of unrelated "As of <Month> <day>, <year>, ..." sentences elsewhere on the page
    # (e.g. per-month appendix entries) with no "declined to" of their own -- a plain `.*?` walks
    # straight past several of those to steal THIS sentence's "declined to 1,473" and misdate it
    # to an unrelated earlier month; confirmed as a real false match on gov2023-24.pdf before
    # this fix. Bounding to "no period crossed" keeps the match inside one sentence.
    for m in re.finditer(r'As of\s+(\w+)\s+\d{1,2},?\s+(\d{4}),[^.]*?declined to\s+([\d,]{3,5})', flat, re.I):
        add(_month_period(m.group(1), m.group(2)), _num(m.group(3)), "prose_snapshot", pos=m.start(), cite_table=False)
    for m in re.finditer(r'([\d,]{3,5})\s+individuals pending placement[^.]*?in\s+(\w+)\s+(\d{4})', flat, re.I):
        add(_month_period(m.group(2), m.group(3)), _num(m.group(1)), "prose_snapshot", pos=m.start(), cite_table=False)
    for m in re.finditer(r'(?:there are|there were)\s+([\d,]{3,5})\s*\d*\s+individuals on the waitlist', flat, re.I):
        pass  # report-relative ("As of the 2024-25 May Revision") — skip (no clean date)
    for m in re.finditer(r"now down to\s+([\d,]{3,5})\s+as of\s+20\d\d-\d\d\s+(?:Governor.s Budget|May Revision)",
                          flat, re.I):
        pass  # SAME report-relative problem, different phrasing -- a second independent audit
              # (2026-09-07) confirmed both of the two newest raw PDFs contain this sentence
              # ("...is now down to 275 as of 2026-27 Governor's Budget", gov2026-27.pdf; "...256
              # as of 2026-27 May Revision", may2026-27.pdf), each textually more recent than the
              # shipped "latest reading" -- deliberately still skipped rather than guess a
              # calendar month from a budget-cycle label (a "Governor's Budget" is typically
              # published in January, a "May Revision" in May, of the FIRST year in the "20XX-YY"
              # label, but that's an inference this pipeline isn't willing to assert as a sourced
              # date). This regex exists only to make the skip explicit and grep-able, same as
              # the one above; disclosed on california.html rather than left silent.
    # Four more prose phrasings, found by an independent audit that specifically hunted for
    # extraction-COVERAGE gaps (as opposed to wrong-value bugs): all 9 raw PDFs already sitting
    # in data/raw/ca/ contain 8 more genuine, unambiguous, dated readings that none of
    # the patterns above matched -- confirmed directly against the source text, not guessed.
    # Each addition below was corpus-tested for false positives before being added (see this
    # commit's message); the "IST"/"waitlist" context guards are load-bearing, not decorative --
    # an unguarded version of the FY-comparison pattern below also matched an unrelated "LPS
    # census" sentence with the exact same "from X patients in <month> to Y patients in <month>"
    # shape in gov2024-25.pdf, which would have silently mixed a different population into this
    # series.
    for m in re.finditer(r'waitlist[^.]*?to\s+([\d,]{3,5})\s+as of\s+(\w+)\s+\d{1,2},?\s+(\d{4})', flat, re.I):
        add(_month_period(m.group(2), m.group(3)), _num(m.group(1)), "prose_snapshot", pos=m.start(), cite_table=False)
    for m in re.finditer(r'([\d,]{3,5})\s+patients\s+pending placement\s+as of\s+(\w+)\s+\d{1,2},?\s+(\d{4})', flat, re.I):
        add(_month_period(m.group(2), m.group(3)), _num(m.group(1)), "prose_snapshot", pos=m.start(), cite_table=False)
    for m in re.finditer(r'in\s+(\w+)\s+(\d{4}),\s+DSH had\s+([\d,]{3,5})\s+individuals\s+pending placement', flat, re.I):
        add(_month_period(m.group(1), m.group(2)), _num(m.group(3)), "prose_snapshot", pos=m.start(), cite_table=False)
    for m in re.finditer(r'IST[^.]*?from\s+([\d,]{3,5})\s+patients\s+in\s+(\w+)\s+(\d{4})\s+to\s+([\d,]{3,5})\s+patients\s+in\s+(\w+)\s+(\d{4})', flat, re.I):
        add(_month_period(m.group(2), m.group(3)), _num(m.group(1)), "prose_snapshot", pos=m.start(), cite_table=False)
        add(_month_period(m.group(5), m.group(6)), _num(m.group(4)), "prose_snapshot", pos=m.start(), cite_table=False)
    return rows

def _report_chrono_key(name):
    # An independent audit found the dedup tie-break below used to sort by the raw filename
    # STRING ("gov2026-27.pdf" < "may2025-26.pdf" alphabetically, even though the Jan-2026
    # Governor's Budget is chronologically NEWER than the May-2025 Revision) -- confirmed inert
    # against the current corpus (no period has ever had two reports disagree on its value), but
    # a real latent bug: a future restated figure could silently prefer the wrong report. "gov"
    # (~January) sorts before "may" (~May) of the SAME fiscal-year label; the fiscal-year's own
    # start year is the primary sort key.
    m = re.match(r'(gov|may)(\d{4})-\d{2}\.pdf$', name)
    if not m:
        return (0, 0)
    return (int(m.group(2)), 0 if m.group(1) == "gov" else 1)

def build() -> pd.DataFrame:
    rows = []
    for p in sorted((C.RAW / "ca").glob("*.pdf")):
        rr = parse_estimate(p)
        print(f"  [ok] {p.name}: {len(rr)} datapoints")
        rows += rr
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # prefer dated prose snapshot over the annual table where both exist for a period; else latest report
    df["pri"] = (df["kind"] == "prose_snapshot").astype(int)
    df["_chrono"] = df["report"].map(_report_chrono_key)
    return (df.sort_values(["pri", "_chrono"]).drop_duplicates(["period"], keep="last")
              .drop(columns=["pri", "_chrono"]).sort_values("period"))

if __name__ == "__main__":
    df = build()
    out = C.DERIVED / "ca_dsh.parquet"
    df.to_parquet(out, index=False)
    print(f"\nsaved {out} ({len(df)} rows)\n")
    print(df[["state", "period", "value", "kind", "report"]].to_string(index=False))
    print("\n=== ANCHOR CHECKS ===")
    by = df.set_index("period")["value"].to_dict()
    c1 = by.get("2022-01") == 1953
    c2 = by.get("2024-05") == 397
    c3 = df["value"].isin([849, 1212, 1454, 1779]).sum() >= 2   # annual table values present
    print(f"  peak 1,953 as of Jan 2022:  {'PASS' if c1 else 'FAIL'} (got {by.get('2022-01')})")
    print(f"  397 as of May 2024:         {'PASS' if c2 else 'FAIL'} (got {by.get('2024-05')})")
    print(f"  annual FY table values:     {'PASS' if c3 else 'FAIL'}")
    print(f"  OVERALL: {'PASS' if (c1 and c2 and c3) else 'NEEDS REVIEW'}")
