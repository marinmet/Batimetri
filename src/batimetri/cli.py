from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .io import load_soundings
from .processing import BathymetrySummary, GridSpecification, compute_summary, export_filtered_csv, export_grid, generate_ascii_grid


def _print_summary(summary: BathymetrySummary) -> None:
    print("Sounding Count :", summary.count)
    print("Minimum Depth  :", f"{summary.min_depth:.2f} m")
    print("Maximum Depth  :", f"{summary.max_depth:.2f} m")
    print("Mean Depth     :", f"{summary.mean_depth:.2f} m")


def cmd_summary(args: argparse.Namespace) -> None:
    soundings = load_soundings(args.input)
    summary = compute_summary(soundings)
    _print_summary(summary)


def cmd_export_grid(args: argparse.Namespace) -> None:
    soundings = load_soundings(args.input)
    if args.min_depth is not None or args.max_depth is not None:
        from .processing import filter_soundings

        soundings = filter_soundings(soundings, min_depth=args.min_depth, max_depth=args.max_depth)
    grid = generate_ascii_grid(soundings, GridSpecification(cell_size=args.cell_size, nodata_value=args.nodata))
    export_grid(args.output, grid)
    print(f"Grid exported to {args.output}")


def cmd_filter(args: argparse.Namespace) -> None:
    soundings = load_soundings(args.input)
    export_filtered_csv(args.output, soundings, min_depth=args.min_depth, max_depth=args.max_depth)
    print(f"Filtered soundings written to {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Singlebeam bathymetry processing toolkit")
    subparsers = parser.add_subparsers(dest="command")

    summary = subparsers.add_parser("summary", help="Summarize input soundings")
    summary.add_argument("input", type=Path, help="CSV file containing soundings")
    summary.set_defaults(func=cmd_summary)

    grid = subparsers.add_parser("export-grid", help="Create a simple ASCII grid")
    grid.add_argument("input", type=Path, help="CSV file containing soundings")
    grid.add_argument("output", type=Path, help="Path to the ASCII grid output")
    grid.add_argument("--cell-size", type=float, default=0.0005, help="Grid cell size in degrees (default: 0.0005)")
    grid.add_argument("--nodata", type=float, default=-9999.0, help="NODATA value used in the grid")
    grid.add_argument("--min-depth", type=float, help="Minimum depth filter (inclusive)")
    grid.add_argument("--max-depth", type=float, help="Maximum depth filter (inclusive)")
    grid.set_defaults(func=cmd_export_grid)

    filter_cmd = subparsers.add_parser("filter", help="Filter soundings and write to CSV")
    filter_cmd.add_argument("input", type=Path, help="CSV file containing soundings")
    filter_cmd.add_argument("output", type=Path, help="Filtered CSV output file")
    filter_cmd.add_argument("--min-depth", type=float, help="Minimum depth filter (inclusive)")
    filter_cmd.add_argument("--max-depth", type=float, help="Maximum depth filter (inclusive)")
    filter_cmd.set_defaults(func=cmd_filter)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
