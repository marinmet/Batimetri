from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import floor
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .models import Sounding
from .io import write_soundings


@dataclass
class GridSpecification:
    cell_size: float
    nodata_value: float = -9999.0


@dataclass
class BathymetrySummary:
    count: int
    min_depth: float
    max_depth: float
    mean_depth: float


@dataclass
class BathymetryGrid:
    spec: GridSpecification
    ncols: int
    nrows: int
    xllcorner: float
    yllcorner: float
    values: List[List[float]]

    def to_ascii(self) -> str:
        lines = [
            f"ncols {self.ncols}",
            f"nrows {self.nrows}",
            f"xllcorner {self.xllcorner:.6f}",
            f"yllcorner {self.yllcorner:.6f}",
            f"cellsize {self.spec.cell_size}",
            f"NODATA_value {self.spec.nodata_value}",
        ]
        for row in self.values:
            line = " ".join(f"{v:.3f}" if v != self.spec.nodata_value else str(self.spec.nodata_value) for v in row)
            lines.append(line)
        return "\n".join(lines)


def compute_summary(soundings: Iterable[Sounding]) -> BathymetrySummary:
    depths = [s.depth for s in soundings]
    if not depths:
        raise ValueError("No soundings available")
    min_depth = min(depths)
    max_depth = max(depths)
    mean_depth = sum(depths) / len(depths)
    return BathymetrySummary(count=len(depths), min_depth=min_depth, max_depth=max_depth, mean_depth=mean_depth)


def filter_soundings(
    soundings: Iterable[Sounding],
    min_depth: float | None = None,
    max_depth: float | None = None,
) -> List[Sounding]:
    filtered = []
    for s in soundings:
        if min_depth is not None and s.depth < min_depth:
            continue
        if max_depth is not None and s.depth > max_depth:
            continue
        filtered.append(s)
    return filtered


def _grid_bounds(soundings: Iterable[Sounding], cell_size: float) -> Tuple[int, int, float, float]:
    lats = [s.latitude for s in soundings]
    lons = [s.longitude for s in soundings]
    if not lats or not lons:
        raise ValueError("No soundings to grid")
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    ncols = int((max_lon - min_lon) / cell_size) + 1
    nrows = int((max_lat - min_lat) / cell_size) + 1

    return ncols, nrows, min_lon, min_lat


def _bin_soundings(soundings: Iterable[Sounding], cell_size: float, x0: float, y0: float):
    bins: Dict[Tuple[int, int], List[float]] = defaultdict(list)
    for s in soundings:
        col = floor((s.longitude - x0) / cell_size)
        row = floor((s.latitude - y0) / cell_size)
        bins[(row, col)].append(s.depth)
    return bins


def generate_ascii_grid(
    soundings: Iterable[Sounding],
    spec: GridSpecification,
) -> BathymetryGrid:
    soundings = list(soundings)
    ncols, nrows, x0, y0 = _grid_bounds(soundings, spec.cell_size)
    bins = _bin_soundings(soundings, spec.cell_size, x0, y0)

    nodata = spec.nodata_value
    grid: List[List[float]] = [[nodata for _ in range(ncols)] for _ in range(nrows)]

    for (row, col), depths in bins.items():
        if row < 0 or col < 0 or row >= nrows or col >= ncols:
            continue
        grid[row][col] = sum(depths) / len(depths)

    return BathymetryGrid(spec=spec, ncols=ncols, nrows=nrows, xllcorner=x0, yllcorner=y0, values=grid)


def export_grid(path: Path | str, grid: BathymetryGrid) -> None:
    path = Path(path)
    path.write_text(grid.to_ascii(), encoding="utf-8")


def export_filtered_csv(
    path: Path | str, soundings: Iterable[Sounding], min_depth: float | None = None, max_depth: float | None = None
) -> None:
    filtered = filter_soundings(soundings, min_depth=min_depth, max_depth=max_depth)
    write_soundings(path, filtered)
