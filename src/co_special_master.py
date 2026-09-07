"""CO extractor — Layer 2: special-master court reports (the rich monthly Tier-1/Tier-2 series).

Each quarterly report embeds two semi-structured tables:
  (A) "Average Wait Times for Inpatient Competence Restoration" — Tier1/Tier2 avg days by month
      + the decree deadline columns ("7 days", "49 days").
  (B) "Number of Defendants Waiting for Inpatient Restoration" — Tier1/Tier2/Combined counts by
      month, anchored on the "Combined" row.
Period headers vary per report and, in the 2025+ format, sometimes wrap a column's completing
year onto the PHYSICAL LINE BELOW the header (pdfplumber's own line-joining artifact -- in the
worst case a whole month name is separated from its neighbours onto a different line). Text-only
regex cannot always recover this correctly, so the count table's period axis is reconstructed
positionally (word x/y coordinates, see `_combined_row_periods`) and used to date BOTH the count
rows and the wait-day rows (which are re-dated from the count axis, not their own header -- see
`parse_report`'s docstring). Some reports also carry a second, footnoted "Key Metric" wait-time
table covering overlapping quarters with genuinely DIFFERENT (and less authoritative) values than
the report's own prose citation -- resolved in `build()` by preferring the unfootnoted table on a
genuine conflict. This is the BEST decree-compliance data of any state (explicit Tier-vs-deadline
-> comparable to WA).

Files: dashboard_data/raw/co/sm_*.pdf. 3 files are the original 2018-21 Clearinghouse S3 vintage;
11 more (2023-2026) were sourced directly from CourtListener's RECAP storage CDN (free, not
paywalled, just not linked from the docket's own web page). 2 files in this glob are not actually
special-master quarterly reports (the Consent Decree filing itself, a 2019 status letter) and 1
has a broken/cid-encoded font pdfplumber can't read -- all three produce 0 rows and print a
[WARN] naming which, rather than silently vanishing (see `build()`).
"""
from __future__ import annotations
import re
from pathlib import Path
import pdfplumber, pandas as pd
import config as C
import _util

MON = {m[:3]: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
MONTH_TOK = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})?', re.I)
TIER_ROW = re.compile(r'^\s*Tier\s*([12])\s+(.+)$', re.I)
VAL = re.compile(r'(N/?A|[\d]+(?:\.\d+)?)')

_MONTH_WORD = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?$', re.I)
_YEAR_WORD = re.compile(r'^(\d{4}|\d{2})$')
_CELL_WORD = re.compile(r'^-?[\d.,]+\*{0,3}$|^N/?A\*{0,3}$', re.I)

def _header_periods_for_row(words, anchor_top, anchor_end_x, n_expected=None, exclude_tops=()):
    """Positional (x/y word-coordinate) reconstruction of ONE specific row's period axis,
    given that row's own label anchor (top, end-x of the label text). Needed because the
    2025+ report format's column labels sometimes wrap across TWO physical text lines (e.g.
    the header row reads "March Nov 25 - Feb 2026 Mar 2026 Apr 2026" while the completing
    year for the first two columns, "2019" and "Jan 26", sits on the line directly below) --
    `extract_text()`'s line-joined string genuinely drops which column a wrapped token
    belongs to (in the worst case the month name itself, not just its year, is on a
    different physical row than its neighbours), so no text-only regex on the flattened
    line can recover it correctly. Word coordinates can: cluster every month/year word in
    the header band by which numeric CELL it sits above (by x0 proximity), then take the
    LAST (bottom-most/right-most) month+year found near that cell. This has a second,
    load-bearing effect beyond fixing line-wrap: for a RANGE column ("Aug - Oct 23"), taking
    the last nearby month/year naturally resolves to the range's END month, not its start --
    exactly the convention this file's period-dating already documents for wait-day columns.

    n_expected caps how many numeric cells (sorted left to right) are treated as this row's
    real data columns, so a trailing non-data column picked up by the coordinate scan (e.g.
    the "7 days"/"28 days" decree-requirement column, whose bare number would otherwise look
    like a 5th cell) doesn't shift the alignment -- pass the already deadline-stripped cell
    count from the text-regex parse of this same row.

    exclude_tops skips the given row-top values entirely from the header band -- needed
    because a Tier-2 row can sit far enough below the shared header that the search band has
    to widen past an intervening Tier-1 DATA row; a bare integer value like a rounded "92"
    (92.0 days) fully matches the 2-digit-year pattern and would otherwise be misread as
    "year 92" -> 2092 if that row weren't excluded. Pass the OTHER known tier-row tops on
    this page/table so only genuine header text is ever scanned.

    Returns (periods, is_range) -- is_range[i] is True iff cell i's own header names two
    distinct months (a combined/rolling-window column, not one calendar month; see the
    tier_waitlist_count handling in parse_report() for why this matters). Returns (None, None)
    if the anchor has no cells to its right (never guess a partial axis -- callers fall back to
    a less precise method)."""
    row_words = [w2 for w2 in words if abs(w2['top'] - anchor_top) < 2]
    cells = sorted((w2 for w2 in row_words if w2['x0'] > anchor_end_x and _CELL_WORD.match(w2['text'])),
                   key=lambda w2: w2['x0'])
    if n_expected is not None:
        cells = cells[:n_expected]
    if not cells:
        return None, None
    # 60px, not 40: wide enough to reach a shared table header from a Tier-2 row even when a
    # Tier-1 row sits between it and the header -- verified against sm_2023-11-28.pdf's
    # unfootnoted table, where the Tier-2 row is ~45px below the header but only ~15px below
    # the Tier-1 row (see exclude_tops for why that intervening row must be filtered out).
    band = [w2 for w2 in words if anchor_top - 60 <= w2['top'] < anchor_top - 1 and w2['x0'] > 100
            and not any(abs(w2['top'] - t) < 2 for t in exclude_tops)]
    periods = []
    is_range = []
    for c in cells:
        near = sorted((w2 for w2 in band if abs(w2['x0'] - c['x0']) < 45), key=lambda w2: (w2['top'], w2['x0']))
        months = [w2['text'] for w2 in near if _MONTH_WORD.match(w2['text'])]
        years = [w2['text'] for w2 in near if _YEAR_WORD.match(w2['text'])]
        if not months or not years:
            periods.append(None)
            is_range.append(False)
            continue
        mon = months[-1][:3].lower()
        y = years[-1]
        yr = int(y) if len(y) == 4 else 2000 + int(y)
        periods.append(f"{yr:04d}-{MON[mon]:02d}")
        # A column header naming TWO DISTINCT months (e.g. "Nov 24 - Jan 25") is a multi-month
        # combined/rolling-average column, not a single calendar month -- taking the LAST month
        # (above) correctly resolves its END-month for DATING purposes (matches this file's
        # documented convention for wait-day ranges), but a count sourced from such a column is
        # NOT a point-in-time snapshot and must not be treated like one (see the "A headcount is
        # never fractional" guard in emit() -- this is the same bug class in a guise that happens
        # to divide evenly, so it wasn't caught by that check alone: real case confirmed directly
        # against sm_2025-05-28.pdf/sm_2025-02-28.pdf, "Nov24-Jan25" Tier-1=27 vs. the true
        # single-month Jan-2025 Tier-1=39 the same fact sits under in an earlier report).
        distinct_months = {m[:3].lower() for m in months}
        is_range.append(len(distinct_months) >= 2)
    return periods, is_range

def _combined_row_periods(words):
    """Same reconstruction as `_header_periods_for_row`, anchored on the count/waitlist
    table's 'Combined' row specifically. Returns (periods, is_range) or (None, None) if no
    'Combined' row is found or no anchor resolves a full axis (the pre-2022 report format this
    wasn't designed for falls back to the text-line method in the caller)."""
    for w in words:
        if w['text'] != 'Combined':
            continue
        periods, is_range = _header_periods_for_row(words, w['top'], w['x1'])
        if periods and all(periods):
            return periods, is_range
    return None, None

_TIER_WORD_COMBINED = re.compile(r'^Tier\s*([12])$', re.I)

def _tier_word_anchors(words):
    """Ordered list of (top, end-x, tier) for every 'Tier 1'/'Tier 2' TABLE-ROW occurrence on
    a page, in natural top-to-bottom reading order. A page can carry this label up to 4 times
    as a real row (a Tier-1/Tier-2 pair in the waitlist-COUNT table, another pair in the
    wait-DAYS table) -- used to positionally re-derive each individual row's own column
    period axis instead of assuming its cell count lines up with some OTHER row's/table's
    months (see `parse_report`, which consumes this list in the same order text-line Tier-row
    matches are found, so the two independently-extracted streams stay aligned row-for-row).

    'Tier 1'/'Tier 2' also appears constantly in this report's own PROSE ("Tier 1 defendants
    waited..."), which is NOT a table row and must not be treated as one -- filtered out by
    requiring the very next word on the same line to look like a data cell (a number, possibly
    with trailing footnote asterisks, or 'N/A'), which prose text never does."""
    anchors = []
    ws = sorted(words, key=lambda w: (w['top'], w['x0']))
    def _is_row(top, end_x):
        following = sorted((w2 for w2 in ws if abs(w2['top'] - top) < 2 and w2['x0'] > end_x),
                            key=lambda w2: w2['x0'])
        return bool(following) and _CELL_WORD.match(following[0]['text'])
    for i, w in enumerate(ws):
        m = _TIER_WORD_COMBINED.match(w['text'])
        if m:
            if _is_row(w['top'], w['x1']):
                anchors.append((w['top'], w['x1'], int(m.group(1))))
            continue
        if w['text'] == 'Tier':
            for w2 in ws[i + 1:i + 3]:
                if abs(w2['top'] - w['top']) < 2 and w2['text'] in ('1', '2') and 0 <= w2['x0'] - w['x1'] < 20:
                    if _is_row(w['top'], w2['x1']):
                        anchors.append((w['top'], w2['x1'], int(w2['text'])))
                    break
    return anchors

def _parse_period_header(line: str):
    """Return ordered list of 'YYYY-MM' for the data columns; infer year from any year in the header.
    Stops before deadline columns (those carry an explicit year but are handled by the caller via 'days')."""
    toks = MONTH_TOK.findall(line)
    if not toks:
        return []
    # default year = the last explicit year seen, else None; back-fill forward
    years = [int(y) if y else None for (_, y) in toks]
    # forward-fill then back-fill the year
    last = next((y for y in years if y), None)
    out = []
    for (mon, y), yi in zip(toks, years):
        yr = int(y) if y else last
        last = yr or last
        out.append((mon, yr))
    # second pass back-fill leading Nones
    firstyr = next((yr for _, yr in out if yr), None)
    periods = []
    for mon, yr in out:
        yr = yr or firstyr
        if yr:
            periods.append(f"{yr:04d}-{MON[mon[:3].lower()]:02d}")
        else:
            periods.append(None)
    return periods

def _isna(c): return c.upper().replace("/", "") == "NA"

def parse_report(path: Path) -> list[dict]:
    """Two-pass. Pass 1 collects each Tier row's (tier, metric, cells, header-periods) using the
    text-line method (correct for the pre-2022 report format). Pass 1.5 (right after `raw` is
    built) overrides COUNT rows' periods with the positional axis (`_combined_row_periods`)
    whenever it resolves cleanly -- fixes the 2025+ format's cross-line column-wrap mis-dating
    that the text-line method cannot recover (see that function's docstring). Pass 2 dates the
    WAIT rows from the (now-corrected) COUNT periods, not their own header: wait values are
    aligned to the count table's months, ending at the report's latest month (a range col like
    'Nov-Jan' lands on its END month, consistent with the count) -- this is the original C1 fix,
    unchanged.
    """
    sha = _util.sha12(path)
    with pdfplumber.open(path) as pdf:
        pages = [(pg.extract_text() or "", pg.extract_words()) for pg in pdf.pages]
    _pos_pairs = [_combined_row_periods(words) for _, words in pages]
    positional_axis = [p for p, _ in _pos_pairs]
    positional_is_range = [r for _, r in _pos_pairs]
    tier_anchors = [_tier_word_anchors(words) for _, words in pages]
    anchor_cursor = [0] * len(pages)
    raw = []  # {tier, metric, cells, periods, word_periods, page}
    for page_idx, (text, words) in enumerate(pages):
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            mt = TIER_ROW.match(ln)
            if not mt:
                continue
            tier = int(mt.group(1))
            rest = mt.group(2)

            # skip header lines that repeat tier labels, e.g. "Tier 1 Tier 2 Tier 1 Tier 2 ..."
            # (VAL would otherwise read the '2','1' from "Tier 2"/"Tier 1" as spurious data) — fixes the spurious-row bug
            if "tier" in rest.lower():
                continue
            rest_no_dead = re.split(r'\d+\s*days', rest)[0]          # cut at first "N days" deadline col
            cells = VAL.findall(rest_no_dead)
            if not cells:
                continue
            # Some reports (e.g. sm_2023-11-28.pdf) carry TWO separate "Average Wait Times..."
            # tables covering overlapping quarters with genuinely DIFFERENT values -- a "Key
            # Metric" summary table (footnoted, "**"/"***" = compliance annotations) and a
            # second, unfootnoted table matching the report's own prose citation exactly
            # (confirmed by direct comparison: prose states "128 days... 138 days", the
            # unfootnoted table's matching column reads 128.3/138, the footnoted table's reads
            # 124.9/156.6 for the SAME quarter). Track which rows carry footnote markers so
            # `build()` can prefer the unfootnoted table on a genuine conflict.
            has_star = "*" in rest_no_dead
            header = next((lines[j] for j in range(i - 1, max(i - 6, -1), -1)
                           if len(MONTH_TOK.findall(lines[j])) >= 2), "")
            periods = _parse_period_header(header)
            ctx = " ".join(lines[max(0, i - 22):i]).lower()
            has_decimal = any("." in c for c in cells)
            wait_ctx = "wait time" in ctx or "average wait" in ctx
            list_ctx = "waitlist" in ctx or "number of" in ctx or "individuals on" in ctx
            if wait_ctx and not list_ctx:        metric = "tier_wait_days_restoration"
            elif list_ctx and not wait_ctx:      metric = "tier_waitlist_count"
            elif has_decimal:                    metric = "tier_wait_days_restoration"
            elif all(_isna(c) or "." not in c for c in cells): metric = "tier_waitlist_count"
            else:                                continue

            # Consume this page's word-anchor stream in the same top-to-bottom order the
            # text-line regex is scanning -- but only NOW, for a row that has survived every
            # rejection check above, not on every raw "Tier N" text match. Consuming on every
            # match (including prose sentences merely starting with "Tier 1"/"Tier 2" that get
            # rejected a few lines below) was a real bug: it ate a real anchor before the real
            # table row reached it, permanently desyncing the two streams for the rest of the
            # page -- confirmed against sm_2024-02-28.pdf and sm_2025-05-28.pdf, where this
            # caused wait-day values to fall through to the discredited count-axis-borrowing
            # fallback and land on the wrong month, the exact bug class this file's positional
            # re-dating exists to eliminate. `_tier_word_anchors` itself already excludes prose
            # (via `_is_row`, requiring a numeric cell right after the label) -- consuming only
            # here, after this row is confirmed real, keeps the two independently-filtered
            # streams in the same order without wasting an anchor on a row that doesn't exist.
            word_top = word_x1 = None
            anchors = tier_anchors[page_idx]
            while anchor_cursor[page_idx] < len(anchors):
                a_top, a_x1, a_tier = anchors[anchor_cursor[page_idx]]
                anchor_cursor[page_idx] += 1
                if a_tier == tier:
                    word_top, word_x1 = a_top, a_x1
                    break

            # Positional VALUE validation, independent of the period-dating work above: a
            # prose sentence that merely starts with "Tier N " and happens to contain digits
            # near a "waitlist"-mentioning paragraph (real corpus case: "...only 12 Tier 1
            # Detainees were waiting in county jails as of July 31, 2024 (as compared to 58
            # one year before)" in sm_2024-08-28.pdf, p.3 -- no table anywhere nearby) can
            # still pass every check above and reach here with `cells` extracted from PROSE,
            # not a table -- e.g. cells=['31','2024','58'], the day-of-month and the year
            # digit from a date, misread as data. This produced a real, silently-shipped
            # fabricated row (2023-06, Tier 1, tier_waitlist_count=31.0) that only escaped
            # detection because a later report's genuine table value happened to overwrite
            # most of the damage on dedup -- not because anything caught it. `word_top` above
            # only proves *some* anchor was found; it doesn't prove THIS row's cells are real,
            # since a phantom text match can still walk the anchor cursor forward and steal a
            # later genuine row's anchor. Cross-check independently: read the actual numeric
            # words positioned at that anchor and require they match `cells` value-for-value.
            # A row that can't be corroborated this way is discarded entirely, not downgraded
            # to a text-only fallback -- the fallback is exactly what let bad cells through.
            verified = False
            if word_top is not None:
                anchor_cells = [w2['text'].rstrip('*')
                                 for w2 in sorted((w2 for w2 in words
                                                    if abs(w2['top'] - word_top) < 2 and w2['x0'] > word_x1
                                                    and _CELL_WORD.match(w2['text'])),
                                                   key=lambda w2: w2['x0'])[:len(cells)]]
                verified = ([c.replace(',', '') for c in anchor_cells] == [c.replace(',', '') for c in cells])
                if not verified:
                    word_top = word_x1 = None
            if not verified:
                continue

            other_tops = [a_top for a_top, _, _ in tier_anchors[page_idx] if word_top is None or abs(a_top - word_top) >= 2]
            # is_range discarded here: this word_periods result feeds WAIT-DAY row dating below,
            # where a multi-month range column is an expected, already-disclosed convention (its
            # END month), not a defect -- see the count-row-only handling further down for where
            # is_range actually matters (a count is never honestly a multi-month average).
            word_periods, _ = (_header_periods_for_row(words, word_top, word_x1, n_expected=len(cells),
                                                         exclude_tops=other_tops)
                                if word_top is not None else (None, None))
            raw.append(dict(tier=tier, metric=metric, cells=cells, periods=periods,
                             word_periods=word_periods, page=page_idx, has_star=has_star))

    # Prefer the positional (word-coordinate) period axis over the text-line one, for COUNT rows,
    # whenever it resolved a period for every cell on this row's page AND its length matches this
    # row's own cell count -- this is what actually fixes the 2025+ report format's cross-line
    # column-wrap mis-dating (see _combined_row_periods' docstring): both the emitted count VALUES
    # below and the count_periods axis used to re-date wait-day rows read from r["periods"], so
    # correcting it here fixes both in one place. Falls back to the text-line axis for any
    # page/report where the positional method didn't apply (e.g. no 'Combined' row -- the
    # pre-2022 report format, already correctly dated by the text-line method).
    for r in raw:
        if r["metric"] == "tier_waitlist_count":
            pos = positional_axis[r["page"]]
            r["is_range"] = [False] * len(r["cells"])   # default: no evidence this cell is a range
            if pos and len(pos) == len(r["cells"]):
                r["periods"] = pos
                r["is_range"] = positional_is_range[r["page"]]

    # count rows: the authoritative period axis per tier, used to re-date wait-day rows below
    count_periods = {}
    for r in raw:
        if r["metric"] == "tier_waitlist_count":
            cp = [p for p, c in zip(r["periods"], r["cells"]) if p and not _isna(c)]
            if cp:
                count_periods[r["tier"]] = cp

    rows = []
    def emit(period, tier, metric, value, has_star, pdf_page):
        # pdf_page: 1-indexed PHYSICAL PDF page (jump-to-page N in any reader), not the
        # document's own printed page label -- same convention as wa_trueblood.py's pdf_page.
        # No table_ref here, unlike ca_dsh.py/tx_hhsc.py: unlike THOSE numbered tables, these
        # reports don't consistently caption their Tier-1/Tier-2 tables (checked directly --
        # the only "Table N" text found anywhere in the corpus is an unrelated "Table 1" inside
        # a court-order boilerplate clause, not a caption on the data table itself), so a table
        # citation here would have to be invented, not read. pdf_page plus the positional
        # word-anchor validation each row already passed above (see the "Positional VALUE
        # validation" block in parse_report) together pin every row to a verified table
        # location on that page -- the same trust guarantee table_ref gives elsewhere, without
        # a fabricated number.
        # A headcount is never fractional -- a non-integer tier_waitlist_count means the source
        # column is actually a 3-month rolling AVERAGE masquerading as a single-month snapshot
        # (confirmed real case: sm_2025-02-28.pdf's count table has a "Aug - Oct 24" quarterly
        # column sitting between genuine single months "Nov 2024"/"Dec 2024"/"Jan 2025"; the
        # report's own prose gives the true Oct 2024 combined count as 208, while the quarterly
        # column's Tier-1+Tier-2 split sums to ~213 -- a materially different, averaged number).
        # Unlike wait-days (where a quarter-end reading is this file's own documented, disclosed
        # convention), a fractional "count of people" has no honest single-month interpretation
        # to fall back to -- excluded here as a parse miss, not silently rounded or kept.
        if metric == "tier_waitlist_count" and float(value) != int(float(value)):
            return
        rows.append(dict(state="CO", period=period, tier=tier, metric=metric,
                         value=float(value), report=path.name, source_sha=sha, has_star=has_star,
                         pdf_page=pdf_page))
    for r in raw:
        if r["metric"] != "tier_wait_days_restoration":
            is_range = r.get("is_range") or [False] * len(r["cells"])
            for p, c, rng in zip(r["periods"], r["cells"], is_range):
                # A tier_waitlist_count cell sourced from a column whose own header names TWO
                # distinct months (a combined/rolling window, not one calendar month) is not a
                # point-in-time snapshot -- excluded the same way a non-integer average already
                # is above, not silently kept because this particular window happened to divide
                # evenly (see _header_periods_for_row's is_range docstring for the confirmed
                # real case this closes).
                if r["metric"] == "tier_waitlist_count" and rng:
                    continue
                if p and not _isna(c):
                    emit(p, r["tier"], r["metric"], c, r["has_star"], r["page"] + 1)
            continue
        # Wait-day columns are sometimes single months, sometimes rolling multi-month ranges
        # (a range column dates to its own END month -- see _header_periods_for_row) -- prefer
        # this row's OWN header, resolved positionally (handles cross-line wraps and ranges
        # correctly) or, failing that, from the flattened text line, over ever assuming this
        # row's N cells line up with some OTHER table's most recent N months. That borrowing
        # was this function's original (and, for 2023+ reports, WRONG) default: a report whose
        # wait-day table has quarterly columns ("Nov22-Jan23 | Feb-Apr23 | May-Jul23 |
        # Aug-Oct23") would get all 4 quarterly averages relabeled onto the 4 most recent
        # individual months, e.g. the May-Jul23 average mislabeled as a September reading --
        # confirmed against the source PDF text directly. Only reached as a last resort now,
        # for reports where this row's own header genuinely can't be resolved either way.
        data = [c for c in r["cells"] if not _isna(c)]
        wp = r.get("word_periods")
        if wp and len(wp) == len(r["cells"]) and all(wp):
            use = [p for p, c in zip(wp, r["cells"]) if not _isna(c)]
        elif r["periods"] and len(r["periods"]) == len(r["cells"]) and all(r["periods"]):
            use = [p for p, c in zip(r["periods"], r["cells"]) if not _isna(c)]
        elif r["tier"] in count_periods:
            cp = count_periods[r["tier"]]
            use = cp[-len(data):] if len(cp) >= len(data) else cp
            data = data[-len(use):]
        else:
            continue
        for p, v in zip(use, data):
            emit(p, r["tier"], r["metric"], v, r["has_star"], r["page"] + 1)
    return rows

def build() -> pd.DataFrame:
    rows = []
    for p in sorted((C.RAW / "co").glob("sm_*.pdf")):
        rr = parse_report(p)
        if not rr:
            # A zero-row file must never vanish silently -- but the cause varies and shouldn't be
            # assumed. Confirmed two distinct causes so far: sm_2024-11-28.pdf embeds a font with
            # no usable Unicode CMap (pdfplumber's extract_text() returns raw "(cid:N)" glyph
            # codes -- checked directly: 0 occurrences of "tier" in >1M extracted chars; would
            # need OCR to recover). sm_109305.pdf/sm_109327.pdf are NOT special-master quarterly
            # reports at all despite matching the sm_*.pdf glob -- they're the underlying Consent
            # Decree filing and a March-2019 status letter, genuinely with no Tier table to find.
            with pdfplumber.open(p) as _pdf:
                _txt = "\n".join((pg.extract_text() or "") for pg in _pdf.pages)
            cause = "cid-encoded/broken font" if "(cid:" in _txt[:2000] else "not a Tier-table report (check by hand)"
            print(f"  [WARN] {p.name}: 0 Tier datapoints -- {cause}")
            continue
        print(f"  [ok] {p.name}: {len(rr)} Tier datapoints")
        rows += rr
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # On a genuine conflict (same period/tier/metric, different source rows -- e.g. the
    # "Key Metric" footnoted table vs. the main unfootnoted table, see the has_star comment
    # above), prefer the unfootnoted row. Within a tie on that (both footnoted, or both not --
    # e.g. 2024-01 Tier-1 count: 23 in sm_2024-02-28.pdf vs 31 in the later sm_2024-05-28.pdf,
    # confirmed by hand to be a genuine revision in the later filing, not an extraction error),
    # prefer the MOST RECENT report, matching or_osh.py's own explicit "keep the value from the
    # most recent report" convention -- a later court filing revising an earlier one is presumed
    # to reflect more complete information, not the other way around. Previously this file used
    # a plain stable-sort (chronologically-FIRST report silently won every such tie, the opposite
    # convention, with zero visibility into that it was even happening -- see the conflict log
    # above, added alongside this fix).
    #
    # Log every conflict this resolves, matching or_osh.py's build() -- silently resolving
    # disagreements between report vintages was flagged as a real gap (this file previously had
    # no visibility into 16 such disagreements at all, some genuine source-document revisions,
    # some the bugs fixed elsewhere in this file).
    for (period, tier, metric), g in df.groupby(["period", "tier", "metric"]):
        vals = g["value"].unique()
        if len(vals) > 1:
            detail = ", ".join(f"{v} ({r})" for v, r in zip(g["value"], g["report"]))
            print(f"  [conflict] ({period}, tier{tier}, {metric}): {detail}")
    df = df.sort_values(["period", "tier", "metric", "has_star", "report"],
                         ascending=[True, True, True, True, False])
    return (df.drop_duplicates(["period", "tier", "metric"])
              .drop(columns="has_star")
              .sort_values(["metric", "tier", "period"]))

if __name__ == "__main__":
    df = build()
    out = C.DERIVED / "co_special_master.parquet"
    df.to_parquet(out, index=False)
    print(f"\nsaved {out} ({len(df)} rows)\n")
    print(df.to_string(index=False))
    print("\n=== FACE-VALIDITY CHECKS (vs the report we read) ===")
    wt = df[df.metric == "tier_wait_days_restoration"]
    ct = df[df.metric == "tier_waitlist_count"]
    t1 = wt[wt.tier == 1]["value"]; t2 = wt[wt.tier == 2]["value"]
    c2 = ct[ct.tier == 2]["value"]
    print(f"  Tier-1 wait days mostly <=~11 (under/near 7-day limit): {'PASS' if (t1 <= 11).mean() > 0.7 else 'REVIEW'} (vals {sorted(t1.round(1).tolist())[:6]})")
    print(f"  Tier-2 wait days mostly >49 (over limit):               {'PASS' if (t2 > 49).mean() > 0.6 else 'REVIEW'} (vals {sorted(t2.round(1).tolist())[:6]})")
    print(f"  Tier-2 waitlist counts ~100-130:                        {'PASS' if c2.between(80,140).mean() > 0.6 else 'REVIEW'} (vals {sorted(c2.astype(int).tolist())[:6]})")
