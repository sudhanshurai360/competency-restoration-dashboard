"""Competency Restoration Dashboard Data — shared primitives for the extractors.

Only GENUINELY-identical helpers belong here. The per-state `MON` month-maps and
`_num`/`_period` parsers LOOK duplicated but are NOT interchangeable — each state's
source documents use a different date format and number convention:
  WA  = 'JAN-24'  (3-letter, 2-digit year, uppercase)
  OR  = 'january 2024'  (full name, lowercase, 4-digit year)
Consolidating those would couple independent adapters and break parsing. Do NOT
"de-duplicate" the per-state date/number helpers — the specialization is intentional.
"""
import hashlib
from pathlib import Path


def sha12(path) -> str:
    """First 12 hex chars of a file's SHA-256 — the provenance fingerprint stamped on
    every extracted row. The one primitive shared by all extractors."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]
