from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter
from itertools import combinations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import algorithm


def source_graphs_through_order_four():
    for n in range(1, 5):
        possible_edges = list(combinations(range(n), 2))
        for mask in range(1 << len(possible_edges)):
            edges = tuple(
                edge for i, edge in enumerate(possible_edges) if mask & (1 << i)
            )
            adjacency = [set() for _ in range(n)]
            for u, v in edges:
                adjacency[u].add(v)
                adjacency[v].add(u)
            seen = {0}
            stack = [0]
            while stack:
                u = stack.pop()
                for v in adjacency[u] - seen:
                    seen.add(v)
                    stack.append(v)
            if len(seen) == n and all(len(neighbors) <= 4 for neighbors in adjacency):
                yield {"n": n, "edges": [list(edge) for edge in edges]}


def independent_matching_cut_oracle(graph):
    n = graph["n"]
    edges = tuple(tuple(edge) for edge in graph["edges"])
    witnesses = []
    for colors in product((0, 1), repeat=n):
        if independent_matching_cut(n, edges, colors):
            witnesses.append(colors)
    return witnesses


def independent_matching_cut(n, edges, colors):
    if len(colors) != n or len(set(colors)) != 2:
        return False
    crossing_degree = [0] * n
    for u, v in edges:
        if colors[u] != colors[v]:
            crossing_degree[u] += 1
            crossing_degree[v] += 1
    return max(crossing_degree, default=0) <= 1


def source_scopes_independently(graph):
    n = graph["n"]
    neighbors = [set() for _ in range(n)]
    for u, v in graph["edges"]:
        neighbors[u].add(v)
        neighbors[v].add(u)
    scopes = []
    for center in range(n):
        for left, right in combinations(sorted(neighbors[center]), 2):
            scopes.append((center, left, left, center, right, right))
    return scopes


def base_graph_is_connected_4_regular(root):
    n = root["n"]
    edges = [tuple(edge) for edge in root["edges"]]
    if len(set(edges)) != len(edges) or len(edges) * 2 != 4 * n:
        return False
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        if u == v:
            return False
        adjacency[u].add(v)
        adjacency[v].add(u)
    if any(len(neighbors) != 4 for neighbors in adjacency):
        return False
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adjacency[u] - seen:
            seen.add(v)
            stack.append(v)
    return len(seen) == n


def independent_line_graph_2cut(root, colors):
    """Check a cut directly from root-edge incidences, without production code."""
    n = root["n"]
    edges = tuple(tuple(edge) for edge in root["edges"])
    if len(colors) != len(edges) or len(set(colors)) != 2:
        return False
    incident_edges = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(edges):
        incident_edges[u].append(edge_id)
        incident_edges[v].append(edge_id)
    for edge_id, (u, v) in enumerate(edges):
        opposite = sum(
            colors[other_id] != colors[edge_id]
            for other_id in incident_edges[u] + incident_edges[v]
            if other_id != edge_id
        )
        if opposite > 2:
            return False
    return True


class ReductionTests(unittest.TestCase):
    def test_cli_reduce_reads_stdin(self):
        graph = {"n": 3, "edges": [[0, 1], [1, 2]]}
        script = Path(__file__).resolve().parents[1] / "algorithm.py"
        root = subprocess.run(
            [sys.executable, str(script), "reduce", "-"],
            check=True,
            capture_output=True,
            input=json.dumps(graph),
            text=True,
        )
        target_root = json.loads(root.stdout)
        self.assertTrue(base_graph_is_connected_4_regular(target_root))

    def test_local_relation_equals_matching_cut_pair_rule(self):
        for p, q, r in product((0, 1), repeat=3):
            self.assertEqual(
                algorithm.relation((p, q, q, p, r, r)),
                not (q == r and q != p),
            )

    def test_equality_gadget(self):
        accepted = []
        for p, q, t in product((0, 1), repeat=3):
            if algorithm.relation((p, t, t, q, t, t)):
                accepted.append((p, q, t))
        self.assertEqual(accepted, [(0, 0, 0), (1, 1, 1)])

    def test_cubic_synchronizers(self):
        for size in range(2, 22, 2):
            edges = algorithm.cubic_multigraph_edges(list(range(size)))
            degrees = Counter(v for edge in edges for v in edge)
            self.assertEqual(len(edges), 3 * size // 2)
            self.assertEqual(set(degrees), set(range(size)))
            self.assertEqual(set(degrees.values()), {3})
            adjacency = [set() for _ in range(size)]
            for u, v in edges:
                adjacency[u].add(v)
                adjacency[v].add(u)
            seen = {0}
            stack = [0]
            while stack:
                u = stack.pop()
                for v in adjacency[u] - seen:
                    seen.add(v)
                    stack.append(v)
            self.assertEqual(seen, set(range(size)))

    def test_fixed_no_instance_has_no_target_cut(self):
        graph = {"n": 1, "edges": []}
        reduction = algorithm.build_reduction(graph)
        self.assertEqual(reduction.root_n, 5)
        self.assertEqual(len(reduction.root_edges), 10)
        self.assertTrue(base_graph_is_connected_4_regular(reduction.public_root()))
        for colors in product((0, 1), repeat=len(reduction.root_edges)):
            self.assertEqual(
                algorithm.is_line_graph_2cut(
                    reduction.root_n, reduction.root_edges, colors
                ),
                independent_line_graph_2cut(reduction.public_root(), colors),
            )
            self.assertFalse(
                independent_line_graph_2cut(reduction.public_root(), colors)
            )

    def test_fixed_yes_instance_and_universal_recovery(self):
        graph = {"n": 2, "edges": [[0, 1]]}
        reduction = algorithm.build_reduction(graph)
        self.assertEqual(reduction.root_n, 7)
        self.assertEqual(len(reduction.root_edges), 14)
        self.assertTrue(base_graph_is_connected_4_regular(reduction.public_root()))

        witness = algorithm.target_witness_from_source(graph, [0, 1])
        self.assertTrue(
            independent_line_graph_2cut(reduction.public_root(), witness)
        )
        self.assertIn(tuple(algorithm.recover_source_witness(graph, witness)), {
            (0, 1), (1, 0)
        })

        # Check recovery for every valid target cut of this 14-edge root.
        for colors in product((0, 1), repeat=len(reduction.root_edges)):
            independently_valid = independent_line_graph_2cut(
                reduction.public_root(), colors
            )
            self.assertEqual(
                algorithm.is_line_graph_2cut(
                    reduction.root_n, reduction.root_edges, colors
                ),
                independently_valid,
            )
            if independently_valid:
                recovered = tuple(algorithm.recover_source_witness(graph, list(colors)))
                self.assertIn(recovered, {(0, 1), (1, 0)})

    def test_all_connected_sources_through_order_four(self):
        checked = 0
        for graph in source_graphs_through_order_four():
            checked += 1
            n = graph["n"]
            source_edges = tuple(tuple(edge) for edge in graph["edges"])
            source_witnesses = independent_matching_cut_oracle(graph)
            scopes = source_scopes_independently(graph)

            # Independently compare every source coloring with all local R tests.
            for colors in product((0, 1), repeat=n):
                r_csp_accepts = all(
                    algorithm.relation(tuple(colors[v] for v in scope))
                    for scope in scopes
                )
                nonconstant = len(set(colors)) == 2
                source_accepts = independent_matching_cut(n, source_edges, colors)
                self.assertEqual(r_csp_accepts and nonconstant, source_accepts)

            reduction = algorithm.build_reduction(graph)
            self.assertTrue(base_graph_is_connected_4_regular(reduction.public_root()))

            if n == 1:
                self.assertEqual(source_witnesses, [])
                continue

            for source_colors in source_witnesses:
                target_colors = algorithm.target_witness_from_source(
                    graph, list(source_colors)
                )
                self.assertTrue(
                    independent_line_graph_2cut(
                        reduction.public_root(), target_colors
                    )
                )
                recovered = tuple(
                    algorithm.recover_source_witness(graph, target_colors)
                )
                self.assertIn(recovered, source_witnesses)
        self.assertGreaterEqual(checked, 30)


if __name__ == "__main__":
    unittest.main()
