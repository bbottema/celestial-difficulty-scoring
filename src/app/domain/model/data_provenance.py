"""
Data provenance tracking for catalog sources.

Tracks where data came from, when it was fetched, and quality indicators.
Enables cache TTL decisions and data quality assessment.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DataProvenance:
    """
    Track source and quality of catalog data.

    Used for:
    - Cache TTL decisions (OpenNGC cached longer than SIMBAD)
    - Data quality assessment
    - Debugging data issues
    - Attribution in UI
    """
    source: str  # "openngc", "simbad", "horizons", "wds", "skyfield"
    fetched_at: datetime
    catalog_version: Optional[str] = None  # e.g., "OpenNGC_2023-12-13"
    confidence: float = 1.0  # 0.0-1.0 for computed/estimated values

    def is_authoritative(self) -> bool:
        """Check if this is direct catalog data vs computed"""
        return self.confidence >= 0.9

    def is_stale(self, max_age_hours: int) -> bool:
        """Check if data is older than specified hours"""
        age = datetime.now() - self.fetched_at
        return age.total_seconds() > (max_age_hours * 3600)
