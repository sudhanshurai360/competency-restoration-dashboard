# Colorado — source documents

**14 PDF files bundled — two distinct sources with different rights bases, read both sections.**

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

## 2. Colorado Joint Budget Committee documents — PDFs INCLUDED, PERMISSION CONFIRMED

**`jbc_memo.pdf`, `fy2024-25_humbrf2.5.pdf`, and `fy2025-26_humbrf1.5.pdf` are bundled in this
folder.** These were held back from the initial release while their rights basis was the weakest
in this archive (see "Rights" below) — no court-filing redistribution precedent, no public-domain
or agency-license backdrop. Rather than publish on fair use alone with nothing else behind it, JBC
staff were asked directly (see "Confirmation received," below) before including them.
**JBC staff confirmed in writing on 2026-09-10** that these are public documents and free to
include — this is now the *strongest* rights basis of any document type in this archive: direct,
explicit authorization from the originating office, not an inference from fair-use doctrine.
`python src/co_jbc.py` reproduces this dataset from scratch in this archive; all 3 source PDFs are
present.

Staff budget briefings produced by the Colorado General Assembly's Joint Budget Committee (JBC)
staff, hosted at `leg.colorado.gov`.

**Where these came from**: the two `fy*.pdf` files have confirmed Wayback Machine snapshot URLs in
`SOURCES.csv` (`leg.colorado.gov` blocks direct scripted downloads, so Wayback was used instead).
`jbc_memo.pdf` was searched for but never found archived anywhere with confidence — its `SOURCES.csv`
entry points to the JBC's general publications page instead, not a specific archived copy.

**Rights — history of the analysis, kept for the record**: Colorado's legislative branch has a
documented history of *asserting* copyright over its own work product (it claimed copyright in the
Colorado Revised Statutes themselves from 1970 until a deliberate 2016 policy reversal waived that
claim — for the statutes only, not JBC materials specifically). No public-domain dedication or
open-redistribution policy was found for JBC publications independent of direct confirmation. Prior
to confirmation, redistribution would have rested on **fair use** alone — factual, functional
budget-briefing content, redistributed unchanged for non-commercial accountability research, no
market for reselling them, no endorsement implied — a reasonable position, but not as
well-established or battle-tested as the fair-use basis for the federal court filings above.

Worth noting, as a favorable (not dispositive) analogy that turned out to be moot once direct
confirmation arrived: the reasoning behind the 2016 CRS copyright-waiver decision — that the
content is the product of state-paid legislative staff and is already freely posted on the General
Assembly's own site, so there's no private contractor's proprietary editorial layer to protect —
applies with at least equal force to a JBC staff memo as it did to the statutes themselves.

**Confirmation received.** Because this was genuinely the weakest-footing document type in this
whole archive, and because JBC memos name a real, findable staff contact (`jbc_memo.pdf` itself
lists the author and a phone number), an email was sent to JBC's general staff office
(jbc.ga@coleg.gov) on 2026-09-07 asking for confirmation of no objection to non-commercial
reproduction. **Jessi Neuberg, JBC Staff, replied on 2026-09-10: "Yes, all of our documents are
public documents, so you are free to include them."** The 3 PDFs are bundled accordingly. Full
correspondence preserved in the private working tree's `dashboard_data/publish_permission/`
outreach log (not part of this public repo).

## Both categories

- All 14 bundled PDFs (11 Special Master reports + 3 JBC documents) are redistributed
  **unchanged**, so both extraction pipelines (`../../../src/co_special_master.py`,
  `../../../src/co_jbc.py`) are independently reproducible from their exact inputs
  (`python src/verify.py` from the archive root).
- Not covered by this archive's own `LICENSE` (MIT) or `LICENSE-DATA` (CC-BY-4.0) — see the
  archive-root `NOTICE` and `SAFETY_REVIEW.md`.
- **Official figures remain those of the Special Master and the Colorado Joint Budget Committee.**
  Contact `me@sudhanshurai.org` for corrections or removal requests from a rights holder.

## Full file list

All 14 files are bundled in this folder (11 Special Master reports + 3 JBC documents).

- `fy2024-25_humbrf2.5.pdf` — [source](https://web.archive.org/web/20250224084723/http://leg.colorado.gov/sites/default/files/fy2024-25_humbrf2.5.pdf)
- `fy2025-26_humbrf1.5.pdf` — [source](https://web.archive.org/web/20250407090012/http://leg.colorado.gov/sites/default/files/fy2025-26_humbrf1.5.pdf)
- `jbc_memo.pdf` — [source](https://leg.colorado.gov/agencies/joint-budget-committee) *(general landing/docket page, not a direct per-file link)*
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
