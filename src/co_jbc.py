"""CO extractor — Layer 1: JBC legislative-PDF dated snapshots (the guaranteed annual spine).

CO data is born-digital TEXT but PROSE (dated figures embedded in narrative), not repeating
tables. So we mine reliable dated patterns: waitlist count "as of <date>", average wait days,
and consent-decree fines by fiscal year. Sparse but real + validated. The RICH monthly
Tier-1/Tier-2 series lives in the special-master reports (Layer 2 = `co_special_master.py`, a
semi-structured stitch — files already downloaded to data/raw/co/sm_*.pdf, format confirmed).

CO decree thresholds: Tier-1 inpatient restoration <=7 days,
Tier-2 <=28 days (later 49/42 in monitor reports); inpatient eval <=14 days, jail eval <=21.
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

def _date_to_period(mname: str, day: str, year: str) -> str:
    return f"{int(year):04d}-{MON[mname.lower()]:02d}"

def parse_jbc(path: Path) -> list[dict]:
    sha = _util.sha12(path)
    with pdfplumber.open(path) as pdf:
        page_texts = [re.sub(r'\s+', ' ', pg.extract_text() or "").strip() for pg in pdf.pages]
    # Page citation, built from the SAME whitespace-collapsed text every regex below matches
    # against. Collapsing+stripping each page individually, then joining only the NON-EMPTY
    # ones with a single space, is PROVABLE byte-identical to the original
    # `re.sub(r'\s+', ' ', " ".join(raw_page_texts))` (verified empirically across every raw CO
    # PDF in this tree, JBC and special-master alike) -- a genuine blank page must be skipped
    # entirely, not joined-as-empty, or it contributes a doubled separator space a global
    # collapse would have removed. No table_ref here: this docstring's own claim (CO's JBC
    # figures are PROSE, not repeating tables) checks out against the raw text -- these
    # documents' own "Table N" headings (when present at all, e.g. fy2024-25_humbrf2.5.pdf)
    # are unrelated appropriations tables, not the source of any value extracted below, so a
    # table citation here would be as misleading as it was for CA's prose_snapshot rows.
    page_starts, pos, parts = [], 0, []
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
    rows = []

    # (1) dated waitlist count: "<N> individuals are on the waitlist ... as of <Month DD, YYYY>"
    for m in re.finditer(r'(\d{2,4})\s+individuals?\s+are\s+on\s+the\s+waitlist[^.]*?as of\s+'
                         r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
                         flat, re.I):
        rows.append(dict(state="CO", period=_date_to_period(m.group(2), m.group(3), m.group(4)),
                         metric="restoration_waitlist_count", value=float(m.group(1)),
                         as_of=f"{m.group(2)} {m.group(3)}, {m.group(4)}",
                         source=path.name, source_sha=sha, pdf_page=_page_at(m.start())))

    # (2) average time on waitlist: "Average time on the waitlist is <lo>-<hi> days"
    for m in re.finditer(r'average time on the waitlist is\s+(\d+)\s*-\s*(\d+)\s+days', flat, re.I):
        rows.append(dict(state="CO", period=None, metric="avg_wait_days_restoration",
                         value=(float(m.group(1)) + float(m.group(2))) / 2,
                         as_of=f"{m.group(1)}-{m.group(2)} day range", source=path.name, source_sha=sha,
                         pdf_page=_page_at(m.start())))

    # (3) consent-decree fines, capped, by FY: "capped to $<X> million ... in FY <YYYY-YY>"
    for m in re.finditer(r'capped to \$?([\d.]+)\s*million[^.]*?FY\s*(\d{4}-\d{2})', flat, re.I):
        rows.append(dict(state="CO", period=m.group(2), metric="decree_fines_capped_$M",
                         value=float(m.group(1)), as_of=f"FY{m.group(2)}", source=path.name, source_sha=sha,
                         pdf_page=_page_at(m.start())))
    # uncapped estimate: "would have totaled $<X> million in FY <YYYY-YY>"
    for m in re.finditer(r'would have totaled \$?([\d.]+)\s*million[^.]*?FY\s*(\d{4}-\d{2})', flat, re.I):
        rows.append(dict(state="CO", period=m.group(2), metric="decree_fines_uncapped_est_$M",
                         value=float(m.group(1)), as_of=f"FY{m.group(2)}", source=path.name, source_sha=sha,
                         pdf_page=_page_at(m.start())))
    return rows

def build() -> pd.DataFrame:
    rows = []
    for p in sorted((C.RAW / "co").glob("*.pdf")):
        if p.name.startswith("sm_"):  # special-master reports = Layer 2, not here
            continue
        rr = parse_jbc(p)
        print(f"  [ok] {p.name}: {len(rr)} dated figures")
        rows += rr
    df = pd.DataFrame(rows).drop_duplicates(subset=["metric", "value", "as_of"])
    return df

if __name__ == "__main__":
    df = build()
    out = C.DERIVED / "co_jbc_snapshots.parquet"
    df.to_parquet(out, index=False)
    print(f"\nsaved {out} ({len(df)} rows)\n")
    print(df.sort_values(["metric", "period"]).to_string(index=False))
    # validate against known anchors
    print("\n=== ANCHOR CHECKS ===")
    wl = df[(df.metric == "restoration_waitlist_count")]
    fines = df[df.metric == "decree_fines_capped_$M"]
    c1 = (wl["value"] == 431).any() or (wl["value"] == 391).any()
    c2 = (df.metric == "avg_wait_days_restoration").any() and df[df.metric == "avg_wait_days_restoration"]["value"].between(100, 120).any()
    c3 = (fines["value"] == 12.0).any()
    print(f"  waitlist count anchor (431 or 391): {'PASS' if c1 else 'FAIL'}")
    print(f"  avg-wait ~105-115 days anchor:      {'PASS' if c2 else 'FAIL'}")
    print(f"  fines $12.0M cap anchor:            {'PASS' if c3 else 'FAIL'}")
    print(f"  OVERALL: {'PASS' if (c1 and c2 and c3) else 'NEEDS REVIEW'}")
