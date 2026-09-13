"""WA Trueblood monthly-report extractor — dashboard tree.

DUPLICATED (2026-08-28) from code/pipeline/wa_trueblood.py, not imported from it — the paper and
dashboard trees are kept deliberately independent (see dashboard/code/config.py's docstring). All
parsing logic below (column-anchoring by the compliance-% cell, the "Court Orders Completed"
column detection, table classification, dedup rule) is identical to the paper's copy; only the
month-range function and the __main__ block differ, because this tree's job is different: an
OPEN-ENDED living panel over dashboard_data/raw/wa/, not a frozen, gated, paper-scoped window.
Re-sync by hand if the paper-side parser changes (do not import across trees at runtime).

Proves the load-bearing assumption: a clean longitudinal competency-services time-series can be
parsed from WA DSHS's monthly court-monitor PDFs (2018+ format). Each monthly report carries a
13-month rolling grid per facility/service table (e.g. "Table 2. Class Member Status WSH -
Jail-based Competency Evaluations"). Columns drift across years, so indices are never hardcoded —
anchored on the compliance-"%" columns instead. Overlapping 13-month windows are deduped (latest
mature value wins). Provenance: every row carries source_url + source_sha.
"""
from __future__ import annotations
import re
from pathlib import Path
import pdfplumber, pandas as pd
import config as C
import _util

MONTH_RE = re.compile(r'^\s*(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[-\s]?(\d{2})\s*$', re.I)
TABLE_REF_RE = re.compile(r'TABLE\s+(\d+[a-z]?)\.', re.I)
MON = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
NUM_RE = re.compile(r'^-?\d+(\.\d+)?$')

def _period(cell: str):
    m = MONTH_RE.match(cell or "")
    if not m: return None
    return f"20{m.group(2)}-{MON[m.group(1).upper()]:02d}"

def _num(cell):
    s = (cell or "").replace(",", "").replace("%", "").strip()
    return float(s) if NUM_RE.match(s) else None

# The "Court Orders Completed" count column was ADDED in the 2019-04 report (checked directly
# against the raw PDFs: 2019-01/02/03 have no such column in their extracted tables, 2019-04
# onward does -- this comment previously said 2019-05, which was off by one report). Older-format
# tables (2019-03 and earlier) have no such column, so the positional anchor at p0-3 would
# land on the incomplete-referrals median instead. Detect the column structurally by its
# header text and NULL orders_completed when the table lacks it (never read the wrong cell) --
# this detection is structural, not date-based, so the exact month above is informational only
# and was never load-bearing for correctness.
COMPLETED_HDR_RE = re.compile(r'court\s*orders?\s*completed', re.I)

def _has_completed_col(data) -> bool:
    """True iff this month-grid table actually carries a 'Court Orders Completed' column.
    Reads the table's own header cells (the non-period rows above the data) — structural,
    not month-hardcoded. Only the standalone count header matches; the compliance-% phrases
    ('Percent completed within 7 days ...') do not, because 'court orders' precedes 'completed'."""
    for r in data:
        if not r: continue
        if _period(r[0] or ""):            # reached the data rows; headers are above them
            continue
        for c in r:
            if c and COMPLETED_HDR_RE.search(c):
                return True
    return False

def _ssl_ctx():
    """A properly-verified TLS context even on a Python whose default cert store is
    misconfigured (the macOS 'Install Certificates' gap = CERTIFICATE_VERIFY_FAILED,
    the real root cause of the silent download failures). Uses certifi's CA bundle."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()

def download_report(year: int, month: int, force=False, verbose=True) -> Path | None:
    """Fetch one monthly report over a properly-verified TLS context (certifi), with a
    guarded curl last-resort. FAILS LOUDLY with per-URL reasons and correctly distinguishes
    'not published yet' (every host returns HTTP >=400) from a real error — so the silent
    staleness that froze this data for a year (a bare `except: continue`) cannot recur."""
    out = C.RAW / "wa" / f"Trueblood-Report-{year:04d}-{month:02d}.pdf"
    if out.exists() and not force:
        return out
    import urllib.request as U, urllib.error as UE, subprocess, shutil
    ctx = _ssl_ctx()
    errors, http_status = [], []
    for url in C.wa_report_urls(year, month):
        # 1) urllib with a real CA bundle — the primary, portable path
        try:
            req = U.Request(url, headers={"User-Agent": "Mozilla/5.0 (Competency Restoration Observatory research)"})
            data = U.urlopen(req, timeout=60, context=ctx).read()
            if data[:4] == b"%PDF":
                out.write_bytes(data); return out
            errors.append(f"{url}: HTTP 200 but not a PDF (starts {data[:12]!r})")
            continue
        except UE.HTTPError as e:
            http_status.append(e.code); errors.append(f"{url}: urllib HTTP {e.code}")
            continue                                          # a definite HTTP status; curl won't differ
        except Exception as e:
            errors.append(f"{url}: urllib {type(e).__name__}: {e}")
        # 2) curl last-resort — only if urllib hit a NON-HTTP error (e.g. TLS on a stripped box)
        if shutil.which("curl"):
            try:
                r = subprocess.run(["curl", "-fsS", "--max-time", "60", "-o", str(out), url],
                                   capture_output=True, timeout=90)
                if r.returncode == 0 and out.exists() and out.read_bytes()[:4] == b"%PDF":
                    return out
                out.unlink(missing_ok=True)
                if r.returncode == 22:                        # curl --fail: server returned HTTP >=400
                    http_status.append(404); errors.append(f"{url}: curl HTTP error (>=400)")
                else:
                    errors.append(f"{url}: curl rc={r.returncode} {r.stderr.decode()[:80]!r}")
            except Exception as e:
                errors.append(f"{url}: curl {type(e).__name__}: {e}")
    # honest classification: every host returned >=400 -> not published yet; anything else = a real break
    not_published = bool(http_status) and all(c and c >= 400 for c in http_status)
    if verbose:
        tag = "not published yet" if not_published else "DOWNLOAD FAILED"
        print(f"  [{tag}] {year:04d}-{month:02d}:")
        for e in errors:
            print(f"      - {e}")
    return None

def _classify(title: str):
    """Map a (concatenated) table title -> (facility, stage, setting)."""
    t = title.lower()
    if "total" in t:                       fac = "TOTAL"
    elif "western" in t:                   fac = "WSH"
    elif "eastern" in t:                   fac = "ESH"
    elif "residential" in t or "behavioral health treatment" in t or "bhtc" in t: fac = "RTF"
    elif "ocrp" in t or "outpatient competency restoration" in t:                  fac = "OCRP"
    else:                                  fac = "?"
    stage = "restoration" if "restoration" in t else "evaluation" if "evaluation" in t else "?"
    if stage == "?":
        if fac == "OCRP":                                 # OCRP = Outpatient Competency RESTORATION Program
            stage = "restoration"
        elif "inpatient competency services" in t or "inpatient services" in t:
            # WA convention: the UNQUALIFIED inpatient table is the evaluation one (restoration
            # always says 'Restoration'). "inpatient services" (without "competency") widened in
            # 2026-09-11 -- the WSH/ESH-specific old-format titles say "...Inpatient Competency
            # Services", but the TOTALS old-format title drops "Competency": "...(Totals) -
            # Inpatient Services" (Trueblood-Report-2018-11.pdf p.12 et al, confirmed directly).
            # Both mean the same unqualified-inpatient=evaluation table; only reached here (this
            # branch) once "restoration"/"evaluation" are both already confirmed absent from t.
            stage = "evaluation"
    setting = ("outpatient" if "outpatient" in t or "ocrp" in t
               else "jail" if "jail" in t
               else "inpatient" if "inpatient" in t else "all")
    return fac, stage, setting

def _page_lines(pg):
    """[(top_y, line_text)] for every reconstructed text line on the page (by word position)."""
    by_row = {}
    for w in pg.extract_words():
        by_row.setdefault(round(w["top"] / 3.0), []).append(w)
    lines = []
    for ws in by_row.values():
        ws = sorted(ws, key=lambda w: w["x0"])
        lines.append((min(w["top"] for w in ws), " ".join(w["text"] for w in ws)))
    return sorted(lines)

def _parse_grid(data, fac, stage, setting, name, sha, url, pdf_page, table_ref):
    """Parse one month-grid table; anchor columns on the compliance-% cell.

    ADDITIVE (2026-07-11), leaves all prior columns byte-identical:
      - orders_signed        = Court Orders Signed (DEMAND) = first numeric after the month
      - pct_within_alt2/alt3 = the 2nd/3rd compliance-% columns the table carries.
        For the restoration totals (Table 11) the three are, in order:
        within-7d-from-order-SIGNATURE (=pct_within_deadline, our primary/strictest),
        within-7d-from-RECEIPT-of-order, and within-7d-receipt-or-14d-from-signature.
        (Meaning is table-specific; documented in each table's column headers.)

    pdf_page: the 1-indexed PHYSICAL PDF page this table's row came from -- the PDF's own page
    count (jump-to-page N in any reader), not the document's printed page label (which can
    differ, e.g. a cover page offsetting every subsequent printed number), on the reasoning
    that a reader verifying a number opens a PDF viewer and jumps by physical page, not by
    footer text -- plain, robust, and always available, unlike parsing every footer.

    table_ref: the report's own table label ("Table 1a"), extracted from the literal "TABLE
    1a. Class Member Status ..." heading printed directly above each grid -- the report's own
    citation unit, one level more specific than the page."""
    out = []
    has_completed = _has_completed_col(data)     # old-format tables lack the count column
    # A row with zero completions that month legitimately prints "n/a" for every day/percent
    # column (undefined, not just missing) -- FIXED 2026-09-11 (meta/docs/data_validation_
    # 2026-09-11/wa_batch2_findings.md, Trueblood-Report-2026-06.pdf Table 5c/OCRP, 2025-06:
    # signed=3, completed=0, everything else genuinely n/a). Column-anchoring below is keyed on
    # the first "%" cell in the ROW -- an all-"n/a" row has none, so it was silently dropped
    # entirely, losing even its perfectly real signed/completed counts. Recover the column
    # layout from the first SIBLING row in this same table that does have a "%" anchor (same
    # table = same columns every month), reused ONLY when the row lengths match exactly, so a
    # differently-shaped row can't be misaligned by this fallback.
    ref_p0 = None
    for r in data:
        if not r: continue
        idx = [i for i, c in enumerate(r) if c and "%" in c]
        if idx:
            ref_p0, ref_len = idx[0], len(r)
            break
    for r in data:
        if not r: continue
        period = _period(r[0])
        if not period: continue
        pct_idx = [i for i, c in enumerate(r) if c and "%" in c]
        if pct_idx:
            p0 = pct_idx[0]
        elif ref_p0 is not None and len(r) == ref_len:
            p0 = ref_p0            # this row itself has no "%" cell; borrow a verified sibling's layout
        else:
            continue
        med = _num(r[p0 - 1]) if p0 - 1 >= 0 else None
        avg = _num(r[p0 - 2]) if p0 - 2 >= 0 else None
        # only read the count when the table actually has the column; else NULL (never grab
        # the adjacent incomplete-referrals median that sits at p0-3 in the old format).
        completed = (_num(r[p0 - 3]) if (has_completed and p0 - 3 >= 0) else None)
        signed = _num(r[1]) if len(r) > 1 else None                 # demand = orders signed (col 1)
        # Skip only if this row is truly empty of any usable data -- a legitimate zero-
        # completions row (avg/med genuinely n/a) still has real signed/completed counts and
        # must still ship; only a row with NOTHING at all is a non-data line.
        if avg is None and med is None and completed is None and signed is None: continue
        pct2 = _num(r[pct_idx[1]]) if len(pct_idx) >= 2 else None
        pct3 = _num(r[pct_idx[2]]) if len(pct_idx) >= 3 else None
        out.append(dict(state="WA", period=period, facility=fac, stage=stage, setting=setting,
                        orders_signed=signed,
                        orders_completed=completed, avg_days_to_completion=avg,
                        median_days_to_completion=med, pct_within_deadline=_num(r[p0]),
                        pct_within_alt2=pct2, pct_within_alt3=pct3,
                        report=name, source_url=url, source_sha=sha, pdf_page=pdf_page,
                        table_ref=table_ref))
    return out

def _broken_font_fallback(pg):
    """Recover a Class-Member-Status page whose embedded font defeats pdfplumber's default word-
    boundary detection badly enough that find_tables() finds no usable month-grid table at all --
    ADDED 2026-09-11 (re-audit finding, meta/docs/data_validation_2026-09-11_relens/
    wa_lensB_completeness_findings.md): Trueblood-Report-2018-11/12.pdf and -2019-01.pdf's
    INPATIENT-table pages (WSH/ESH/TOTALS) have a font whose character-width metrics are wide
    enough that pdfplumber's default extract_words() (x_tolerance=3) reads every character (or
    near enough) as its own separate word -- e.g. "Oct-17" comes back as ['O','ct-1','7']. This
    is the sole cause of a 40-row-month gap (Oct 2017-Aug 2018 across 9 streams) with no future
    report able to self-heal it (unlike every other table-detection failure in this corpus,
    which the 13-month rolling window and report redundancy already recover). Confirmed directly
    (word-coordinate inspection): x_tolerance=7 correctly re-merges every split token corpus-wide
    on these pages (including the one abbreviation, "Mar-18", that x_tolerance=5 still splits as
    'M'+'ar-18') without over-merging any two genuinely distinct values -- tested stable through
    x_tolerance=20. This is a font-metrics quirk specific to these three files' inpatient-table
    pages, not a genuine ambiguity in the underlying PDF, so a fixed override is safe here.

    A page's title line (e.g. "TABLE 1b. Class Member Status Western State Hospital - Inpatient
    Competency Services") is NOT affected by this font issue -- confirmed directly, it reads
    clean even at the default tolerance -- so it's read via the existing `_page_lines()` (not
    re-derived here), unlike the DATA rows below it.

    An inpatient-table page can carry TWO sub-tables (evaluation then restoration) under one
    title. A bare rotated side-label reading "Restoration" does appear somewhere on such pages
    (gluing a footnote-marker digit in three different ways across the corpus: "Restoration",
    "Restoration4", and "Restoration"+"4" as two separate tokens -- matched with
    `restoration\\d*`, not an exact string) -- but its Y-position CANNOT be used as the segment
    boundary: confirmed directly (Trueblood-Report-2018-11.pdf p.8) that the label sits at the
    vertical CENTER of its own sub-table's height, not its top, so several of the restoration
    sub-table's own rows (its earliest months) print ABOVE the label and would be wrongly folded
    into the evaluation segment by a position-based split -- a real bug caught only by checking
    the recovered rows' values against the audit's own per-stream period ranges, not by the
    parse succeeding without error. The reliable, page-layout-independent signal is a PERIOD
    REPEATING: this corpus's two sub-tables always cover the identical month range in the same
    order, so the row immediately after the first table's last month is always the second
    table's first month, of a period already seen in the current segment -- split there instead.
    The "Restoration" label is used only to confirm a second segment, once found, actually IS the
    restoration table (checked once per page, not per row). Jail-based and TOTALS
    jail/inpatient-evaluation-only pages never repeat a period and correctly return a single
    segment. Row scanning stops at the "Data Notes:" line so a later footnote sentence that
    happens to mention "restoration" in prose (confirmed real case: "...inpatient restoration
    data for WSH includes...") can never be mistaken for a restoration-table confirmation.

    Returns (title_line, segments) where segments is a list of (stage_override, data) tuples --
    stage_override is None (classify from title_line alone) or "restoration" (append to the
    title before classifying). `data` is a list of token-lists in the exact shape `_parse_grid`
    already expects (one list per row, first token expected to parse as a period) -- never
    guesses a row that doesn't start with a real month abbreviation."""
    lines = _page_lines(pg)
    # LAST matching line, not first: page 7 of these reports carries a generic section-intro
    # line ("CLASS MEMBER STATUS DATA TABLES (See APPENDICES...)") directly above the real
    # per-table title ("TABLE 1a. Class Member Status Western State Hospital..."), and the
    # generic line has none of the facility/stage/setting keywords _classify() needs -- same
    # "last, not first" bug class already documented and fixed for the main find_tables() path
    # just above this function (see parse_report's own "LAST matching line, not first" comment).
    title_line = next((txt for _, txt in reversed(lines) if re.search(r'class member status', txt, re.I)), "")
    words = pg.extract_words(x_tolerance=7)
    by_row = {}
    for w in words:
        by_row.setdefault(round(w["top"] / 3.0), []).append(w)
    rows = []
    for ws in by_row.values():
        ws = sorted(ws, key=lambda w: w["x0"])
        rows.append((min(w["top"] for w in ws), [w["text"] for w in ws]))
    rows.sort(key=lambda r: r[0])

    saw_restoration_label = False
    segments_raw = []      # [[row, row, ...], [row, ...]] -- split on period-repeat only
    current = []
    seen_periods = set()
    for _, toks in rows:
        if toks and toks[0].lower() == "data" and any("notes" in t.lower() for t in toks[1:2]):
            break
        per = _period(toks[0] if toks else "")
        if per:
            if per in seen_periods:
                segments_raw.append(current)
                current, seen_periods = [], set()
            current.append(toks)
            seen_periods.add(per)
            continue
        if any(re.fullmatch(r'restoration\d*', t, re.I) for t in toks):
            saw_restoration_label = True
    if current:
        segments_raw.append(current)

    if len(segments_raw) > 2:
        return title_line, []      # never seen on this corpus -- don't guess an unverified shape
    if len(segments_raw) == 2 and not saw_restoration_label:
        # Two repeating blocks but no confirming label anywhere on the page -- never guess which
        # (if either) is really "restoration"; ship neither rather than risk a wrong classification.
        return title_line, []
    segments = [(None, segments_raw[0])] if segments_raw else []
    if len(segments_raw) == 2:
        segments.append(("restoration", segments_raw[1]))
    return title_line, segments

def parse_report(path: Path) -> list[dict]:
    # Header-attribution bug (found by an independent audit, confirmed against
    # Trueblood-Report-2019-10/11/12.pdf p.10): the old fixed "-70px above this table" band
    # misses a table's title whenever a page carries two back-to-back grid tables tightly
    # packed with little separating text -- exactly WSH-then-RTF restoration tables in the
    # 2018-2019 report era. When the band missed, the code fell back to a WHOLE-PAGE text
    # search for "class member status", which on a two-table page concatenates BOTH tables'
    # titles -- and `_classify()`'s elif chain (western checked before residential) then
    # always resolved to WSH, silently overwriting the real RTF row under the wrong label and
    # leaving WSH's own true value for that month completely absent from the dataset.
    #
    # Fix: attribute each table using ONLY text that provably belongs to it -- text strictly
    # between the previous table's bottom edge (or page top, for the first table) and this
    # table's own top edge, never anything from another table's region. This can't cross-
    # contaminate by construction. Falls back, in order, to (a) the table's own first
    # extracted row (some tightly-packed tables absorb their title AS a data row instead of
    # separate page text) and (b) inheriting the immediately preceding table's classification
    # on the SAME page (a titleless continuation sub-table, e.g. a "BY COMPLETION MONTH"
    # breakdown, describes the same facility/stage/setting as the table above it) -- never the
    # old whole-page fallback, which is exactly what mixed the two tables' identities.
    sha = _util.sha12(path)
    url = f"(local) {path.name}"
    rows = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            text = pg.extract_text() or ""
            if "Class Member Status" not in text:
                continue
            lines = _page_lines(pg)
            tables = sorted(pg.find_tables(), key=lambda ft: ft.bbox[1])
            usable = any(any(_period((r or [""])[0]) for r in ft.extract() if r) for ft in tables)
            # Gated on the exact 3 files this fallback was built for and individually verified
            # against (2026-09-11 re-audit) -- CONFIRMED NEEDED via `git log`-independent testing
            # against a 4th candidate, Trueblood-Report-2019-04.pdf, whose own page 8 ALSO clears
            # this same "no usable table" trigger but carries a genuinely different table
            # ("Table 1c", a WSH+RTF-COMBINED table whose title wraps across two physical lines
            # and whose data rows carry an extra, unexplained numeric token this fallback's
            # column-anchoring was never designed to handle) -- confirmed that page's own data is
            # fully redundant with periods already correctly captured elsewhere (via properly-
            # detected tables in later reports), so gating narrowly here costs nothing real and
            # avoids shipping an unverified, structurally-different table through a fallback
            # that was only ever checked against these three.
            if not usable and path.name in (
                "Trueblood-Report-2018-11.pdf", "Trueblood-Report-2018-12.pdf",
                "Trueblood-Report-2019-01.pdf"):
                title_line, segments = _broken_font_fallback(pg)
                for override, data in segments:
                    header = title_line + (" Restoration" if override == "restoration" else "")
                    fac, stage, setting = _classify(header)
                    tm = TABLE_REF_RE.search(title_line)
                    table_ref = f"Table {tm.group(1)}" if tm else None
                    rows += _parse_grid(data, fac, stage, setting, path.name, sha, url,
                                         pg.page_number, table_ref)
                continue
            prev_bottom = 0.0
            prev_classification = None
            for ft in tables:
                data = ft.extract()
                if not any(_period((r or [""])[0]) for r in data if r):
                    continue                                  # not a month-grid table
                ttop = ft.bbox[1]
                # Region strictly between the previous table's bottom and this table's own top --
                # can never include another table's title or footnotes. But when this is the
                # FIRST table on a page, that region can span the whole page above it, which can
                # include unrelated prior-table FOOTNOTE prose that happens to mention "jail" or
                # a facility name in passing (confirmed real case: Trueblood-Report-2019-08.pdf
                # p.10's footnote text "...individuals waited for competency services in jail..."
                # is methodology prose, not this table's own setting, but got matched anyway when
                # the whole region was classified as one blob). Fix: search LINE BY LINE for the
                # actual "class member status" title line(s), and classify from ONLY those lines
                # (title + the next line, to catch a wrapped "...(Restorations)" subtitle) --
                # never the surrounding footnote/prose text, no matter how far back it reaches.
                # LAST matching line, not first: a page can carry a generic section-intro line
                # ("Class Member Status Data Tables ... Data Tables 2 Through 4B.") well above
                # the real per-table title (confirmed real case: Trueblood-Report-2024-06.pdf
                # p.13 has exactly this, ~150px above the genuine "Table 2. Class Member Status
                # Western State Hospital - Jail-based Competency Evaluations" line) -- the real
                # title is always the occurrence closest to (immediately above) its own table.
                region = [(y, txt) for y, txt in lines if prev_bottom <= y <= (ttop + 6)]
                title_idx = next((i for i, (y, txt) in reversed(list(enumerate(region)))
                                   if re.search(r'class member status', txt, re.I)), None)
                band = (" ".join(txt for _, txt in region[title_idx:title_idx + 2])
                        if title_idx is not None else "")
                first_row_title = ((data[0][0] or "") if data and data[0] else "")
                if band:
                    header = band
                elif re.search(r'class member status', first_row_title, re.I):
                    header = first_row_title
                elif prev_classification is not None:
                    header = None                              # signal: inherit below
                else:
                    header = " ".join(txt for _, txt in region)  # nothing to go on; classify as "?"
                fac, stage, setting = _classify(header) if header is not None else prev_classification
                prev_classification = (fac, stage, setting)
                tm = TABLE_REF_RE.search(band) or TABLE_REF_RE.search(first_row_title)
                table_ref = f"Table {tm.group(1)}" if tm else None
                rows += _parse_grid(data, fac, stage, setting, path.name, sha, url,
                                     pg.page_number, table_ref)
                prev_bottom = ft.bbox[3]
    return rows

def build_panel(periods: list[tuple[int, int]], offline: bool = False) -> pd.DataFrame:
    """Build the panel from monthly reports.

    offline=True uses ONLY the PDFs already in dashboard_data/raw/wa/ and never touches the
    network — the dashboard build should stay reproducible from what's already on disk, same
    discipline as the paper gate, even though this panel's own window is open-ended.
    """
    allrows = []
    for (y, m) in periods:
        if offline:
            p = C.RAW / "wa" / f"Trueblood-Report-{y:04d}-{m:02d}.pdf"
            p = p if p.exists() else None
        else:
            p = download_report(y, m)
        if not p:
            continue
        rr = parse_report(p)
        print(f"  [ok]   {y}-{m:02d}: {len(rr)} rows from {p.name}")
        allrows += rr
    df = pd.DataFrame(allrows)
    if df.empty: return df
    # dedup overlapping 13-mo windows: keep the value from the LATEST report (most mature)
    df["rep_ym"] = df["report"].str.extract(r'(\d{4}-\d{2})')
    df = (df.sort_values("rep_ym")
            .drop_duplicates(["state", "facility", "stage", "setting", "period"], keep="last")
            .drop(columns="rep_ym")
            .sort_values(["facility", "stage", "setting", "period"]))
    # Two cells, hand-corrected 2026-09-11 (adversarial review of the n/a-row fix, meta/docs/
    # data_validation_2026-09-11/): Jun-22's pct_within_alt3 for ESH/evaluation/jail and TOTAL/
    # evaluation/jail is shipping from Trueblood-Report-2023-06.pdf (43%, 78%), but the SAME row
    # was revised in Trueblood-Report-2023-07.pdf the following month (50%, 82%, confirmed by
    # directly opening that PDF's p.19/p.22 -- every other field on the row is identical between
    # both reports). Normally "keep the newest report" would pick that revision up automatically,
    # but 2023-07.pdf is one of the reports whose own table-detection this pipeline can't
    # currently recover (pdfplumber finds zero tables on those specific pages -- see
    # meta/docs/data_validation_2026-09-11/wa_batch2_findings.md Part 5 for the full
    # investigation), and Jun-22 rolls out of every later report's 13-month window, so there's no
    # future report this can self-heal from. Two cells, both independently verified against the
    # source PDF directly, not from the audit doc alone -- narrow enough to hand-correct rather
    # than build a general recovery mechanism for a table-detection problem with no safe
    # automated fix (see the same investigation for why).
    # CORRECTED 2026-09-11 (adversarial review of THIS fix, same session): the first version of
    # this override updated pct_within_alt3 but left report/pdf_page/source_sha still pointing at
    # Trueblood-Report-2023-06.pdf -- which prints the OLD, pre-revision value, not the corrected
    # one. A reader clicking that citation would land on a page contradicting the number shown.
    # The automated PDF-citation-audit gate gave a false pass on this: "50"/"82" happen to also
    # appear elsewhere on the (wrong) 2023-06.pdf page as substrings of unrelated cells, which a
    # substring match can't distinguish from a real citation -- a real, if narrow, gap in that
    # checker's coverage, worth remembering. Every field below (report/pdf_page/table_ref/
    # source_sha) is now the actual page this value is really printed on.
    _new_report = "Trueblood-Report-2023-07.pdf"
    _new_sha = _util.sha12(C.RAW / "wa" / _new_report)
    _pct3_fixes = {
        ("ESH", "evaluation", "jail", "2022-06"): (50.0, 19, "Table 5"),
        ("TOTAL", "evaluation", "jail", "2022-06"): (82.0, 22, "Table 8"),
    }
    for (fac, stage, setting, period), (val, pdf_page, table_ref) in _pct3_fixes.items():
        mask = ((df.facility == fac) & (df.stage == stage) & (df.setting == setting)
                & (df.period == period))
        df.loc[mask, "pct_within_alt3"] = val
        df.loc[mask, "report"] = _new_report
        df.loc[mask, "source_url"] = f"(local) {_new_report}"
        df.loc[mask, "source_sha"] = _new_sha
        df.loc[mask, "pdf_page"] = pdf_page
        df.loc[mask, "table_ref"] = table_ref
    return df

def _months(start, end):
    return [(y, m) for y in range(start[0], end[0] + 1) for m in range(1, 13) if start <= (y, m) <= end]

def dashboard_months():
    """Open-ended living axis: 2018-11 through next year. Unlike the paper's frozen
    canonical_months(), this is meant to grow the moment a new report lands in
    dashboard_data/raw/wa/ — there's no gate pinning this tree to a closed window."""
    from datetime import date
    today = date.today()
    return _months((2018, 11), (today.year + 1, 6))

if __name__ == "__main__":
    import sys
    months = dashboard_months()
    print(f"Building WA dashboard panel from up to {len(months)} monthly reports "
          f"(source: {C.RAW / 'wa'}) ...")
    df = build_panel(months, offline=True)
    if df.empty:
        print("NO ROWS — parser needs adjustment"); sys.exit(1)
    out = C.DERIVED / "wa_trueblood_dashboard.parquet"
    df.to_parquet(out, index=False)
    print(f"\nsaved {out}  ({len(df)} rows, {df.period.min()}..{df.period.max()})")
    print("facility x stage coverage:")
    print(df.groupby(["facility", "stage", "setting"])["period"].agg(["count", "min", "max"]).to_string())
