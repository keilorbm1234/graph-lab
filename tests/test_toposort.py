"""Unit and NetworkX oracle tests for Feature 2: topological sort and cycle detection."""

from pathlib import Path
import unittest

import networkx as nx

from graph.formatter import format_topological_order
from graph.loader import load_graph_from_csv
from graph.model import DirectedGraph
from graph.toposort import CycleError, topological_sort

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def to_nx_digraph(graph: DirectedGraph) -> nx.DiGraph:
    """Convert a DirectedGraph into an equivalent NetworkX DiGraph for oracle assertions."""
    nx_graph = nx.DiGraph()
    for vertex in graph.vertices:
        nx_graph.add_node(vertex)
    for source, targets in graph.adjacency.items():
        for target in targets:
            nx_graph.add_edge(source, target)
    return nx_graph


def assert_valid_topological_order(
    testcase: unittest.TestCase,
    graph: DirectedGraph,
    order: list[str],
) -> None:
    """Verify FR-006: completeness/uniqueness and edge precedence."""
    testcase.assertEqual(len(order), graph.vertex_count())
    testcase.assertEqual(set(order), graph.vertices)
    position = {vertex: idx for idx, vertex in enumerate(order)}
    for source, targets in graph.adjacency.items():
        for target in targets:
            testcase.assertLess(
                position[source],
                position[target],
                f"Expected {source!r} before {target!r} in {order}",
            )


class TestCycleError(unittest.TestCase):
    """T002: Foundational unit tests for CycleError invariants and message formatting."""

    def test_cycle_error_multi_vertex_invariants_and_str(self) -> None:
        """T002: CycleError stores cycle list (len >= 2, cycle[0] == cycle[-1]) and formats message."""
        cycle = ["auth", "session", "user-profile", "auth"]
        err = CycleError(cycle)
        self.assertEqual(err.cycle, cycle)
        self.assertGreaterEqual(len(err.cycle), 2)
        self.assertEqual(err.cycle[0], err.cycle[-1])
        self.assertEqual(str(err), "cycle detected: auth -> session -> user-profile -> auth")

    def test_cycle_error_self_loop_invariants_and_str(self) -> None:
        """T002: CycleError for a self-loop stores [v, v] and formats 'cycle detected: v -> v'."""
        cycle = ["metrics", "metrics"]
        err = CycleError(cycle)
        self.assertEqual(err.cycle, ["metrics", "metrics"])
        self.assertEqual(len(err.cycle), 2)
        self.assertEqual(err.cycle[0], err.cycle[-1])
        self.assertEqual(str(err), "cycle detected: metrics -> metrics")


class TestTopologicalSortUS1(unittest.TestCase):
    """T004 & T005: Unit and NetworkX oracle tests for acyclic graphs (US1)."""

    def test_empty_graph_topological_sort_and_format(self) -> None:
        """T004: Empty graph produces [] and 'Topological order (0):'."""
        graph = DirectedGraph()
        order = topological_sort(graph)
        self.assertEqual(order, [])
        self.assertEqual(format_topological_order(order), "Topological order (0):")

    def test_small_dag_unit_and_fr006_properties(self) -> None:
        """T004: small-dag.csv satisfies FR-006 and places isolated 'watch' at position 9."""
        graph = load_graph_from_csv(DATA_DIR / "small-dag.csv")
        order = topological_sort(graph)
        assert_valid_topological_order(self, graph, order)
        expected = [
            "shirt",
            "socks",
            "tie",
            "undershorts",
            "pants",
            "belt",
            "jacket",
            "shoes",
            "watch",
        ]
        self.assertEqual(order, expected)
        # Determinism check across repeated calls
        self.assertEqual(topological_sort(graph), expected)
        self.assertEqual(
            format_topological_order(order),
            "Topological order (9):\n" + "\n".join(expected),
        )

    def test_networkx_oracle_on_dags(self) -> None:
        """T005: Compare topological_sort against nx.lexicographical_topological_sort on DAGs."""
        dag_cases: list[DirectedGraph] = [
            load_graph_from_csv(DATA_DIR / "small-dag.csv"),
            load_graph_from_csv(DATA_DIR / "cs-curriculum.csv"),
            DirectedGraph(),
        ]

        disconnected = DirectedGraph()
        disconnected.add_edge("c", "d")
        disconnected.add_edge("a", "b")
        disconnected.add_vertex("isolated_mid")
        dag_cases.append(disconnected)

        diamond = DirectedGraph()
        diamond.add_edge("root", "branch_b")
        diamond.add_edge("root", "branch_a")
        diamond.add_edge("branch_b", "sink")
        diamond.add_edge("branch_a", "sink")
        dag_cases.append(diamond)

        for idx, graph in enumerate(dag_cases):
            with self.subTest(case=idx):
                nx_graph = to_nx_digraph(graph)
                self.assertTrue(nx.is_directed_acyclic_graph(nx_graph))
                expected = list(nx.lexicographical_topological_sort(nx_graph))
                actual = topological_sort(graph)
                assert_valid_topological_order(self, graph, actual)
                self.assertEqual(actual, expected)


class TestCycleDetectionUS2(unittest.TestCase):
    """T012 & T013: Unit and NetworkX oracle tests for cycle detection and reconstruction (US2)."""

    def test_excludes_vertices_that_only_depend_on_cycle(self) -> None:
        """T012: Vertices in R that only depend on a cycle (like 'aaa' or 'api'/'web') are never chosen as v1."""
        graph = DirectedGraph()
        graph.add_edge("b_node", "c_node")
        graph.add_edge("c_node", "b_node")
        # 'aaa' is lexicographically smaller than 'b_node', and has in-degree > 0 so Kahn leaves it in R,
        # but 'aaa' only depends on the cycle and is NOT part of any cycle.
        graph.add_edge("b_node", "aaa")
        graph.add_edge("aaa", "zzz_sink")

        with self.assertRaises(CycleError) as ctx:
            topological_sort(graph)
        self.assertEqual(ctx.exception.cycle, ["b_node", "c_node", "b_node"])
        self.assertEqual(str(ctx.exception), "cycle detected: b_node -> c_node -> b_node")

    def test_bridge_between_two_cycles_is_excluded(self) -> None:
        """T012: A vertex on a one-way bridge between two cycles has out-degree > 0 in R but is not in a cycle."""
        graph = DirectedGraph()
        graph.add_edge("m1", "m2")
        graph.add_edge("m2", "m1")
        graph.add_edge("m1", "aaa_bridge")
        graph.add_edge("aaa_bridge", "n1")
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n1")

        with self.assertRaises(CycleError) as ctx:
            topological_sort(graph)
        self.assertEqual(ctx.exception.cycle, ["m1", "m2", "m1"])

    def test_self_loop_priority_and_deterministic_branch_selection(self) -> None:
        """T012: Self-loops participate under identical lexicographical rules, and cycle branches tie-break alphabetically."""
        # Case 1: self-loop on 'a_loop' is smaller than cycle 'b -> c -> b'
        graph1 = DirectedGraph()
        graph1.add_edge("a_loop", "a_loop")
        graph1.add_edge("b", "c")
        graph1.add_edge("c", "b")
        with self.assertRaises(CycleError) as ctx1:
            topological_sort(graph1)
        self.assertEqual(ctx1.exception.cycle, ["a_loop", "a_loop"])

        # Case 2: 'a' belongs to two cycles: a -> c -> a and a -> b -> a; must pick 'b' first
        graph2 = DirectedGraph()
        graph2.add_edge("a", "c")
        graph2.add_edge("c", "a")
        graph2.add_edge("a", "b")
        graph2.add_edge("b", "a")
        with self.assertRaises(CycleError) as ctx2:
            topological_sort(graph2)
        self.assertEqual(ctx2.exception.cycle, ["a", "b", "a"])

    def test_networkx_oracle_cycle_detection_equivalence(self) -> None:
        """T013: CycleError is raised if and only if nx.is_directed_acyclic_graph is False, and cycle edges exist."""
        cyclic_graphs: list[DirectedGraph] = [
            load_graph_from_csv(DATA_DIR / "build-with-cycle.csv"),
        ]

        self_loop_only = DirectedGraph()
        self_loop_only.add_edge("u", "v")
        self_loop_only.add_edge("metrics", "metrics")
        cyclic_graphs.append(self_loop_only)

        figure_eight = DirectedGraph()
        figure_eight.add_edge("x", "z")
        figure_eight.add_edge("z", "x")
        figure_eight.add_edge("x", "y")
        figure_eight.add_edge("y", "x")
        cyclic_graphs.append(figure_eight)

        for idx, graph in enumerate(cyclic_graphs):
            with self.subTest(cyclic_case=idx):
                nx_graph = to_nx_digraph(graph)
                self.assertFalse(nx.is_directed_acyclic_graph(nx_graph))
                with self.assertRaises(CycleError) as ctx:
                    topological_sort(graph)
                cycle = ctx.exception.cycle
                self.assertGreaterEqual(len(cycle), 2)
                self.assertEqual(cycle[0], cycle[-1])
                self.assertEqual(len(set(cycle[:-1])), len(cycle) - 1)
                for u, v in zip(cycle[:-1], cycle[1:]):
                    self.assertTrue(nx_graph.has_edge(u, v), f"Missing edge {u} -> {v}")

    def test_us3_as2_case_sensitive_unicode_ascii_tie_breaking_oracle(self) -> None:
        """T019 (US3-AS2): 'Zeta' precedes 'alpha' in both topological_sort and NetworkX oracle."""
        graph = DirectedGraph()
        graph.add_edge("alpha", "target_node")
        graph.add_edge("Zeta", "target_node")
        graph.add_vertex("Beta")

        nx_graph = to_nx_digraph(graph)
        expected = list(nx.lexicographical_topological_sort(nx_graph))
        actual = topological_sort(graph)
        self.assertEqual(actual, ["Beta", "Zeta", "alpha", "target_node"])
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
