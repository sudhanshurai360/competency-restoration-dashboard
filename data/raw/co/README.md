# Colorado — source documents

**11 PDF files bundled + 3 withheld pending confirmation — two distinct sources with different
rights bases, read both sections.**

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
question — and leans toward "no" here specifically: `sm_109305.pdf` (the consent decree itself)
states the Special Master "shall be engaged and paid for by the Department" — i.e., paid by the
state defendant, not the federal government, which weighs against treating the report as a federal
employee's work product. We do **not** claim these are public domain. Redistribution instead rests
on **fair use**: non-commercial, public-interest reproduction of documents with no market this
could substitute for, already freely public via RECAP, backed by established practice —
CourtListener, RECAP, the Internet Archive, and Justia all redistribute filings like these at scale
on the same basis, and these specific files were sourced from RECAP for exactly that reason. (One
case sometimes cited for this kind of use, *White v. West Publishing Corp.*, S.D.N.Y. 2014, turned
specifically on West/Lexis *transforming* litigants' briefs into a searchable database — a
different fact pattern from this archive's verbatim, unmodified redistribution for pipeline
reproducibility. It supports the general direction of this argument, not a precise match, and isn't
leaned on here as if it were on point.)

## 2. Colorado Joint Budget Committee documents — PDFs WITHHELD PENDING CONFIRMATION

**`jbc_memo.pdf`, `fy2024-25_humbrf2.5.pdf`, and `fy2025-26_humbrf1.5.pdf` are NOT bundled in this
folder right now.** This is the one document type in this archive resting on fair use alone with no
public-domain or agency-license backdrop behind it (see "Rights" below) — rather than publish the
PDFs on that basis alone, we're holding them back until JBC staff have had a chance to confirm no
objection to non-commercial reproduction (a real, findable contact — see "Where these came from").
**What's still here despite the withheld PDFs**: the extracted data itself
(`data/derived/colorado_jbc.csv`, `co_jbc_snapshots.parquet`) and every citation to these documents
on the dashboard remain fully included — factual figures extracted from a public document are a
different, much lower-risk thing to publish than the document itself, regardless of the source
PDF's own status. `python src/co_jbc.py` will not currently reproduce this dataset from scratch in
this archive (its 3 source PDFs aren't here) until the PDFs are added back; the already-derived CSV
output is provided as-is in the meantime. `SOURCES.csv` still carries the full metadata (filename,
URL, hash) for these 3 files, for citation purposes — that's just information about where the
originals live, not a redistribution of them.

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

Worth noting, as a favorable (not dispositive) analogy: the reasoning behind the 2016 CRS
copyright-waiver decision — that the content is the product of state-paid legislative staff and is
already freely posted on the General Assembly's own site, so there's no private contractor's
proprietary editorial layer to protect — applies with at least equal force to a JBC staff memo as
it did to the statutes themselves. That's not a formal legal opinion and doesn't change the
"fair use only" bottom line above, but it's a real, favorable data point this document didn't
previously mention.

Because this is genuinely the weakest-footing document type in this whole archive, and because JBC
memos name a real, findable staff contact (`jbc_memo.pdf` itself lists the author and a phone
number), a direct check-in with JBC staff confirming no objection to non-commercial reproduction is
worth doing before treating this basis as final — see this project's own outreach notes for status.

## Both categories

- The 11 bundled Special Master PDFs are redistributed **unchanged**, so the extraction pipeline
  (`../../../src/co_special_master.py`) is independently reproducible from its exact inputs
  (`python src/verify.py` from the archive root). The 3 JBC PDFs are withheld per above; their
  already-derived data is included instead.
- Not covered by this archive's own `LICENSE` (MIT) or `LICENSE-DATA` (CC-BY-4.0) — see the
  archive-root `NOTICE` and `SAFETY_REVIEW.md`.
- **Official figures remain those of the Special Master and the Colorado Joint Budget Committee.**
  Contact `me@sudhanshurai.org` for corrections or removal requests from a rights holder.

## Full file list

11 files are bundled in this folder (Special Master reports); the 3 JBC files are withheld pending confirmation (see above) — linked here for citation purposes only, not bundled as PDFs.

- `fy2024-25_humbrf2.5.pdf` — [source](https://web.archive.org/web/20250224084723/http://leg.colorado.gov/sites/default/files/fy2024-25_humbrf2.5.pdf) — **withheld, not bundled**
- `fy2025-26_humbrf1.5.pdf` — [source](https://web.archive.org/web/20250407090012/http://leg.colorado.gov/sites/default/files/fy2025-26_humbrf1.5.pdf) — **withheld, not bundled**
- `jbc_memo.pdf` — [source](https://leg.colorado.gov/agencies/joint-budget-committee) *(general landing/docket page, not a direct per-file link)* — **withheld, not bundled**
- `sm_109305.pdf` — [source](https://www.courtlistener.com/docket/4176801/center-for-legal-advocacy-v-barnes/) *(general landing/docket page, not a direct per-file link)*
- `sm_109327.pdf` — [source](https://www.courtlistener.com/docket/4176801/center-for-legal-advocacy-v-barnes/) *(general landing/docket page, not a direct per-file link)*
- `sm_109331.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.197.0.pdf)
- `sm_2023-11-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.280.0.pdf)
- `sm_2024-02-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.284.0.pdf)
- `sm_2024-05-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.290.0.pdf)
- `sm_2024-08-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.296.0.pdf)
- `sm_2024-11-28.pdf` — [source](https://www.courtlistener.com/docket/4176801/center-for-legal-advocacy-v-barnes/) *(general landing/docket page, not a direct per-file link)*
- `sm_2025-02-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.306.0.pdf)
- `sm_2025-05-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.310.0.pdf)
- `sm_2026-05-28.pdf` — [source](https://storage.courtlistener.com/recap/gov.uscourts.cod.128117/gov.uscourts.cod.128117.341.0_1.pdf)
