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
8 more (2023-2026) were sourced directly from CourtListener's RECAP storage CDN (free, not
paywalled, just not linked from the docket's own web page). 2 files in this glob are not actually
special-master quarterly reports (the Consent Decree filing itself, a 2019 status letter) and
produce 0 rows, printing a [WARN] naming which, rather than silently vanishing (see `build()`); a
3rd file has a broken/cid-encoded font pdfplumber can't read directly, but is OCR-recovered
instead of vanishing (see `_ocr_recover_sm_2024_11_28`).
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
# "Recent Wait Times for Inpatient Restoration" table row, e.g. "Jul 2024 26 76 63.5 110.4
# 25** 68**" -- month-per-ROW, Tier1/Tier2-per-COLUMN, the opposite orientation of every other
# table this file parses (see parse_report's own comment where this is first used). Module-level
# so both the plain-text path (parse_report) and the OCR path (_ocr_recover_sm_2024_11_28, for
# the one report whose page carrying this table is cid-encoded) share one definition.
RECENT_WAIT_RE = re.compile(
    r'^([A-Za-z]+)\s+(\d{4})\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\*{0,3}\s+(\d+)\*{0,3}\s*$')

# Trailing [-–—]? added 2026-09-11 (adversarial review of the is_multi_month_avg disclosure fix,
# meta/docs/data_validation_2026-09-11/): sm_2025-05-28.pdf's range-column headers glue the dash
# directly onto the month with no space ("May–", "Aug–" -- pdfplumber extracts it as one word,
# confirmed via char-code inspection: U+2013 EN DASH appended, no space token), unlike every other
# range header in the corpus ("Nov 24 - Jan 25", where the dash is its own word). The un-widened
# regex silently dropped "May–"/"Aug–" from the header band entirely, leaving only the OTHER month
# in a 2-month range visible -- distinct_months collapsed to 1, so is_range came out False for a
# genuine 3-month-average reading (2024-07 and 2024-10, both tiers, on that report). Confirmed via
# a corpus-wide scan that this exact glued-dash pattern occurs on only this one page. Doesn't
# affect the PERIOD itself (date resolution already takes the LAST month found, which was never
# the dropped one) -- confirmed no value/period changed, only the disclosure flag for these 4 rows.
_MONTH_WORD = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?[-–—]?$', re.I)
# "(?:/\d{2})?" added 2026-09-11 (public-repo audit, meta/docs/data_validation_2026-09-11/
# co_pass1_findings.md): sm_109331.pdf's "Nov – Jan 2019/20" range header prints its completing
# year as a single glued "2019/20" token, not the "2020"-only form every other range header in the
# corpus uses -- confirmed via direct word-coordinate dump (one token, text="2019/20", no space).
# The un-widened regex didn't match it at all (not even partially), so `years` came back empty for
# this column and _header_periods_for_row silently gave up on it (`not years: periods.append(None)`)
# -- this is a strict widening (new alternative branch only), the two pre-existing year forms are
# unchanged, so no other column in the corpus is affected (confirmed via the sm_109331.pdf-only
# corpus-wide extraction diff below).
_YEAR_WORD = re.compile(r'^(\d{4}(?:/\d{2})?|\d{2})$')
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
    # Assign each header word to its NEAREST cell (by x0), not to every cell within 45px --
    # ADDED 2026-09-11 (public-repo audit, meta/docs/data_validation_2026-09-11/co_pass1_findings.md,
    # caught during the is_multi_month_avg flag fix, not in the audit itself). sm_109331.pdf's
    # columns sit only ~50px apart (narrower than the rest of the corpus, where 68-75px spacing
    # meant a 45px both-sides radius never bridged two columns) -- the old "within 45px of MY OWN
    # x0" test let a single header word (e.g. "Mar") satisfy the radius test for BOTH the Feb
    # column (44.7px away) and the Mar column (0.5px away) at once, so the Feb cell picked up
    # "Mar" as its own last/bottom-most month and got mislabeled 2020-03 with a spurious is_range.
    # Nearest-cell assignment can't double-count a word this way regardless of absolute column
    # spacing, and still keeps a genuine two-word range header (e.g. "May 2023" / "Jul 2023"
    # wrapped across two lines) on ONE cell, since both words sit far closer to their own range
    # column's x0 than to either neighbour's.
    cell_x0s = [c['x0'] for c in cells]
    assigned = [[] for _ in cells]
    for w2 in band:
        idx = min(range(len(cell_x0s)), key=lambda i: abs(cell_x0s[i] - w2['x0']))
        if abs(cell_x0s[idx] - w2['x0']) < 45:
            assigned[idx].append(w2)
    for c, near_words in zip(cells, assigned):
        near = sorted(near_words, key=lambda w2: (w2['top'], w2['x0']))
        months = [w2['text'] for w2 in near if _MONTH_WORD.match(w2['text'])]
        years = [w2['text'] for w2 in near if _YEAR_WORD.match(w2['text'])]
        if not months or not years:
            periods.append(None)
            is_range.append(False)
            continue
        mon = months[-1][:3].lower()
        y = years[-1]
        if '/' in y:
            # "2019/20" = a range crossing a calendar-year boundary (e.g. "Nov - Jan 2019/20" =
            # Nov 2019 through Jan 2020) -- but only when the range genuinely straddles Dec/Jan.
            # HARDENED 2026-09-12 (3rd re-audit pass, meta/docs/data_validation_2026-09-12_pass3/
            # co_lensB_date_arithmetic.md): the previous version unconditionally took the SECOND
            # year half, correct for this corpus's only instance (Nov-Jan, a real rollover) but a
            # latent landmine -- a hypothetical same-year range like "Aug - Oct 2019/20" (both
            # months in the FIRST year) would have silently misdated as 2020-08/2020-10 instead
            # of 2019-08/2019-10. Now checks whether the range's own first month is numerically
            # AFTER its last month (the only shape a genuine rollover can take) before trusting
            # the second half; a single-month match (no second month to compare) keeps the
            # already-proven-correct second-half behavior as a documented fallback.
            first_mon = MON[months[0][:3].lower()] if len(months) > 1 else None
            if first_mon is not None and first_mon <= MON[mon]:
                yr = int(y.split('/')[0])          # same-year range, e.g. "Aug - Oct 2019/20"
            else:
                yr = 2000 + int(y.split('/')[1])   # genuine Dec/Jan-style rollover
        else:
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
    """Return ordered list of 'YYYY-MM' for the data columns -- each token must carry its OWN
    explicit 4-digit year; a year is never propagated from a neighboring token. FIXED 2026-09-12
    (3rd re-audit pass, meta/docs/data_validation_2026-09-12_pass3/co_lensB_date_arithmetic.md):
    the previous version forward/back-filled a missing year from the nearest explicit year found
    ANYWHERE in the header, with no notion of month order or which columns are actually related --
    reproduced directly with two verbatim headers from this corpus, both silently producing a
    plausible but WRONG year (a stray "March 2019" baseline column's year leaking forward onto a
    genuinely ~2023/2024 range column dozens of characters later; and the reverse, a later token's
    year propagating backward onto an earlier one 6 years off). Confirmed empirically (by
    instrumenting parse_report and logging which branch every row in every corpus file actually
    took) that this fallback is currently dead code for anything that ships today -- the
    positional word-coordinate axis and sibling-tier borrowing always supersede it first -- but
    its safety was incidental (coverage by other mechanisms), not structural, so this closes the
    silent-wrong-answer trap outright rather than leaving it in place. A token with no year of its
    own now correctly returns None (an honest "can't resolve this one," matching this file's
    existing "never guess a partial axis" convention) instead of a confident-looking wrong period.
    Stops before deadline columns (those carry an explicit year but are handled by the caller via 'days')."""
    toks = MONTH_TOK.findall(line)
    if not toks:
        return []
    periods = []
    for mon, y in toks:
        periods.append(f"{int(y):04d}-{MON[mon[:3].lower()]:02d}" if y else None)
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
            # is_range used to be fully discarded here on the reasoning that a multi-month range
            # column is an expected, already-disclosed convention for wait-day rows (its own END
            # month), not a defect. ADDED 2026-09-11 (meta/docs/data_validation_2026-09-11/
            # co_pass1_findings.md): "already-disclosed" turned out not to be true -- the shipped
            # CSV never actually said which periods are a true single month vs. a rolling average,
            # so a reader had no way to tell. Kept (not discarded) purely to EXPOSE that fact as a
            # new column below -- deliberately NOT used to change which value ships (see build()):
            # a direct check of the report's own prose (sm_2024-02-28.pdf p.13: "Tier 1 ... 92 days
            # on average between November 2023 - January 2024") confirmed the report treats the
            # rolling average as ITS OWN authoritative headline figure, not a lesser fallback -- so
            # preferring the single-month reading instead would have been a real, wrong value
            # change disguised as a fix. Disclosure only.
            word_periods, word_is_range = (_header_periods_for_row(words, word_top, word_x1, n_expected=len(cells),
                                                                     exclude_tops=other_tops)
                                            if word_top is not None else (None, None))
            raw.append(dict(tier=tier, metric=metric, cells=cells, periods=periods, word_is_range=word_is_range,
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

    # Sibling-tier word_periods borrowing -- ADDED 2026-09-11 (public-repo audit,
    # meta/docs/data_validation_2026-09-11/co_pass1_findings.md): confirmed root cause of a
    # "Tier-2 blank instead of False/True" is_multi_month_avg bug in 3 files (6 rows). A
    # range-header column that wraps its completing month onto a SECOND physical text line
    # (e.g. sm_2023-11-28.pdf p.13's "May 2023 -" / "Jul 2023") sits far enough above a
    # TIER-2 row that the existing 60px header search band -- deliberately kept narrow after
    # an earlier widening (60->75px) caused a real regression on unrelated count-table rows,
    # reverted the same session -- doesn't reach it, while the closer TIER-1 row's own band
    # does. Rather than widen the band again, borrow the already-correctly-resolved word-axis
    # from the sibling tier row in the SAME table (same page, same footnote grouping, same
    # cell count -- these three together are the same signal `_header_periods_for_row` itself
    # relies on to mean "same table"): same fix pattern as wa_trueblood.py's _parse_grid
    # borrowing a sibling row's column layout for an all-n/a row.
    sibling_wp = {}
    for r in raw:
        if r["metric"] == "tier_wait_days_restoration":
            wp, wir = r.get("word_periods"), r.get("word_is_range")
            if wp and len(wp) == len(r["cells"]) and all(wp):
                sibling_wp[(r["page"], r["has_star"], len(r["cells"]))] = (wp, wir)

    rows = []
    def emit(period, tier, metric, value, has_star, pdf_page, is_multi_month_avg=None):
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
                         pdf_page=pdf_page, is_multi_month_avg=is_multi_month_avg))
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
                    emit(p, r["tier"], r["metric"], c, r["has_star"], r["page"] + 1, is_multi_month_avg=False)
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
        wir = r.get("word_is_range")
        # is_multi_month_avg is DISCLOSURE ONLY here -- added 2026-09-11, see the word_is_range
        # capture above for why. It never affects which value ships (build()'s own selection logic
        # is untouched); it only tells a reader, per shipped row, whether that row's own reading
        # is a true single month or a multi-month rolling average dated to its end month.
        if wp and len(wp) == len(r["cells"]) and all(wp):
            use = [p for p, c in zip(wp, r["cells"]) if not _isna(c)]
            rngs = ([rng for rng, c in zip(wir, r["cells"]) if not _isna(c)]
                    if wir and len(wir) == len(r["cells"]) else [None] * len(use))
        elif r["periods"] and len(r["periods"]) == len(r["cells"]) and all(r["periods"]):
            use = [p for p, c in zip(r["periods"], r["cells"]) if not _isna(c)]
            # A row that reaches this branch has, by construction, one header token per cell (see
            # the word_periods branch's own docstring for why a genuine range header can't reach
            # here) -- so False is a real fact about this row, not a guess.
            rngs = [False] * len(use)
        elif (r["page"], r["has_star"], len(r["cells"])) in sibling_wp:
            # This row's OWN header axis (word-based and text-line) both failed to resolve, but
            # the opposite-tier row in the SAME table (same page/footnote-grouping/cell-count)
            # already resolved cleanly -- borrow its axis. See sibling_wp's own comment above for
            # why this is needed (band-width asymmetry between tier rows) and why it's safe (the
            # sibling's periods are read from the identical shared column headers, not guessed).
            wp2, wir2 = sibling_wp[(r["page"], r["has_star"], len(r["cells"]))]
            use = [p for p, c in zip(wp2, r["cells"]) if not _isna(c)]
            rngs = ([rng for rng, c in zip(wir2, r["cells"]) if not _isna(c)]
                    if wir2 and len(wir2) == len(r["cells"]) else [None] * len(use))
        elif r["tier"] in count_periods:
            cp = count_periods[r["tier"]]
            use = cp[-len(data):] if len(cp) >= len(data) else cp
            data = data[-len(use):]
            # This fallback borrows the count table's period LABELS and has no way to check
            # whether its OWN wait-day cell is a true single month or a range -- None (unknown),
            # not a guessed True/False, is the honest disclosure here.
            rngs = [None] * len(use)
        else:
            continue
        for p, v, rng in zip(use, data, rngs):
            emit(p, r["tier"], r["metric"], v, r["has_star"], r["page"] + 1, is_multi_month_avg=rng)

    # "Recent Wait Times for Inpatient Restoration" table -- FIXED 2026-09-12 (3rd re-audit
    # pass, meta/docs/data_validation_2026-09-12_pass3/co_lensA_blind_rebuild.md). Starting with
    # sm_2024-08-28.pdf, this report switched its "Key Metric" wait-days table from the older
    # 4-column layout (1 composite quarter-range column + 3 single months) to a 3-row,
    # month-per-row layout listing the 3 most recent individual months directly (no combined
    # column at all) -- a genuinely different table ORIENTATION (month rows, Tier1/Tier2
    # columns) than every other table this file parses (which is always Tier-N-per-ROW, matched
    # by TIER_ROW above). These lines don't start with "Tier", so the main loop never reaches
    # them -- 10 genuine single-month tier_wait_days_restoration readings were silently never
    # captured at all (confirmed: 2024-05/06/08/09/11/12, 2025-02/03, 2026-02/03).
    #
    # The NEWEST of the 3 listed months is always the report's own current quarter's END month --
    # confirmed directly (sm_2024-08-28.pdf p.12: "Tier 1 detainees ... 69 days on average
    # between May - July 2024" -- the report's OWN prose treats the 3-month rolling composite,
    # not this table's own single-month Jul-2024 reading of 63.5, as its authoritative headline
    # figure for that quarter-end month -- the SAME established convention already confirmed for
    # the older 4-column format's own quarter-range column). So this block only fills a
    # period+tier not already emitted above -- it never overrides the quarter-end row the main
    # wait-days path already produced from the separate rolling-average table, preserving that
    # convention rather than re-litigating it (see this file's own composite-vs-single-month
    # revert history for why guessing wrong here is a real, not hypothetical, risk).
    covered = {(r["period"], r["tier"]) for r in rows if r["metric"] == "tier_wait_days_restoration"}
    for page_idx, (text, words) in enumerate(pages):
        for ln in text.split("\n"):
            m = RECENT_WAIT_RE.match(ln.strip())
            if not m:
                continue
            mon = m.group(1)[:3].lower()
            if mon not in MON:
                continue
            period = f"{int(m.group(2)):04d}-{MON[mon]:02d}"
            for tier, days in ((1, m.group(5)), (2, m.group(6))):
                if (period, tier) in covered:
                    continue
                emit(period, tier, "tier_wait_days_restoration", days, False, page_idx + 1,
                     is_multi_month_avg=False)
                covered.add((period, tier))
    return rows

def _ocr_recover_sm_2024_11_28(path: Path, sha: str) -> list[dict]:
    """OCR-based recovery, ONLY for sm_2024-11-28.pdf's page-14 waitlist table -- ADDED
    2026-09-11 (public-repo audit, meta/docs/data_validation_2026-09-11/co_pass1_findings.md).
    This file's page 14 embeds a subsetted font with no usable ToUnicode CMap -- pdfplumber's
    text layer returns raw (cid:N) glyph codes for every character on the page (confirmed
    directly: the page renders correctly as an image, it's vector text with a broken text
    layer, not a scan, which is why OCR on a high-resolution render works reliably here).
    Cross-validated independently by the audit itself: the average of the 3 recovered months
    (16.67/196.67) matches the "Aug-Oct24" 3-month-avg column printed VERBATIM in the NEXT
    report (sm_2025-02-28.pdf, p.14) -- these are genuine, internally-consistent values, not
    an OCR artifact.

    Deliberately narrow, not a general OCR fallback: parses ONLY the one known table shape on
    page 14 of this ONE file (gated on the exact filename below), so no other file in the
    corpus -- even a future one with a similarly broken font -- can silently start routing
    through here with a different, unverified table shape. If the OCR text ever stops matching
    the expected "Tier N  N/A  <range>  <int>  <int>  <int>" shape (e.g. a re-download changes
    the file), this returns nothing and build()'s existing [WARN] path stands unchanged --
    never guesses a partial or malformed row.
    """
    import pytesseract
    out = []
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[13]  # printed page 14 -- confirmed via the audit's own direct read
        text = pytesseract.image_to_string(page.to_image(resolution=400).original, config="--psm 6")
    for tier in (1, 2):
        m = re.search(rf'Tier\s*{tier}\s+N/?A\s+[\d.]+\s+(\d+)\s+(\d+)\s+(\d+)', text, re.I)
        if not m:
            continue
        for period, val in (("2024-08", m.group(1)), ("2024-09", m.group(2)), ("2024-10", m.group(3))):
            out.append(dict(state="CO", period=period, tier=tier, metric="tier_waitlist_count",
                             value=float(val), report=path.name, source_sha=sha, has_star=False,
                             pdf_page=14, is_multi_month_avg=False))

    # Page 11's "Recent Wait Times" table -- ADDED 2026-09-12 (3rd re-audit pass, meta/docs/
    # data_validation_2026-09-12_pass3/co_lensA_blind_rebuild.md). Same cid-encoded-font problem
    # as page 14 above, same OCR fix. All 3 months (Aug/Sep/Oct 2024) are emitted here, including
    # the quarter-boundary month (Oct) -- deliberately NOT hand-skipped the way parse_report()'s
    # own plain-text path skips it, because that skip exists only to prevent ONE report's two
    # OWN tables (this one and its quarterly-composite table on another page) from both
    # contributing a same-recency row for the same period. This whole report contributes
    # nothing else at all (both pages 11 and 14 are cid-encoded), so there's no such self-
    # conflict here -- only a cross-report conflict with whichever LATER report's own quarterly
    # table also covers Aug-Oct24, which build()'s existing recency-based dedup already resolves
    # correctly (confirmed: sm_2025-05-28.pdf's 40.3/95.3 already wins for 2024-10 today).
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[10]  # printed page 11
        text2 = pytesseract.image_to_string(page.to_image(resolution=400).original, config="--psm 6")
    for ln in text2.split("\n"):
        m = RECENT_WAIT_RE.match(ln.strip())
        if not m:
            continue
        mon = m.group(1)[:3].lower()
        if mon not in MON:
            continue
        period = f"{int(m.group(2)):04d}-{MON[mon]:02d}"
        for tier, days in ((1, m.group(5)), (2, m.group(6))):
            out.append(dict(state="CO", period=period, tier=tier, metric="tier_wait_days_restoration",
                             value=float(days), report=path.name, source_sha=sha, has_star=False,
                             pdf_page=11, is_multi_month_avg=False))
    return out

def build() -> pd.DataFrame:
    rows = []
    for p in sorted((C.RAW / "co").glob("sm_*.pdf")):
        rr = parse_report(p)
        if not rr and p.name == "sm_2024-11-28.pdf":
            rr = _ocr_recover_sm_2024_11_28(p, _util.sha12(p))
            if rr:
                print(f"  [ocr-recovered] {p.name}: {len(rr)} Tier datapoints (page 14, cid-encoded font)")
                rows += rr
                continue
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
    # above), prefer the unfootnoted row. Within a tie on that (both footnoted, or both not),
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
