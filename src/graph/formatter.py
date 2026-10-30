"""Output formatter for DirectedGraph applying alphabetical order at display time."""

from graph.model import DirectedGraph


def format_graph(graph: DirectedGraph) -> str:
    """Format the summary, sorted vertices, and sorted directed edges."""
    sorted_vertices = sorted(graph.vertices)
    edge_lines: list[str] = []
    for source in sorted_vertices:
        for target in sorted(graph.adjacency[source]):
            edge_lines.append(f"{source} -> {target}")

    lines = [
        f"Vertices: {graph.vertex_count()}, Edges: {graph.edge_count()}",
        "Vertices:",
        *sorted_vertices,
        "Edges:",
        *edge_lines,
    ]
    return "\n".join(lines)
