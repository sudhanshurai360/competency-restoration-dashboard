# Colorado — source documents

**14 files, two distinct sources with different rights bases — read both sections.**

## 1. Special Master reports (`sm_*.pdf`, 11 files)

Quarterly (formerly monthly) reports to the court from the court-appointed Special Master in
*Center for Legal Advocacy v. Barnes*, Case No. 1:11-cv-02285-NYW (D. Colo.) — a federal consent
decree setting tiered restoration-admission deadlines. Filed on the federal docket and retrieved
via CourtListener/RECAP (the Free Law Project's public archive of PACER records).

**Where these came from**: `SOURCES.csv` at the archive root (filter `state == co`) has the exact
URL, byte size, and SHA-256 for every file that has a confirmed one — mostly
`storage.courtlistener.com/recap/gov.uscourts.cod.128117/...`. Three early files
(`sm_109305.pdf`, `sm_109327.pdf`, `sm_2024-11-28.pdf`) have no confirmed per-file URL; the general
case docket is linked instead (`hub-only` in `SOURCES.csv`).

**Rights**: these are federal court filings, not our own work. Whether a court-appointed special
master's report is itself a public-domain "work of the U.S. Government" is a genuinely open legal
question (special masters are typically compensated by the parties, not federal employees, unlike
the narrower case of a sitting magistrate judge serving in that role) — we do **not** claim these
are public domain on that basis. Redistribution instead rests on **fair use**: verbatim
redistribution of public federal court filings, for non-commercial, public-interest compliance
tracking, is well-supported by both case law (e.g. *White v. West Publishing Corp.*, S.D.N.Y.
2014, upholding fair use for wholesale redistribution of litigants' own filings) and established
practice — CourtListener, RECAP, the Internet Archive, and Justia all redistribute filings like
these at scale on the same basis, and these specific files were sourced from RECAP for exactly
that reason.

## 2. Colorado Joint Budget Committee documents (`jbc_memo.pdf`, `fy2024-25_humbrf2.5.pdf`,
`fy2025-26_humbrf1.5.pdf`, 3 files)

Staff budget briefings produced by the Colorado General Assembly's Joint Budget Committee (JBC)
staff, hosted at `leg.colorado.gov`.

**Where these came from**: the two `fy*.pdf` files have confirmed Wayback Machine snapshot URLs in
`SOURCES.csv` (`leg.colorado.gov` blocks direct scripted downloads, so Wayback was used instead).
`jbc_memo.pdf` was searched for but never found archived anywhere with confidence — its `SOURCES.csv`
entry points to the JBC's general publications page instead, not a specific archived copy.

**Rights — weaker footing than the Special Master reports, said plainly**: Colorado's legislative
branch has a documented history of *asserting* copyright over its own work product (it claimed
copyright in the Colorado Revised Statutes themselves from 1970 until a deliberate 2016 policy
reversal waived that claim — for the statutes only, not JBC materials specifically). No
public-domain dedication or open-redistribution policy was found for JBC publications. We
redistribute these documents relying on **fair use** alone — factual, functional budget-briefing
content, redistributed unchanged for non-commercial accountability research, no market for
reselling them, no endorsement implied — which we believe is a reasonable position, but it is not
as well-established or battle-tested as the fair-use basis for the federal court filings above.

## Both categories

- Redistributed **unchanged**, solely so the extraction pipeline in this archive
  (`../../../src/co_special_master.py`, `../../../src/co_jbc.py`) is independently reproducible from its
  exact inputs (run `python src/verify.py` from the archive root).
- Not covered by this archive's own `LICENSE` (MIT) or `LICENSE-DATA` (CC-BY-4.0) — see the
  archive-root `NOTICE` and `SAFETY_REVIEW.md`.
- **Official figures remain those of the Special Master and the Colorado Joint Budget Committee.**
  Contact `me@sudhanshurai.org` for corrections or removal requests from a rights holder.
