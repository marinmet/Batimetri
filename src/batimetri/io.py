from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

from .models import Sounding


class InvalidSoundingRow(ValueError):
    """Raised when a row in the input file cannot be parsed."""


REQUIRED_FIELDS = {"latitude", "longitude", "depth"}
OPTIONAL_FIELDS = {"timestamp"}


def _parse_timestamp(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - safeguards for user input
        raise InvalidSoundingRow(f"Invalid timestamp: {value}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_soundings(path: Path | str) -> List[Sounding]:
    """Load soundings from a CSV file.

    The CSV must contain ``latitude``, ``longitude`` and ``depth`` columns.
    A ``timestamp`` column is optional and parsed as ISO-8601. Missing or
    malformed rows raise :class:`InvalidSoundingRow`.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    soundings: List[Sounding] = []
    with path.open(newline="", encoding="utf-8") as handle:
        sample = handle.read(2048)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        reader = csv.DictReader(handle, dialect=dialect)

        headers = {field.lower() for field in reader.fieldnames or []}
        missing = REQUIRED_FIELDS - headers
        if missing:
            raise InvalidSoundingRow(f"Missing required columns: {', '.join(sorted(missing))}")

        for idx, row in enumerate(reader, start=2):
            try:
                lat = float(row.get("latitude", ""))
                lon = float(row.get("longitude", ""))
                depth = float(row.get("depth", ""))
            except ValueError as exc:  # pragma: no cover - defensive
                raise InvalidSoundingRow(f"Invalid numeric value on line {idx}") from exc

            timestamp = row.get("timestamp") or None
            dt = _parse_timestamp(timestamp) if timestamp else None
            soundings.append(Sounding(latitude=lat, longitude=lon, depth=depth, timestamp=dt))

    return soundings


def write_soundings(path: Path | str, soundings: Sequence[Sounding]) -> None:
    """Write soundings to CSV in a canonical format."""

    path = Path(path)
    fieldnames = ["latitude", "longitude", "depth", "timestamp"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for s in soundings:
            writer.writerow(
                {
                    "latitude": f"{s.latitude:.8f}",
                    "longitude": f"{s.longitude:.8f}",
                    "depth": f"{s.depth:.3f}",
                    "timestamp": s.timestamp.isoformat() if s.timestamp else "",
                }
            )
