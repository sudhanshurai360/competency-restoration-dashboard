# Oregon — source documents

**18 files.** Court-monitor and neutral-expert reports, and Attorney General legal pleadings
(`PLD-*.pdf`), from *Oregon Advocacy Center v. Mink / Bowman*, No. 3:02-cv-00339 (D. Or.) — a
federal injunction requiring aid-and-assist admission within 7 days. Published by the Oregon
Health Authority / Oregon State Hospital (most files) and via CourtListener/RECAP (one file, an
exhibit copy of the same underlying report — see below).

## Where these came from

Every file's exact source URL (or best-known landing page, where no stable per-file URL was
confirmed), byte size, and SHA-256 hash is recorded in `SOURCES.csv` at the archive root (filter
`state == or`). 14 of the 18 files (all the court-monitor and neutral-expert reports except one)
follow the Oregon Health Authority's own reports-page pattern —

```
https://www.oregon.gov/oha/OSH/reports/{filename}
```

— marked `inferred` in `SOURCES.csv`: this is the real, live OHA URL pattern, but each individual
file wasn't separately hash-verified against that exact URL. One file
(`2025.09.05-Oregon-Mink-Bowman-Court-Monitor-Report.pdf`) IS individually verified — confirmed
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
