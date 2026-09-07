"""Competency Restoration Dashboard Data — config.

ADAPTED (2026-09-07) from the private working tree's `dashboard/code/config.py` for this
standalone public archive's own layout: `data/raw/` and `data/derived/` here, in place of the
working tree's `dashboard_data/raw/` and `dashboard_data/derived/` (a private tree containing
material -- outreach notes, in-progress drafts -- that isn't part of this public release). No
other change: `_find_root()`'s marker-search logic and every extractor's own parsing code are
otherwise byte-identical to the working tree's copies.

Coverage: all 5 states (Washington, Oregon, Colorado, Texas, California), each with its own
extractor under `src/`.
"""
from pathlib import Path


def _find_root(start: Path) -> Path:
    for cand in [start.resolve()] + list(start.resolve().parents):
        if (cand / "data" / "raw").is_dir() or (cand / ".git").exists():
            return cand
    raise RuntimeError(
        f"src/config.py: could not find the archive root above {start.resolve()} — no 'data/raw/' "
        f"directory and no '.git' anywhere in the parent chain. Refusing to guess a directory depth."
    )


ROOT = _find_root(Path(__file__).parent)
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
for d in (RAW, DERIVED):
    d.mkdir(parents=True, exist_ok=True)

# Duplicated from code/pipeline/config.py (2026-08-28) for wa_trueblood.py's download_report() --
# see this module's own docstring for why WA/OR are duplicated rather than imported.
WA_HOSTS = [
    "https://www.dshs.wa.gov/sites/default/files/BHSIA/FMHS/Trueblood",
    "https://manuals.dshs.wa.gov/sites/default/files/BHSIA/FMHS/Trueblood",
]
def wa_report_urls(year: int, month: int):
    ym = f"{year:04d}-{month:02d}"
    return [f"{h}/{year}Trueblood/Trueblood-Report-{ym}.pdf" for h in WA_HOSTS]
