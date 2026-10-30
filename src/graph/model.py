"""In-memory directed graph representation using an adjacency list."""


class DirectedGraph:
    """Directed, unweighted graph backed by a vertex registry and adjacency sets."""

    def __init__(self) -> None:
        self.vertices: set[str] = set()
        self.adjacency: dict[str, set[str]] = {}

    def add_vertex(self, name: str) -> None:
        """Register a vertex in the graph, preserving isolated vertices."""
        self.vertices.add(name)
        self.adjacency.setdefault(name, set())

    def add_edge(self, source: str, target: str) -> None:
        """Register a directed edge source -> target, deduplicating naturally via set."""
        self.add_vertex(source)
        self.add_vertex(target)
        self.adjacency[source].add(target)

    def vertex_count(self) -> int:
        """Return total number of unique vertices in the graph."""
        return len(self.vertices)

    def edge_count(self) -> int:
        """Return total number of unique directed edges in the graph."""
        return sum(len(targets) for targets in self.adjacency.values())
