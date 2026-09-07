# California — source documents

**9 files.** California Department of State Hospitals (DSH) budget "Estimate" documents,
submitted to the Department of Finance — the Governor's Budget (~January) and May Revision (~May)
each year. California's binding standard comes from a state-court mandate, *Stiavetti v.
Clendenin*, not a federal decree.

## Where these came from

Every file's exact source URL, byte size, and SHA-256 hash is recorded in `SOURCES.csv` at the
archive root (filter `state == ca`). Eight files were retrieved and hash-verified via Wayback
Machine snapshots (one, the most recent, via its live URL — too recent for Wayback to have crawled
yet) of `dsh.ca.gov/About_Us/docs/{filename}`. One file (`gov2026-27.pdf`) has no confirmed
per-file URL — it's included because it's part of the same downloaded corpus, but it doesn't
contribute any figure to this project's derived dataset (its one relevant reading uses a
budget-cycle-relative date phrasing this project's extraction code deliberately doesn't resolve to
a calendar month — see `california.html`'s own methodology note on `competencyrestoration.org`);
the archive root's general `dsh.ca.gov/About_Us/` page is linked instead.

## Rights — public domain

**Said precisely, not glossed over**: DSH's own site footer (dsh.ca.gov, where these 9 documents
are actually hosted) displays only a bare, unelaborated "Copyright © State of California" notice —
no separate Conditions of Use page exists on dsh.ca.gov itself, and no license terms or restriction
accompany that notice. The portal-level ca.gov Conditions of Use states California executive-branch
content is public domain by default —

> "information presented on this website, unless otherwise indicated, is considered in the public
> domain. It may be distributed or copied as permitted by law."
> — ca.gov Conditions of Use

— and that language is independently confirmed live on several other executive-branch sites (e.g.
gov.ca.gov, oag.ca.gov, dhcs.ca.gov), but it could not be independently confirmed as published on,
or adopted by, dsh.ca.gov specifically. Rather than assume DSH has adopted a policy it doesn't
itself display, the actual basis for treating these documents as public domain rests on a published,
precedential California Court of Appeal decision — *County of Santa Clara v. Superior Court
(California First Amendment Coalition)*, 170 Cal.App.4th 1301 (2009) — holding a California public
agency has no statutory authority to invoke copyright to restrict redistribution of a public record
absent specific statutory authorization. (That case concerned a GIS basemap, not budget documents
specifically — extending its reasoning here is a straightforward analogical step, not a strained
one, since nothing in the case's reasoning is basemap-specific and a budget "Estimate" document is
squarely a Public Records Act-covered record like the basemap was, but it's worth being explicit
that the case itself didn't address this document type.) That statutory-authority gap is confirmed
current: AB 2880 (2016), which would have given agencies exactly the copyright-assertion power
*Santa Clara* forecloses, had that language stripped by the Senate before passage. So: a bare,
unelaborated footer notice, without more, does not create an enforceable restriction on these
documents — particularly since no restriction, license, or copyright notice of any kind appears on
the 9 files themselves (confirmed by direct inspection of each).

- We redistribute them **unchanged**, solely so the extraction pipeline in this archive
  (`../../../src/ca_dsh.py`) is independently reproducible from its exact inputs (run
  `python src/verify.py` from the archive root).
- Not covered by this archive's own `LICENSE` (MIT, for our code) or `LICENSE-DATA` (CC-BY-4.0, for
  our derived dataset) — those apply to what we built, not to these third-party public-domain
  documents — see the archive-root `NOTICE` and `SAFETY_REVIEW.md`.
- **Official figures remain those of the California Department of State Hospitals.** Contact
  `me@sudhanshurai.org` for corrections or removal requests.

## Full file list

- `gov2023-24.pdf` — [source](https://web.archive.org/web/20230331050810/https://www.dsh.ca.gov/About_Us/docs/2023-24_Governors_Budget_Estimate.pdf)
- `gov2024-25.pdf` — [source](https://web.archive.org/web/20240125025600/https://www.dsh.ca.gov/About_Us/docs/2024-25_Governors_Budget_Estimate.pdf)
- `gov2025-26.pdf` — [source](https://web.archive.org/web/20250124222254/https://www.dsh.ca.gov/About_Us/docs/DSH_2025-26_Governor's_Budget_Estimate_Binder.pdf)
- `gov2026-27.pdf` — [source](https://www.dsh.ca.gov/About_Us/) *(general landing/docket page, not a direct per-file link)*
- `may2022-23.pdf` — [source](https://web.archive.org/web/20220702014849/https://www.dsh.ca.gov/About_Us/docs/DSH_2022-23_May_Revision_Estimate.pdf)
- `may2023-24.pdf` — [source](https://web.archive.org/web/20230527071743/https://www.dsh.ca.gov/About_Us/docs/DSH_2023-24_May_Revision_Estimate.pdf)
- `may2024-25.pdf` — [source](https://web.archive.org/web/20240524031635/https://www.dsh.ca.gov/About_Us/docs/DSH%202024-25_May_Revision_Estimate.pdf)
- `may2025-26.pdf` — [source](https://web.archive.org/web/20250520221112/https://www.dsh.ca.gov/About_Us/docs/DSH_2025-26_May_Revision_Estimate.pdf)
- `may2026-27.pdf` — [source](https://www.dsh.ca.gov/About_Us/docs/DSH_2026-27_May_Revision_Estimate.pdf)
