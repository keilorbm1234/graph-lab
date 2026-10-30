"""Unit tests for DirectedGraph model (T003) and output formatter (T006)."""

import unittest

from graph.formatter import format_graph
from graph.model import DirectedGraph


class TestDirectedGraphModel(unittest.TestCase):
    """T003: Unit tests for DirectedGraph adjacency list invariants (FR-007, FR-008, FR-009)."""

    def test_empty_graph_invariants(self) -> None:
        graph = DirectedGraph()
        self.assertEqual(graph.vertices, set())
        self.assertEqual(graph.adjacency, {})
        self.assertEqual(graph.vertex_count(), 0)
        self.assertEqual(graph.edge_count(), 0)

    def test_isolated_vertex_preserved_in_vertices_and_adjacency(self) -> None:
        """FR-007: Isolated vertex (e.g., watch) is stored in vertices and adjacency with empty set."""
        graph = DirectedGraph()
        graph.add_vertex("watch")
        self.assertIn("watch", graph.vertices)
        self.assertIn("watch", graph.adjacency)
        self.assertEqual(graph.adjacency["watch"], set())
        self.assertEqual(set(graph.adjacency.keys()), graph.vertices)
        self.assertEqual(graph.vertex_count(), 1)
        self.assertEqual(graph.edge_count(), 0)

    def test_add_edge_registers_both_vertices_and_deduplicates_naturally(self) -> None:
        """FR-008: Duplicate edges are eliminated naturally by set[str] in adjacency."""
        graph = DirectedGraph()
        graph.add_edge("Data Structures", "Algorithms")
        graph.add_edge("Data Structures", "Algorithms")
        self.assertEqual(graph.vertices, {"Data Structures", "Algorithms"})
        self.assertEqual(set(graph.adjacency.keys()), graph.vertices)
        self.assertEqual(graph.adjacency["Data Structures"], {"Algorithms"})
        self.assertEqual(graph.adjacency["Algorithms"], set())
        self.assertEqual(graph.vertex_count(), 2)
        self.assertEqual(graph.edge_count(), 1)

    def test_self_loop_and_multi_vertex_cycle_supported(self) -> None:
        """FR-009: Self-loops (metrics -> metrics) and cycles (auth -> session -> user-profile -> auth)."""
        graph = DirectedGraph()
        graph.add_edge("metrics", "metrics")
        graph.add_edge("auth", "session")
        graph.add_edge("session", "user-profile")
        graph.add_edge("user-profile", "auth")

        self.assertIn("metrics", graph.adjacency["metrics"])
        self.assertEqual(graph.vertex_count(), 4)
        self.assertEqual(graph.edge_count(), 4)
        self.assertEqual(set(graph.adjacency.keys()), graph.vertices)


class TestGraphFormatter(unittest.TestCase):
    """T006: Unit tests for alphabetical output formatting (FR-011, SC-005)."""

    def test_format_graph_applies_alphabetical_order_only_on_display(self) -> None:
        graph = DirectedGraph()
        graph.add_vertex("watch")
        graph.add_edge("undershorts", "shoes")
        graph.add_edge("undershorts", "pants")
        graph.add_edge("pants", "belt")

        expected = "\n".join(
            [
                "Vertices: 5, Edges: 3",
                "Vertices:",
                "belt",
                "pants",
                "shoes",
                "undershorts",
                "watch",
                "Edges:",
                "pants -> belt",
                "undershorts -> pants",
                "undershorts -> shoes",
            ]
        )
        self.assertEqual(format_graph(graph), expected)

    def test_format_empty_graph(self) -> None:
        graph = DirectedGraph()
        expected = "Vertices: 0, Edges: 0\nVertices:\nEdges:"
        self.assertEqual(format_graph(graph), expected)


if __name__ == "__main__":
    unittest.main()
