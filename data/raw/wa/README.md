# Washington — source documents

**91 files.** Monthly compliance reports filed by the court monitor in *Trueblood v. DSHS*, No.
2:14-cv-01178 (W.D. Wash.) — a federal consent decree requiring admission for competency
restoration within 7 days. Published by the Washington State Department of Social and Health
Services (DSHS).

## Where these came from

Every file's exact source URL, byte size, and SHA-256 hash is recorded in `SOURCES.csv` at the
archive root (filter `state == wa`). In short: DSHS hosts these at a stable, predictable path —

```
https://www.dshs.wa.gov/sites/default/files/BHSIA/FMHS/Trueblood/{year}Trueblood/Trueblood-Report-{year}-{month}.pdf
```

— and every file in this folder was downloaded from exactly that pattern and hash-verified
against the copy actually used by the extraction pipeline (`../../../src/wa_trueblood.py`).

## Rights — we do not own these documents

These are public records produced by a federal court monitor under a Washington state agency's
(DSHS's) publication, not our own work. We did not author them, and redistributing them here does
not transfer or claim any ownership or copyright in them.

**Said precisely**: Washington has no public-domain-by-default statute for state agency
publications (unlike California — see `data/raw/ca/README.md` — Washington agencies can and do
assert copyright; the state's Public Records Act, RCW 42.56, is a disclosure/inspection right, not
a copyright license, and that distinction matters here). DSHS's own site is silent on copyright for
these specific reports — no notice appears on the documents themselves, and DSHS has never
restricted their reuse — so redistribution here rests on the same basis as Oregon's and Colorado's
court-filed documents: **fair use** (non-commercial, public-interest reproduction of factual
compliance data DSHS already publishes openly, no market this could substitute for), not a
public-domain claim. Practical risk is low — DSHS openly publishes these exact reports itself — but
that is a different thing from a cleared legal right, and this document doesn't overstate the
difference.

- We redistribute them **unchanged**, solely so the extraction pipeline in this archive is
  independently reproducible from its exact inputs (run `python src/verify.py` from the archive
  root).
- **License**: this archive's own `LICENSE` (code, MIT) and `LICENSE-DATA` (our derived dataset,
  CC-BY-4.0) do **not** cover these source PDFs — see the archive-root `NOTICE` and
  `SAFETY_REVIEW.md` for the full rights and pre-publication safety review covering this folder.
- **Official figures remain those of the court monitor and DSHS.** If anything here conflicts with
  the original, the original governs — contact `me@sudhanshurai.org` for corrections or removal
  requests from a rights holder.
