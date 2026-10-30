"""Strict CSV loader and validator for DirectedGraph."""

import csv
from pathlib import Path

from graph.model import DirectedGraph


class GraphLoadError(Exception):
    """Error raised when a CSV file cannot be loaded or violates format rules."""

    def __init__(
        self,
        message: str,
        *,
        line_number: int | None = None,
        row_content: str | None = None,
    ) -> None:
        self.line_number = line_number
        self.row_content = row_content
        if line_number is not None and row_content is not None:
            full_message = f"Line {line_number}: {message} (row: {row_content!r})"
        elif line_number is not None:
            full_message = f"Line {line_number}: {message}"
        else:
            full_message = message
        super().__init__(full_message)


def load_graph_from_csv(path: str | Path) -> DirectedGraph:
    """Load and validate a DirectedGraph from a CSV file with header `source,target`."""
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise GraphLoadError(f"File not found: '{file_path}'")

    raw_text = file_path.read_text(encoding="utf-8")
    if raw_text == "":
        raise GraphLoadError(f"File is empty: '{file_path}'")

    # Split lines preserving trailing empty lines if there are extra blank lines at EOF
    lines = raw_text.splitlines()
    if raw_text.endswith(("\n\n", "\r\n\r\n", "\n\r\n")):
        lines.append("")

    header_raw = lines[0]
    if header_raw.strip() != "source,target":
        raise GraphLoadError(
            "Invalid or missing header; expected 'source,target'",
            line_number=1,
            row_content=header_raw,
        )

    graph = DirectedGraph()

    for line_number, raw_line in enumerate(lines[1:], start=2):
        if raw_line == "":
            raise GraphLoadError(
                "Blank line is not allowed",
                line_number=line_number,
                row_content=raw_line,
            )

        row = next(csv.reader([raw_line]))
        if len(row) != 2:
            raise GraphLoadError(
                f"Expected exactly 2 columns, got {len(row)}",
                line_number=line_number,
                row_content=raw_line,
            )

        source = row[0].strip()
        target = row[1].strip()

        if source == "":
            raise GraphLoadError(
                "Source vertex cannot be empty",
                line_number=line_number,
                row_content=raw_line,
            )

        if target == "":
            graph.add_vertex(source)
        else:
            graph.add_edge(source, target)

    return graph
