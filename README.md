# Competency Restoration Dashboard Data — A Reproducible Five-State Panel

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22652057.svg)](https://doi.org/10.5281/zenodo.22652057)

**Cite this dataset** (concept DOI, always the latest version):
[10.5281/zenodo.22652057](https://doi.org/10.5281/zenodo.22652057). Each release also carries its
own immutable version DOI, so an exact version can be pinned — current (v1.0.0):
[10.5281/zenodo.22652058](https://doi.org/10.5281/zenodo.22652058). Use the version DOI when citing
for reproducibility. Full citation in `CITATION.cff`; per-version changes in `CHANGELOG.md`.

> **This repository is a DATA AND METHODS resource.** It provides a harmonized, source-linked
> dataset of competency-restoration timeliness and waitlist measures for **five U.S. states** —
> **Washington, Oregon, Colorado, Texas, and California** — each operating under a different legal
> mechanism, together with the code that builds and verifies it from public documents.
> **It is not a research paper and does not report study findings.**

> *This is a sibling resource to [10.5281/zenodo.21436450](https://doi.org/10.5281/zenodo.21436450),
> this project's earlier two-state (Washington/Oregon) academic-paper data deposit. That deposit is
> a frozen snapshot tied to a specific manuscript's analysis window; this one is the full five-state
> dataset behind the live public dashboard at [competencyrestoration.org](https://competencyrestoration.org),
> updated periodically (as a new version) as new source reports are published — independently of
> the paper deposit's own version history.*

## What this is

When a defendant is found incompetent to stand trial, the state must provide timely restoration
treatment; in practice, defendants often wait in jail or in the community for scarce hospital
capacity. Five states enforce (or, in Texas's case, have just begun enforcing) a timeliness
standard through five different legal mechanisms — a federal consent decree with an independent
court monitor (Washington), a federal injunction (Oregon), a federal consent decree with a
court-appointed Special Master (Colorado), a brand-new court ruling under appeal (Texas), and a
state-court mandate (California). The compliance data exist — but are scattered across
court-monitor filings, special-master reports, neutral-expert reports, state-hospital documents,
and legislative budget memos, in inconsistent formats, and have not been assembled into one open,
reproducible, cross-state resource. **This dataset assembles them.**

## What is included

- **`data/derived/` — the harmonized per-state datasets** (`washington.csv`, `oregon.csv`,
  `colorado_jbc.csv`, `colorado_special_master.csv`, `texas.csv`, `california.csv`), each in a
  long schema with explicit, documented measure definitions and a per-row source citation
  (report filename, page, table reference).
- **`src/` — the extraction pipeline**: six per-state extractors
  (`wa_trueblood.py`, `or_osh.py`, `tx_hhsc.py`, `co_jbc.py`, `co_special_master.py`, `ca_dsh.py`)
  plus shared utilities (`_util.py`, `config.py`).
- **`src/verify.py` — a re-execution gate** that rebuilds each dataset from the raw source
  documents and asserts anchor values against the source PDFs, plus cross-run consistency checks
  (e.g. a dedicated completeness check on the newest report in each series, since a fresh report
  has no later report to silently fall back on if its own extraction ever failed).
- **`data/raw/` — the source documents** (138 files bundled: 91 WA + 18 OR + 14 CO + 6 TX + 9 CA),
  redistributed unchanged so the pipeline is reproducible from its exact inputs. **The right to
  redistribute the bundled files differs meaningfully by state — read `data/raw/NOTICE` and each
  state's own `data/raw/<state>/README.md` before assuming a uniform basis.** Per-file provenance
  (source URL, SHA-256, for all 138) is in `SOURCES.csv`; `SAFETY_REVIEW.md` records the
  pre-publication PII/sealing review.

## Coverage (heterogeneous by design)

Each state publishes on its own cadence and in its own format; the harmonization across those
differences is part of the contribution. Washington provides the densest series (monthly, since
2018). Oregon and Colorado are sparser, periodic series. Texas is a semiannual series with no
binding standard until mid-2026. California is the sparsest — annual fiscal-year snapshots plus
irregular budget-prose mentions, explicitly not comparable in freshness to the others. Each measure
carries an explicit basis flag (e.g. wait-time vs. waitlist stock) so non-comparable measures are
never silently mixed, and no cross-state view in this project ever computes a 5-state average — see
`docs/PIPELINE.md`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/verify.py
```

One source document (`data/raw/co/sm_2024-11-28.pdf`) embeds a broken/cid-encoded font on 2 pages
that `pdfplumber`'s normal text layer can't read; `src/co_special_master.py` recovers it via OCR
(`pytesseract`, in `requirements.txt`), which also needs the `tesseract` system binary installed
separately (`brew install tesseract` on macOS, `apt install tesseract-ocr` on Debian/Ubuntu) — not
installable via pip alone. No other source document or extractor needs this.

## Reproducibility

Every value traces to a specific source document, page, and (where applicable) table. To
regenerate and verify a state's dataset from source, run its extractor then the gate:

```
python src/wa_trueblood.py   # (or or_osh.py / tx_hhsc.py / co_jbc.py / co_special_master.py / ca_dsh.py)
python src/verify.py
```

This re-executes the extractors and asserts the output matches both the committed data and a set
of source-value anchors — independently checkable and extensible to additional states, time
periods, or new reports as they're published.

## Intended uses

A reproducible, cross-state compliance series that advocates, court monitors, oversight bodies,
journalists, and researchers can verify, track, and extend. Contributions of additional states or
corrected/expanded source documents are welcome via the repository.

## Data dictionary

See `docs/PIPELINE.md` for field definitions, units, measure bases, and per-state coverage. Every
row across all six files carries the state, period (YYYY-MM), the relevant value(s), and full
source-document provenance (report filename, page, table reference where applicable).

## Sources & Provenance

| State | Governing mechanism | Files | Rights basis (see `data/raw/<state>/README.md`) |
|---|---|---|---|
| Washington | Federal consent decree, *Trueblood v. DSHS*, W.D. Wash. — 7-day admission standard | 91 | Fair use — no copyright notice found on these DSHS reports, but Washington has no public-domain-by-default policy either |
| Oregon | Federal injunction, *Mink/Bowman*, D. Or. — 7-day admission standard | 18 | Split: 15 privately-authored (Dr. Pinals) reports rest on fair use alone; 3 state-authored (Oregon DOJ) pleadings rest on public agency record + fair use |
| Colorado | Federal consent decree, *Center for Legal Advocacy v. Barnes*, D. Colo. — tiered deadlines, Special Master-monitored | 14 | Fair use (Special Master reports); explicit written permission from JBC staff (JBC budget memos) — see the state README |
| Texas | No binding deadline until a July 2026 federal ruling (phase-in underway, on appeal) | 6 | Conditional license (Texas HHSC's own published terms) |
| California | State-court mandate, *Stiavetti v. Clendenin* — 28-day placement standard | 9 | Public domain |

Direct PDF URLs rot over time — several states' own reports moved hosts partway through their
series. Provenance is therefore anchored on **a confirmed URL where one exists, a best-known
landing page otherwise, plus a SHA-256 for every bundled file** — recorded per document in
`SOURCES.csv`. See `docs/SOURCES.md` for per-state detail.

## License and citation

- **Code** (`src/`) is licensed **MIT** (see `LICENSE`); the **derived dataset** (`data/derived/`)
  is licensed **CC-BY-4.0** (see `LICENSE-DATA`).
- **Source documents** (`data/raw/`) are third-party public records, NOT covered by the above
  licenses, with a rights basis that differs by state — see `data/raw/NOTICE`.
- **Cite this resource** using `CITATION.cff`.

## Disclaimer

This is neutral measurement of publicly reported government and court-monitor compliance data,
intended for transparency and research. It is not legal advice and is not affiliated with, or
endorsed by, any party, court monitor, agency, or state.
