"""Construct and decode the Q022 reduction to 2-Cut on line graphs.

The target is represented by a simple 4-regular root H.  A target witness is a
bit for each edge of H, in the canonical lexicographic edge order; these are
the vertices of L(H).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

Edge = tuple[int, int]
Scope = tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class Reduction:
    source_n: int
    root_n: int
    root_edges: tuple[Edge, ...]
    special_case: str | None
    origin_source: tuple[int, ...] = ()
    representative_edges: tuple[int, ...] = ()
    module_edge_owner: dict[Edge, int] | None = None
    constraint_edge_owner: dict[Edge, int] | None = None
    scopes: tuple[Scope, ...] = ()

    def public_root(self) -> dict[str, Any]:
        return {"n": self.root_n, "edges": [list(edge) for edge in self.root_edges]}


def relation(bits: tuple[int, ...]) -> bool:
    """R(A,B): even parity and at least one triple is monochromatic."""
    return len(bits) == 6 and sum(bits) % 2 == 0 and (
        len(set(bits[:3])) == 1 or len(set(bits[3:])) == 1
    )


def equality_scope(left: int, right: int, mediator: int) -> Scope:
    return (left, mediator, mediator, right, mediator, mediator)


def cubic_multigraph_edges(vertices: list[int]) -> list[tuple[int, int]]:
    """Return edges of a connected 3-regular multigraph on an even set."""
    size = len(vertices)
    if size < 2 or size % 2:
        raise ValueError("the synchronization copy count must be positive and even")
    if size == 2:
        return [(vertices[0], vertices[1])] * 3

    edges = {
        tuple(sorted((vertices[i], vertices[(i + 1) % size])))
        for i in range(size)
    }
    edges.update(
        tuple(sorted((vertices[i], vertices[i + size // 2])))
        for i in range(size // 2)
    )
    result = sorted(edges)
    degree = Counter(v for edge in result for v in edge)
    if len(result) != 3 * size // 2 or set(degree.values()) != {3}:
        raise AssertionError("failed to construct the cubic synchronization multigraph")
    return result


def _validate_source(instance: Any) -> tuple[int, tuple[Edge, ...]]:
    if not isinstance(instance, dict) or set(instance) != {"n", "edges"}:
        raise ValueError("graph JSON must have exactly the keys 'n' and 'edges'")
    n = instance["n"]
    raw_edges = instance["edges"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(raw_edges, list):
        raise ValueError("edges must be a list")

    edges: set[Edge] = set()
    for item in raw_edges:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("each edge must be a two-element list")
        u, v = item
        if any(isinstance(x, bool) or not isinstance(x, int) for x in (u, v)):
            raise ValueError("vertex labels must be integers, not booleans")
        if not (0 <= u < n and 0 <= v < n) or u == v:
            raise ValueError("edge endpoints must be distinct labels in range(n)")
        edge = (u, v) if u < v else (v, u)
        if edge in edges:
            raise ValueError("parallel or repeated source edge")
        edges.add(edge)

    ordered_edges = tuple(sorted(edges))
    adjacency = [set() for _ in range(n)]
    for u, v in ordered_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    if any(len(neighbors) > 4 for neighbors in adjacency):
        raise ValueError("source maximum degree must be at most four")
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adjacency[u] - seen:
            seen.add(v)
            stack.append(v)
    if len(seen) != n:
        raise ValueError("source graph must be connected")
    return n, ordered_edges


def _validate_colors(colors: Any, expected: int) -> tuple[int, ...]:
    if not isinstance(colors, list) or len(colors) != expected:
        raise ValueError(f"colors must be a list of length {expected}")
    if any(
        isinstance(bit, bool) or not isinstance(bit, int) or bit not in (0, 1)
        for bit in colors
    ):
        raise ValueError("each color must be the integer 0 or 1")
    return tuple(colors)


def is_matching_cut(
    n: int, edges: tuple[Edge, ...], colors: tuple[int, ...]
) -> bool:
    if len(colors) != n or not colors or len(set(colors)) != 2:
        return False
    opposite = [0] * n
    for u, v in edges:
        if colors[u] != colors[v]:
            opposite[u] += 1
            opposite[v] += 1
            if opposite[u] > 1 or opposite[v] > 1:
                return False
    return True


def is_line_graph_2cut(root_n: int, edges: tuple[Edge, ...], colors: tuple[int, ...]) -> bool:
    """Check a 2-Cut of L(H) from the edge coloring of its root H."""
    if len(colors) != len(edges) or len(set(colors)) != 2:
        return False
    incident: list[list[int]] = [[] for _ in range(root_n)]
    for edge_id, (u, v) in enumerate(edges):
        incident[u].append(edge_id)
        incident[v].append(edge_id)
    for edge_id, (u, v) in enumerate(edges):
        color = colors[edge_id]
        opposite_count = sum(colors[j] != color for j in incident[u])
        opposite_count += sum(colors[j] != color for j in incident[v])
        if opposite_count > 2:
            return False
    return True


def _add_edge(edges: set[Edge], u: int, v: int) -> None:
    if u == v:
        raise AssertionError("root graph construction produced a loop")
    edge = (u, v) if u < v else (v, u)
    if edge in edges:
        raise AssertionError(f"root graph construction produced a repeated edge: {edge}")
    edges.add(edge)


def _connected_and_4_regular(root_n: int, edges: tuple[Edge, ...]) -> bool:
    if root_n < 1 or len(edges) * 2 != 4 * root_n:
        return False
    adjacency = [set() for _ in range(root_n)]
    for u, v in edges:
        if not (0 <= u < root_n and 0 <= v < root_n) or u == v:
            return False
        if v in adjacency[u]:
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
    return len(seen) == root_n


def _fixed_no_root() -> tuple[int, tuple[Edge, ...]]:
    """K5; its line graph has no nontrivial 2-Cut."""
    return 5, tuple(combinations(range(5), 2))


def _fixed_yes_root() -> tuple[int, tuple[Edge, ...]]:
    """Complement of C3 disjoint union C4; its line graph has a 2-Cut."""
    forbidden = {
        (0, 1), (0, 2), (1, 2),
        (3, 4), (4, 5), (5, 6), (3, 6),
    }
    edges = tuple(edge for edge in combinations(range(7), 2) if edge not in forbidden)
    return 7, edges


def _build_from_scopes(
    source_n: int, scopes: list[Scope]
) -> Reduction:
    """Split occurrences, synchronize them, and expand to K4/K2 modules."""
    occurrences = Counter(variable for scope in scopes for variable in scope)
    if set(occurrences) != set(range(source_n)):
        raise AssertionError("every source variable must occur in a constraint")
    if any(count < 2 or count % 2 for count in occurrences.values()):
        raise AssertionError("source relation construction must give positive even occurrences")

    copies_by_source: list[list[int]] = [[] for _ in range(source_n)]
    origin_source: list[int] = []
    regularized_scopes: list[Scope] = []
    for scope in scopes:
        copied: list[int] = []
        for source_variable in scope:
            new_variable = len(origin_source)
            origin_source.append(source_variable)
            copies_by_source[source_variable].append(new_variable)
            copied.append(new_variable)
        regularized_scopes.append(tuple(copied))  # type: ignore[arg-type]

    for source_variable, copies in enumerate(copies_by_source):
        for left, right in cubic_multigraph_edges(copies):
            mediator = len(origin_source)
            origin_source.append(source_variable)
            regularized_scopes.append(equality_scope(left, right, mediator))

    occurrence_count = Counter(v for scope in regularized_scopes for v in scope)
    if set(occurrence_count.values()) != {4}:
        raise AssertionError("regularization failed: every variable must occur exactly four times")
    variable_count = len(origin_source)
    root_edges_set: set[Edge] = set()
    module_vertices: list[tuple[int, int, int, int]] = []
    module_edge_owner: dict[Edge, int] = {}
    next_vertex = 0
    for variable in range(variable_count):
        vertices = tuple(range(next_vertex, next_vertex + 4))
        next_vertex += 4
        module_vertices.append(vertices)  # type: ignore[arg-type]
        for u, v in combinations(vertices, 2):
            edge = (u, v)
            _add_edge(root_edges_set, u, v)
            module_edge_owner[edge] = variable

    used_ports = [0] * variable_count
    constraint_edge_owner: dict[Edge, int] = {}
    for constraint_id, scope in enumerate(regularized_scopes):
        left, right = next_vertex, next_vertex + 1
        next_vertex += 2
        _add_edge(root_edges_set, left, right)
        constraint_edge_owner[(left, right)] = constraint_id
        for position, variable in enumerate(scope):
            port_index = used_ports[variable]
            if port_index >= 4:
                raise AssertionError("a variable module has more than four ports")
            used_ports[variable] += 1
            endpoint = left if position < 3 else right
            port_vertex = module_vertices[variable][port_index]
            edge = (endpoint, port_vertex) if endpoint < port_vertex else (port_vertex, endpoint)
            _add_edge(root_edges_set, endpoint, port_vertex)
            module_edge_owner[edge] = variable
    if used_ports != [4] * variable_count:
        raise AssertionError("not every variable module port was used exactly once")

    root_edges = tuple(sorted(root_edges_set))
    root_n = next_vertex
    if not _connected_and_4_regular(root_n, root_edges):
        raise AssertionError("expanded root is not connected, simple, and 4-regular")
    edge_index = {edge: i for i, edge in enumerate(root_edges)}
    representative_edges: list[int] = []
    for source_variable, copies in enumerate(copies_by_source):
        representative = copies[0]
        u, v = module_vertices[representative][:2]
        representative_edges.append(edge_index[(u, v)])

    return Reduction(
        source_n=source_n,
        root_n=root_n,
        root_edges=root_edges,
        special_case=None,
        origin_source=tuple(origin_source),
        representative_edges=tuple(representative_edges),
        module_edge_owner=module_edge_owner,
        constraint_edge_owner=constraint_edge_owner,
        scopes=tuple(regularized_scopes),
    )


def build_reduction(instance: Any) -> Reduction:
    """Return the deterministic root-graph reduction for a legal source graph."""
    n, source_edges = _validate_source(instance)
    if n == 1:
        root_n, root_edges = _fixed_no_root()
        return Reduction(n, root_n, root_edges, "single-vertex-no")
    if n == 2:
        # Every connected simple graph on two vertices is K2, which is YES.
        root_n, root_edges = _fixed_yes_root()
        return Reduction(n, root_n, root_edges, "two-vertex-yes")

    neighbors = [set() for _ in range(n)]
    for u, v in source_edges:
        neighbors[u].add(v)
        neighbors[v].add(u)

    # R(p,q,q,p,r,r) iff p=q or p=r, i.e. not(q=r != p).
    scopes: list[Scope] = []
    for center in range(n):
        for left, right in combinations(sorted(neighbors[center]), 2):
            scopes.append(
                (center, left, left, center, right, right)
            )
    if not scopes:
        raise AssertionError("a connected source with n >= 3 must create a constraint")
    return _build_from_scopes(n, scopes)


def reduce_graph(instance: Any) -> dict[str, Any]:
    """Map a connected simple max-degree-four graph to the root of a line graph."""
    return build_reduction(instance).public_root()


def target_witness_from_source(
    instance: Any, source_colors: Any
) -> list[int]:
    """Construct a valid target edge coloring from a source Matching Cut."""
    n, source_edges = _validate_source(instance)
    colors = _validate_colors(source_colors, n)
    if not is_matching_cut(n, source_edges, colors):
        raise ValueError("source colors are not a nontrivial Matching Cut")
    reduction = build_reduction(instance)

    if reduction.special_case == "two-vertex-yes":
        x4 = {4, 6}
        return [int(u in x4 or v in x4) for u, v in reduction.root_edges]
    if reduction.special_case is not None:
        raise ValueError("the one-vertex source is a NO instance and has no witness")

    regularized_colors = tuple(colors[v] for v in reduction.origin_source)
    assert reduction.module_edge_owner is not None
    assert reduction.constraint_edge_owner is not None
    output: list[int] = []
    for edge in reduction.root_edges:
        if edge in reduction.module_edge_owner:
            output.append(regularized_colors[reduction.module_edge_owner[edge]])
            continue
        constraint_id = reduction.constraint_edge_owner[edge]
        scope = reduction.scopes[constraint_id]
        left = tuple(regularized_colors[v] for v in scope[:3])
        right = tuple(regularized_colors[v] for v in scope[3:])
        if len(set(left)) == 1:
            output.append(left[0])
        elif len(set(right)) == 1:
            output.append(right[0])
        else:
            raise AssertionError("a satisfying R constraint must have a monochromatic side")
    if not is_line_graph_2cut(reduction.root_n, reduction.root_edges, tuple(output)):
        raise AssertionError("constructed target witness is not a 2-Cut")
    return output


def recover_source_witness(instance: Any, edge_colors: Any) -> list[int]:
    """Recover a source Matching Cut from any valid target 2-Cut witness."""
    n, source_edges = _validate_source(instance)
    reduction = build_reduction(instance)
    colors = _validate_colors(edge_colors, len(reduction.root_edges))
    if not is_line_graph_2cut(reduction.root_n, reduction.root_edges, colors):
        raise ValueError("target colors are not a nontrivial 2-Cut of the line graph")
    if reduction.special_case == "two-vertex-yes":
        return [0, 1]
    if reduction.special_case is not None:
        raise ValueError("the NO-instance target must not have a valid 2-Cut")

    source_colors = [
        colors[edge_id] for edge_id in reduction.representative_edges
    ]
    result = tuple(source_colors)
    if not is_matching_cut(n, source_edges, result):
        raise AssertionError("valid target witness did not decode to a Matching Cut")
    return list(result)


def _read_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(value: Any) -> None:
    json.dump(value, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    reduce_parser = subparsers.add_parser("reduce", help="output the target root graph")
    reduce_parser.add_argument("source_json", help="source graph JSON file, or '-' for stdin")
    witness_parser = subparsers.add_parser(
        "witness", help="map a source Matching Cut to target edge colors"
    )
    witness_parser.add_argument("source_json")
    witness_parser.add_argument("source_colors_json")
    recover_parser = subparsers.add_parser(
        "recover", help="recover a source Matching Cut from target edge colors"
    )
    recover_parser.add_argument("source_json")
    recover_parser.add_argument("target_colors_json")
    args = parser.parse_args()

    source = _read_json(args.source_json)
    if args.command == "reduce":
        _write_json(reduce_graph(source))
    elif args.command == "witness":
        witness_data = _read_json(args.source_colors_json)
        if not isinstance(witness_data, dict) or set(witness_data) != {"colors"}:
            raise ValueError("source witness JSON must be {'colors': [...]}")
        _write_json({"edge_colors": target_witness_from_source(source, witness_data["colors"])})
    else:
        witness_data = _read_json(args.target_colors_json)
        if not isinstance(witness_data, dict) or set(witness_data) != {"edge_colors"}:
            raise ValueError("target witness JSON must be {'edge_colors': [...]}")
        _write_json({"colors": recover_source_witness(source, witness_data["edge_colors"])})


if __name__ == "__main__":
    main()
