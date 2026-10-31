"""Topological sort using Kahn's algorithm with a min-heap and deterministic cycle detection."""

import heapq

from graph.model import DirectedGraph


class CycleError(Exception):
    """Raised when a directed graph contains at least one cycle and cannot be topologically sorted."""

    def __init__(self, cycle: list[str]) -> None:
        if len(cycle) < 2 or cycle[0] != cycle[-1]:
            raise ValueError("cycle must contain at least 2 elements and start/end at the same vertex")
        self.cycle: list[str] = list(cycle)
        super().__init__(f"cycle detected: {' -> '.join(self.cycle)}")


def _reconstruct_deterministic_cycle(graph: DirectedGraph, remaining: set[str]) -> list[str]:
    """Identify the lexicographically smallest cycle vertex v1 and reconstruct its deterministic cycle."""
    sorted_remaining = sorted(remaining)
    sorted_successors: dict[str, list[str]] = {
        u: sorted(graph.adjacency[u] & remaining) for u in sorted_remaining
    }
    reverse_adjacency: dict[str, list[str]] = {u: [] for u in sorted_remaining}
    for u in sorted_remaining:
        for v in sorted_successors[u]:
            reverse_adjacency[v].append(u)

    for v1 in sorted_remaining:
        # Find all vertices in `remaining` that can reach `v1` in >= 1 directed steps
        can_reach_v1: set[str] = set()
        stack: list[str] = list(reverse_adjacency[v1])
        while stack:
            pred = stack.pop()
            if pred not in can_reach_v1:
                can_reach_v1.add(pred)
                stack.extend(reverse_adjacency[pred])

        if v1 not in can_reach_v1:
            continue

        # v1 is the lexicographically smallest vertex belonging to at least one cycle.
        # Reconstruct the closed cycle v1 -> v2 -> ... -> v1 traversing successors alphabetically.
        path: list[str] = [v1]
        on_path: set[str] = {v1}
        blocked: set[str] = set()

        def dfs(curr: str) -> bool:
            for nxt in sorted_successors[curr]:
                if nxt == v1:
                    path.append(v1)
                    return True
                if nxt in can_reach_v1 and nxt not in on_path and nxt not in blocked:
                    on_path.add(nxt)
                    path.append(nxt)
                    if dfs(nxt):
                        return True
                    path.pop()
                    on_path.remove(nxt)
            blocked.add(curr)
            return False

        if dfs(v1):
            return path

    raise RuntimeError("Unreachable: remaining vertices from Kahn must contain at least one cycle")


def topological_sort(graph: DirectedGraph) -> list[str]:
    """Compute the lexicographically smallest topological order using Kahn's algorithm with heapq."""
    in_degree: dict[str, int] = {vertex: 0 for vertex in graph.vertices}
    for source in graph.vertices:
        for target in graph.adjacency[source]:
            in_degree[target] += 1

    available_heap: list[str] = [vertex for vertex, deg in in_degree.items() if deg == 0]
    heapq.heapify(available_heap)

    order: list[str] = []
    while available_heap:
        current = heapq.heappop(available_heap)
        order.append(current)
        for neighbor in graph.adjacency[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(available_heap, neighbor)

    if len(order) < graph.vertex_count():
        remaining = graph.vertices - set(order)
        cycle = _reconstruct_deterministic_cycle(graph, remaining)
        raise CycleError(cycle)

    return order
