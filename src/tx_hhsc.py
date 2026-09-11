"""TX HHSC forensic-waitlist extractor (Competency Restoration Observatory — second state).

Source A: HHSC "Reporting of Waiting Lists for Mental Health Services" (Rider 45/50),
filed ~May 1 & Nov 1. Each report's Tables 5 (Non-Max) & 6 (Max Security Forensic
State Hospital Bed Waiting List) give TWO fiscal quarters x {waitlist stock count,
avg days on list}. TX fiscal year = Sep..Aug; May report = Q1&Q2, Nov report = Q3&Q4.

TX gives the waitlist-STOCK metric (complements WA's wait-TIME/compliance flow).
No binding deadline (litigation dismissed, deadline bills rejected) -> 'no-decree' state.

Server hard-403s scripted fetch; PDFs are pulled from the Wayback Machine `id_`
raw-file form (also better for reproducibility). Files live in data/raw/tx/.
"""
from __future__ import annotations
import re
from pathlib import Path
import pdfplumber, pandas as pd
import config as C
import _util

QWORD = {"one": 1, "two": 2, "three": 3, "four": 4}
# TX FY quarter -> approximate calendar quarter-end (FY starts Sep). Q1=Nov,Q2=Feb,Q3=May,Q4=Aug.
FQ_END = {1: "11", 2: "02", 3: "05", 4: "08"}

def _fy_quarter_to_period(fy: int, q: int) -> str:
    # TX FY starts Sep. Q1 ends Nov of (fy-1); Q2 Feb, Q3 May, Q4 Aug of fy.
    cal_year = fy - 1 if q == 1 else fy
    return f"{cal_year}-{FQ_END[q]}"

def _nums(s: str):
    return [float(x) if "." in x else int(x)
            for x in re.findall(r'[\d,]+(?:\.\d+)?', s.replace(",", "")) if x.strip(".")]

def _emit(rows, periods, level, counts, days, name, sha, count_pos=None, days_pos=None,
          page_at=None, table_at=None):
    # count and days can come from two DIFFERENT tables (confirmed: Table 10 vs 12 for max,
    # Table 7 vs 9 for non-max, in every 2024+ report) -- one row, two independently-sourced
    # values. A previous version cited only the count's position for the whole row (a real
    # readability/precision loss: hovering over the days figure would show the count's table
    # number, not its own) -- now both get their own citation. `pdf_page`/`table_ref` keep
    # their original meaning (the count's source, falling back to the days source if count
    # has none, same as before) so nothing downstream that already reads those two columns
    # needs to change; `pdf_page_days`/`table_ref_days` are new, additive, null only when no
    # days value exists for that row at all -- for old-format rows where count and days
    # genuinely share one table, both citation pairs simply agree, which is correct, not
    # redundant.
    for i, per in enumerate(periods):
        c = counts[i] if counts and i < len(counts) else None
        d = days[i] if days and i < len(days) else None
        if c is None and d is None: continue
        primary_pos = count_pos if count_pos is not None else days_pos
        rows.append(dict(state="TX", period=per, security_level=level,
                         waitlist_count=c, avg_wait_days=d,
                         report=name, source="wayback:hhs.texas.gov", source_sha=sha,
                         pdf_page=(page_at(primary_pos) if primary_pos is not None and page_at else None),
                         table_ref=(table_at(primary_pos) if primary_pos is not None and table_at else None),
                         pdf_page_days=(page_at(days_pos) if days_pos is not None and page_at else None),
                         table_ref_days=(table_at(days_pos) if days_pos is not None and table_at else None)))

def _parse_old(text, name, sha, page_at=None, table_at=None):
    """2023-era: Tables 5 (non-max) & 6 (max), 'People on the Waiting List' + avg days, 2 quarters."""
    m = re.search(r'fiscal year (\d{4}),?\s+quarters?\s+(\w+)\s+and\s+(\w+)', text, re.I)
    if not m: return []
    fy = int(m.group(1)); periods = [_fy_quarter_to_period(fy, QWORD[m.group(2).lower()]),
                                     _fy_quarter_to_period(fy, QWORD[m.group(3).lower()])]
    flat = re.sub(r'\s+', ' ', text); rows = []
    for lab, nxt, level in [("Table 5", "Table 6", "non_max"), ("Table 6", "Table 7", "max")]:
        lab_pos = flat.find(lab)
        if lab_pos < 0: continue
        body_start = lab_pos + len(lab)
        nxt_pos = flat.find(nxt, body_start)
        body = flat[body_start: nxt_pos if nxt_pos >= 0 else len(flat)]
        # "Waiting List" (two words) and "Waitlist" (one word) both appear across report
        # vintages of this SAME table (confirmed: mhs-waiting-lists-may-2023.pdf uses
        # "People on the Waitlist" throughout, while mhs-waiting-lists-nov-2023.pdf -- filed
        # the same fiscal year -- uses "Waiting List") -- the single-word form silently
        # produced 0 rows for 3 of 6 downloaded reports, permanently dropping FY2023 Q1/Q2
        # (Nov 2022/Feb 2023) since no other report covers those months.
        stock = re.search(r'People on the Wait\s*(?:ing\s*)?[Ll]ist\s+([\d,]+)\s+([\d,]+)', body)
        days = re.search(r'Remained on the Wait\s*(?:ing\s*)?[Ll]ist\s+([\d,]+)\s+([\d,]+)', body)
        if not stock: continue
        _emit(rows, periods, level, _nums(stock.group(0))[-2:],
              _nums(days.group(0))[-2:] if days else None, name, sha,
              count_pos=body_start + stock.start(),
              days_pos=(body_start + days.start()) if days else None,
              page_at=page_at, table_at=table_at)
    return rows

def _parse_new(text, name, sha, page_at=None, table_at=None):
    """2024+-era: Tables 7/10 (counts) & 9/12 (avg days) by facility, 'FY YY Qn' columns (4 quarters).
    MSU = single 'Maximum Security' row; non-MSU = 'Statewide'/'Total' row if present."""
    flat = re.sub(r'\s+', ' ', text)
    fym = re.search(r'FY\s*(\d{2})\s*Q1', flat)
    if not fym: return []
    fy = 2000 + int(fym.group(1)); periods = [_fy_quarter_to_period(fy, q) for q in (1, 2, 3, 4)]
    rows = []
    NUM4 = r'((?:\s+[\d,]+(?:\.\d+)?){4})'
    def grab(tbl_label, nxt_label, row_re, valid=lambda vals: True):
        """Try every occurrence of tbl_label in the doc, in order, returning the first whose
        body matches row_re AND passes `valid`. A later report vintage (2025-11) added a "List
        of Tables" table-of-contents section whose entries (e.g. "Table 7.2.") also match a
        naive `tbl_label in flat` substring check as the FIRST occurrence -- a plain single-shot
        .split() then grabs the TOC snippet instead of the real section. Trying each occurrence
        in turn fixes the obvious case, but the TOC region can ALSO contain an unrelated small
        table whose row happens to match row_re (seen: a stray "Total 0 0 0 0" from a different
        table sharing the TOC's span) -- `valid` lets a caller reject an implausible match (e.g.
        all-zero) and keep searching later occurrences, instead of committing to the first
        syntactic match found.

        Returns (vals, abs_pos) -- abs_pos is the match's own offset in `flat`, for page/table
        citation; (None, None) on no match."""
        for m0 in re.finditer(re.escape(tbl_label), flat):
            rest = flat[m0.end():]
            nxt_pos = rest.find(nxt_label)
            body = rest[:nxt_pos] if nxt_pos >= 0 else rest
            m = re.search(row_re, body)
            if m:
                vals = _nums(m.group(0))[-4:]
                if valid(vals):
                    return vals, m0.end() + m.start()
        return None, None
    def nz(vals):  # statewide waitlist STOCK of 0 is implausible -> treat as parse miss
        return [None if (v == 0) else v for v in vals] if vals else vals
    _not_all_zero = lambda vals: bool(vals) and any(v not in (0, None) for v in vals)
    # Row labels sometimes carry a footnote-marker digit glued directly on with no space
    # (e.g. "Maximum Security17" in the 2025-11 report) -- \d{0,2} tolerates 0-2 such digits
    # without risking eating real data (NUM4 itself requires leading whitespace before a number).
    MSU_LBL = r'Maximum Security\d{0,2}'
    # Case-INSENSITIVE (scoped inline flag, not a global re.I -- MSU_LBL above stays exact-case
    # on purpose): the row label varies by report vintage between "Total", "TOTAL", and
    # "Statewide" -- mhs-waiting-lists-nov-2024.pdf's Table 7 uses all-caps "TOTAL", which an
    # exact-case "Total" never matched, silently dropping that report's entire non_max series
    # (FY24 Q1-Q4) even though the row was right there in the table.
    SW_LBL = r'(?i:Statewide|Total)\d{0,2}'
    # MSU (maximum security) waitlist COUNT — use Table 10's "Total" row, not the "Maximum
    # Security" bucket row. FIXED 2026-09-11: an independent multi-pass data audit (see
    # meta/docs/data_validation_2026-09-11/tx_pass1_findings.md) found the previous version
    # pulled MSU_LBL here, which is only the not-yet-facility-assigned subset of the true MSU
    # waitlist (Kerrville/Rusk/Vernon/Wichita Falls facility-assigned people, who are still
    # waiting, were excluded) -- understated the true count by 5-16% across every 2024+ report
    # (e.g. 419 vs. the real 484 for nov-2025.pdf FY25 Q4, confirmed directly against the PDF).
    # Table 10's "Total" row is the genuine full MSU waitlist -- unassigned bucket + facility-
    # assigned-but-still-waiting -- and is what `waitlist_count` for security_level="max" is
    # actually supposed to represent. valid=_not_all_zero closes the same TOC-false-positive
    # edge as the non-MSU grabs below (untriggered so far in any real document checked, but
    # there's no structural reason a future report vintage couldn't put an all-zero "Total"
    # match earlier in the doc).
    msu_ct, msu_ct_pos = grab("Table 10", "Table 11", SW_LBL + NUM4, valid=_not_all_zero)
    # Table 12's own "Maximum Security" row is EITHER absent entirely (nov-2024.pdf) or present
    # and explicitly all-zero, footnoted "Maximum Security is not a physical location... people
    # do not directly admit from the maximum security list" (nov-2025.pdf, footnote 18) --
    # HHSC does not measure a wait-days figure for this population at all in the 2024+ format.
    # A previous version of this code fell back to Table 12's SW_LBL ("Statewide"/"Total") row
    # when the MSU row failed -- but that row is the average across the small set of
    # ALREADY-FACILITY-ASSIGNED patients (Kerrville/Rusk/Vernon/Wichita Falls), a genuinely
    # different, much smaller population than the `msu_ct` statewide unassigned queue this row's
    # count describes (419 vs. ~65 people, confirmed directly against mhs-waiting-lists-
    # nov-2025.pdf Table 12) -- silently pairing the two produced a real, live bug: a count and
    # a days figure on the same CSV row describing two different groups of people. Left as a
    # genuine, disclosed gap instead of a population mismatch -- do not add this fallback back
    # without also fixing how the two figures are labeled/scoped on the dashboard page.
    msu_dy, msu_dy_pos = grab("Table 12", "Acronyms", MSU_LBL + NUM4, valid=_not_all_zero)
    # count and days come from two DIFFERENT tables -- each gets its own citation now (see
    # _emit()'s docstring comment); no more relying on the fixed table-number offset (10->12,
    # 7->9) that used to stand in for a real second citation.
    _emit(rows, periods, "max", nz(msu_ct), msu_dy, name, sha,
          count_pos=msu_ct_pos, days_pos=msu_dy_pos, page_at=page_at, table_at=table_at)
    # non-MSU — prefer a Statewide/Total row (counts only if plausible)
    nm_ct, nm_ct_pos = grab("Table 7", "Table 8", SW_LBL + NUM4, valid=_not_all_zero)
    nm_dy, nm_dy_pos = grab("Table 9", "Table 10", SW_LBL + NUM4, valid=_not_all_zero)
    if nm_ct or nm_dy:
        _emit(rows, periods, "non_max", nz(nm_ct), nm_dy, name, sha,
              count_pos=nm_ct_pos, days_pos=nm_dy_pos, page_at=page_at, table_at=table_at)
    return rows

TABLE_REF_RE = re.compile(r'Table\s+(\d+)\.')

def _page_table_index(pdf):
    r"""Page/table position index for citation, built from the SAME whitespace-collapsed text
    every parse_* function already works on. Collapsing+stripping each page individually, then
    joining only the NON-EMPTY ones with a single space, is PROVABLE byte-identical to this
    file's own `re.sub(r'\s+', ' ', text)` step (verified empirically against all 6 raw TX PDFs
    too) -- every existing regex position is unaffected, and it gives an exact offset->page
    mapping. Skipping empty pages specifically matters: a genuine blank page (pdfplumber returns
    "" for it) would otherwise contribute a doubled separator space that a global collapse would
    have removed -- caught by a byte-identity check failing on 2 of 9 California PDFs, fixed
    there and applied here too since the same edge case can occur in any report vintage."""
    page_texts = [re.sub(r'\s+', ' ', pg.extract_text() or "").strip() for pg in pdf.pages]
    page_starts, pos, parts = [], 0, []  # (char_offset, 1-indexed physical page) per non-empty page
    for i, t in enumerate(page_texts):
        if not t:
            continue
        page_starts.append((pos, i + 1))
        parts.append(t)
        pos += len(t) + 1
    text = " ".join(parts)
    def page_at(charpos):
        p = page_starts[0][1] if page_starts else 1
        for s, pagenum in page_starts:
            if s <= charpos: p = pagenum
            else: break
        return p
    table_positions = [(m.start(), m.group(1)) for m in TABLE_REF_RE.finditer(text)]
    def table_at(charpos):
        ref = None
        for pos_, num in table_positions:
            if pos_ <= charpos: ref = f"Table {num}"
            else: break
        return ref
    return text, page_at, table_at

def parse_report(path: Path) -> list[dict]:
    sha = _util.sha12(path)
    with pdfplumber.open(path) as pdf:
        text, page_at, table_at = _page_table_index(pdf)
    # era detection: 2024+ uses "Table 10. Number of People on MSU"; 2023 uses "Table 6. ... Maximum Security"
    new = bool(re.search(r'Table 10\.\s*Number of People on MSU', text, re.I)) or "FY 24 Q1" in text or "FY 25 Q1" in text
    rows = (_parse_new(text, path.name, sha, page_at, table_at) if new
            else _parse_old(text, path.name, sha, page_at, table_at))
    if not rows:
        print(f"    [warn] {path.name}: 0 rows (era={'new' if new else 'old'})")
    return rows

def build_panel() -> pd.DataFrame:
    rows = []
    for p in sorted((C.RAW / "tx").glob("mhs-waiting-lists-*.pdf")):
        rr = parse_report(p)
        print(f"  [ok] {p.name}: {len(rr)} rows")
        rows += rr
    df = pd.DataFrame(rows)
    if df.empty: return df
    # overlapping reports may repeat a quarter -> keep latest report's value
    df["rep"] = df["report"].str.extract(r'(may|nov)-(\d{4})').apply(
        lambda r: f"{r[1]}-{'05' if r[0]=='may' else '11'}", axis=1)
    df = (df.sort_values("rep")
            .drop_duplicates(["state", "security_level", "period"], keep="last")
            .drop(columns="rep").sort_values(["security_level", "period"]))
    return df

if __name__ == "__main__":
    df = build_panel()
    out = C.DERIVED / "tx_hhsc_panel.parquet"
    df.to_parquet(out, index=False)
    print(f"\nsaved {out} ({len(df)} rows)")
    print(df.to_string(index=False))
    # validate vs known datum: Nov-2023 report, latest quarter (FY2023 Q4 -> 2023-08), MAX: count 968, days 659
    chk = df[(df.security_level == "max") & (df.period == "2023-08")]
    if len(chk) == 1:
        r = chk.iloc[0]
        ok = (r.waitlist_count == 968) and (r.avg_wait_days == 659)
        print(f"\nANCHOR CHECK (max FY2023-Q4): count={r.waitlist_count} (exp 968), days={r.avg_wait_days} (exp 659) -> {'PASS' if ok else 'FAIL'}")
