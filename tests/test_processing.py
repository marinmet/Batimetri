from pathlib import Path

from batimetri.io import load_soundings
from batimetri.processing import GridSpecification, compute_summary, generate_ascii_grid


def test_compute_summary():
    soundings = load_soundings(Path("data/sample_soundings.csv"))
    summary = compute_summary(soundings)
    assert summary.count == 7
    assert round(summary.min_depth, 2) == 12.4
    assert round(summary.max_depth, 1) == 13.8
    assert round(summary.mean_depth, 3) == round(sum(s.depth for s in soundings) / len(soundings), 3)


def test_generate_ascii_grid_creates_values():
    soundings = load_soundings(Path("data/sample_soundings.csv"))
    grid = generate_ascii_grid(soundings, GridSpecification(cell_size=0.0005))
    assert grid.ncols > 0 and grid.nrows > 0
    assert any(value != grid.spec.nodata_value for row in grid.values for value in row)
    ascii_text = grid.to_ascii()
    assert "ncols" in ascii_text and "NODATA_value" in ascii_text
