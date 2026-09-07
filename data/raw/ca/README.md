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

Unlike some other states in this archive, California's own stated policy for executive-branch
content is a public-domain default:

> "information presented on this website, unless otherwise indicated, is considered in the public
> domain. It may be distributed or copied as permitted by law."
> — ca.gov Conditions of Use (the baseline policy for California executive-branch sites,
> including dsh.ca.gov and ebudget.ca.gov, where these documents are published)

This is reinforced by a published, precedential California Court of Appeal decision — *County of
Santa Clara v. California First Amendment Coalition*, 170 Cal.App.4th 1301 (2009) — holding there
is no statutory basis for a California public agency to invoke copyright to restrict redistribution
of public records absent specific statutory authority, which does not exist for budget "Estimate"
documents like these. No copyright notice or usage restriction appears anywhere on any of the 9
files themselves.

- We redistribute them **unchanged**, solely so the extraction pipeline in this archive
  (`../../../src/ca_dsh.py`) is independently reproducible from its exact inputs (run
  `python src/verify.py` from the archive root).
- Not covered by this archive's own `LICENSE` (MIT, for our code) or `LICENSE-DATA` (CC-BY-4.0, for
  our derived dataset) — those apply to what we built, not to these third-party public-domain
  documents — see the archive-root `NOTICE` and `SAFETY_REVIEW.md`.
- **Official figures remain those of the California Department of State Hospitals.** Contact
  `me@sudhanshurai.org` for corrections or removal requests.
