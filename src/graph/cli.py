"""Command-line interface for `graph show <archivo>`."""

import argparse
from collections.abc import Sequence
import sys

from graph.formatter import format_graph
from graph.loader import GraphLoadError, load_graph_from_csv


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for the `graph` command."""
    parser = argparse.ArgumentParser(prog="graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("show", help="Load and display a directed graph from CSV")
    show_parser.add_argument("file", help="Path to the CSV file with header source,target")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the `graph` CLI and return exit code 0 on success or 1 on error."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 1

    try:
        graph = load_graph_from_csv(args.file)
    except GraphLoadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(format_graph(graph))
    return 0


def cli_entrypoint() -> None:
    """Console script entrypoint that exits with the return code from main()."""
    raise SystemExit(main())


if __name__ == "__main__":
    cli_entrypoint()
