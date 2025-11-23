from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Sounding:
    """Singlebeam sounding record.

    Attributes:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        depth: Depth measurement (positive downward, meters).
        timestamp: Optional measurement time as timezone-aware datetime.
    """

    latitude: float
    longitude: float
    depth: float
    timestamp: Optional[datetime] = None
