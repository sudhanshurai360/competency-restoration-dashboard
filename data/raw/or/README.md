# Oregon — source documents

**18 files.** Court-monitor and neutral-expert reports, and Attorney General legal pleadings
(`PLD-*.pdf`), from *Oregon Advocacy Center v. Mink / Bowman*, No. 3:02-cv-00339 (D. Or.) — a
federal injunction requiring aid-and-assist admission within 7 days. Published by the Oregon
Health Authority / Oregon State Hospital (most files) and via CourtListener/RECAP (one file, an
exhibit copy of the same underlying report — see below).

## Where these came from

Every file's exact source URL, byte size, and SHA-256 hash is recorded in `SOURCES.csv` at the
archive root (filter `state == or`) — **all 15 court-monitor and neutral-expert reports are now
individually hash-verified**, not just pattern-guessed. This wasn't true in an earlier version of
this archive: 7 of the 15 were initially marked `inferred` against a single assumed URL pattern
(`oregon.gov/oha/OSH/reports/{filename}`) that turned out to be wrong for several of them — the
1st through 5th Neutral Expert reports actually live under a *different* path
(`oregon.gov/oha/OSH/Documents/{filename}`, note capital "D"), and the 2nd and 8th reports use
different filenames on OHA's own site than the ones used locally in this archive (e.g. the 8th
uses hyphens where this archive's filename uses underscores). A direct link-check (2026-09-07)
caught the resulting 404s; every one of those 7, plus the March 2026 Court Monitor report, was
re-verified byte-for-byte against OHA's actual current hosting before being marked `confirmed`.
One file (`2025.09.05-Oregon-Mink-Bowman-Court-Monitor-Report.pdf`) is separately verified as
content-identical to a copy later filed as a court exhibit and retrieved via CourtListener/RECAP
(storage.courtlistener.com/recap/gov.uscourts.ord.6119/...), same report, same substance, an added
court-filing header/footer stamp only. The 3 `PLD-*.pdf` files have no confirmed per-file URL at
all (marked `hub-only`) — the general case landing page is linked instead.

## Rights — two different document types, with different footing (read both parts)

**15 court-monitor / neutral-expert reports** (everything except the 3 `PLD-*.pdf` files): these
are authored by Dr. Debra Pinals, the court's privately-retained neutral expert/monitor — **not**
Oregon Health Authority (OHA) work product; OHA merely hosts copies on its own site. Redistribution
here rests on **fair use only** (litigation-related material, non-commercial public-interest
reproduction, no market this could substitute for, already freely public on OHA's own site) — the
same basis established services like CourtListener, RECAP, and Justia rely on to redistribute
filings at scale. This is the weaker-footing of Oregon's two document types, precisely because
there's no state-agency-authorship backdrop behind it.

**3 Attorney General legal pleadings** (`PLD-*.pdf`): filed by the Oregon Department of Justice
(Attorney General's office) as counsel for the state defendants — genuinely state-employee-authored
work product, unlike the 15 reports above. These rest on the stronger combination of a public
agency record **plus** the same fair-use basis for litigation filings — the strongest-footing
documents in this folder, not the weakest, despite being lumped together with the reports above in
earlier, less precise framing of this archive.

Neither category is our own work — we did not author any of these 18 documents, and redistributing
them here does not transfer or claim any ownership or copyright in them.

- We redistribute them **unchanged**, solely so the extraction pipeline in this archive is
  independently reproducible from its exact inputs (run `python src/verify.py` from the archive
  root).
- **License**: this archive's own `LICENSE` (code, MIT) and `LICENSE-DATA` (our derived dataset,
  CC-BY-4.0) do **not** cover these source PDFs — see the archive-root `NOTICE` and
  `SAFETY_REVIEW.md` for the full rights and pre-publication safety review covering this folder.
- **Official figures remain those of the court monitor, neutral expert, and Oregon Health
  Authority.** If anything here conflicts with the original, the original governs — contact
  `me@sudhanshurai.org` for corrections or removal requests from a rights holder.

## Full file list

- `2025.09.05-Oregon-Mink-Bowman-Court-Monitor-Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/2025.09.05-Oregon-Mink-Bowman-Court-Monitor-Report.pdf)
- `2025.12.06-Oregon-Mink-Bowman-Court-Monitor-Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/2025.12.06-Oregon-Mink-Bowman-Court-Monitor-Report.pdf)
- `2026.03.16-Oregon-Mink-Bowman-Court-Monitor-Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_3rd_Court_Monitor_Pinals_Report_2026.03.16.pdf)
- `Oregon_Mink-Bowman_10th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_10th_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_11th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_11th_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_11th_Neutral_Expert_Pinals_Report_supplement.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_11th_Neutral_Expert_Pinals_Report_supplement.pdf)
- `Oregon_Mink-Bowman_1st_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/Documents/Oregon-Mink-Bowman-Neutral-Expert-Pinals-Report.pdf)
- `Oregon_Mink-Bowman_2nd_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/Documents/Oregon-Mink-Bowman-2022-0535-2nd-Neutral-Expert-Pinals-Report.pdf)
- `Oregon_Mink-Bowman_3rd_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/Documents/Oregon_Mink-Bowman_3rd_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_4th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/Documents/Oregon_Mink-Bowman_4th_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_5th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/Documents/Oregon_Mink-Bowman_5th_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_6th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_6th_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_7th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_7th_Neutral_Expert_Pinals_Report.pdf)
- `Oregon_Mink-Bowman_8th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon-Mink-Bowman-8th-Neutral-Expert-Pinals-Report.pdf)
- `Oregon_Mink-Bowman_9th_Neutral_Expert_Pinals_Report.pdf` — [source](https://www.oregon.gov/oha/OSH/reports/Oregon_Mink-Bowman_9th_Neutral_Expert_Pinals_Report.pdf)
- `PLD-2022.10.03.pdf` — [source](https://www.oregon.gov/oha/osh/pages/mink-bowman.aspx) *(general landing/docket page, not a direct per-file link)*
- `PLD-2022.11.03.pdf` — [source](https://www.oregon.gov/oha/osh/pages/mink-bowman.aspx) *(general landing/docket page, not a direct per-file link)*
- `PLD-2024.03.03.pdf` — [source](https://www.oregon.gov/oha/osh/pages/mink-bowman.aspx) *(general landing/docket page, not a direct per-file link)*
