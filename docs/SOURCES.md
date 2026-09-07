# Sources

This release covers **five states** — Washington, Oregon, Colorado, Texas, and California — each
operating under a different legal mechanism addressing competency-restoration timeliness. Each
state's series is rebuilt from that state's own public reports. **Per-file provenance** — exact
filename, source URL where a stable one is known, and SHA-256 — is in `SOURCES.csv` at the archive
root (91 WA + 18 OR + 14 CO + 6 TX + 9 CA = 138 documents). The bundled source documents live under
`data/raw/<state>/`; **the terms of their redistribution differ by state** — read `data/raw/NOTICE`
and each state's own `data/raw/<state>/README.md`, not just this file.

Direct PDF links to these reports are unstable and rot over time — several states' own reports
moved hosts partway through their series. Provenance is therefore anchored on a stable landing/
docket page per state plus a SHA-256 for every file (in `SOURCES.csv`), not solely on direct
download URLs.

## Landing pages

| State | Governing matter | Stable source (landing / docket) |
|---|---|---|
| Washington | *Trueblood v. DSHS*, No. 2:14-cv-01178 (W.D. Wash.) — federal settlement/injunction, 7-day admission standard | https://www.dshs.wa.gov/bha/court-monitor-reports |
| Oregon | *Oregon Advocacy Center v. Mink* / *Bowman*, No. 3:02-cv-00339 (D. Or.) — federal injunction, 7-day admission standard | https://www.oregon.gov/oha/osh/pages/mink-bowman.aspx |
| Colorado | *Center for Legal Advocacy v. Barnes*, No. 1:11-cv-02285-NYW (D. Colo.) — federal consent decree, tiered 7-/28-day deadlines, Special Master-monitored | https://www.courtlistener.com/docket/4176801/center-for-legal-advocacy-v-barnes/ (court filings); https://leg.colorado.gov/agencies/joint-budget-committee (budget memos) |
| Texas | No binding admission deadline until a July 2026 federal ruling (now under appeal) | https://www.hhs.texas.gov/about/records-statistics/data-statistics |
| California | *Stiavetti v. Clendenin* — state-court mandate, 28-day placement standard (final, since March 2025) | https://www.dsh.ca.gov/About_Us/ |

## Washington — *Trueblood v. DSHS* (No. 2:14-cv-01178, W.D. Wash.)
Federal settlement/injunction with a 7-day admission standard for restoration and inpatient
evaluation, and a looser 14-day standard for jail-based evaluation only, monitored monthly. This is
the dense, load-bearing series.
- **Publisher:** WA DSHS, Office of Forensic Mental Health Services.
- **Documents:** monthly *Trueblood* court-monitor compliance reports (`data/raw/washington/`).

## Oregon — *Oregon Advocacy Center v. Mink* / *Bowman* (No. 3:02-cv-00339, D. Or.)
Federal injunction requiring admission of aid-and-assist defendants to the Oregon State Hospital
within 7 days; a court-appointed neutral expert / monitor reports periodically, and contempt fines
accrue under the order.
- **Publisher:** Oregon Health Authority / Oregon State Hospital; the court's neutral expert /
  monitor; the Oregon Attorney General (legal pleadings).
- **Documents:** neutral-expert (Pinals) & court-monitor reports, status filings, and AG pleadings
  (`data/raw/oregon/`).

## Colorado — *Center for Legal Advocacy v. Barnes* (No. 1:11-cv-02285-NYW, D. Colo.)
Federal consent decree with two tiers of restoration wait-day deadlines (Tier-1, acute, 7 days;
Tier-2, 28 days, phased down over time), monitored by a court-appointed Special Master. A separate
restoration-waitlist series comes from the state legislature's Joint Budget Committee (JBC) staff
budget briefings.
- **Publisher:** the Special Master (federal court filings, via RECAP); Colorado Joint Budget
  Committee staff (state legislature).
- **Documents:** quarterly Special Master reports (`sm_*.pdf`) and JBC budget memos
  (`data/raw/colorado/`).

## Texas — no binding deadline until mid-2026
Texas Health and Human Services Commission (HHSC) publishes semiannual statewide mental-health
waiting-list reports (both a "non-maximum-security" and a "maximum-security" queue) under a
legislative reporting mandate, but had no binding admission deadline of its own until a July 2026
federal ruling ordered one — now under appeal.
- **Publisher:** Texas HHSC.
- **Documents:** semiannual mental-health waiting-list reports (`data/raw/texas/`).

## California — *Stiavetti v. Clendenin* (state court)
A California *state*-court mandate — not a federal decree, unlike the other four states — setting a
final 28-day IST (Incompetent to Stand Trial) placement standard since March 2025. The Department
of State Hospitals (DSH) reports its pending-placement waitlist irregularly: an annual
fiscal-year-end table plus occasional budget-narrative prose mentions, not a dedicated monthly
monitor report.
- **Publisher:** California Department of State Hospitals (DSH), via Governor's Budget / May
  Revision "Estimate" documents.
- **Documents:** semiannual budget "Estimate" PDFs (`data/raw/california/`).

---

All five states measure and publish somewhat different things (a wait *time* vs. a waitlist
*stock*; admission time vs. completion time; monthly vs. periodic vs. irregular cadence). Every
measure in the harmonized datasets carries an explicit basis flag so non-comparable measures are
never silently mixed, and no cross-state view in this project computes a 5-state average — see
`docs/PIPELINE.md`. For the exact file-by-file list, source URLs, and checksums, see `SOURCES.csv`.
