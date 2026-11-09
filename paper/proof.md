# A 4-Regular-Root Hardness Result for 2-Cut on Line Graphs

## Status

This is a candidate solution package for Reduction Research Q022. It gives an explicit polynomial-time map from connected simple Matching Cut instances of maximum degree at most four, together with recovery from every valid target cut. The target is represented by a connected simple 4-regular root graph.

The proof and code are prepared for independent review. This document does not claim that an external reviewer or the Q022 maintainers have verified the result, and it does not claim priority over unindexed work.

## Problems and encodings

The source instance is a connected simple graph \(G=(V,E)\), with maximum degree at most four. A source witness is a bit vector \(x\in\{0,1\}^{V}\) that is nonconstant and has at most one neighbor of the opposite bit at every vertex. This is a Matching Cut.

The target instance is a connected simple graph \(H\), supplied as a root for its line graph \(L(H)\). The target witness is a bit for each edge of \(H\), in the output's lexicographically sorted edge order. These bits color the vertices of \(L(H)\). They must use both colors, and each edge of \(H\), considered as a vertex of \(L(H)\), may have at most two oppositely colored incident edges in \(L(H)\).

Both graph encodings are JSON objects with keys n and edges. For example, n=3 and edges=[[0,1],[1,2]] represents a path on three vertices. Vertex labels are 0,...,n-1; there are no loops or repeated edges, and undirected edges are lexicographically sorted. The source domain requires connectedness and maximum degree at most four. The reduction output has a simple connected 4-regular root; the target witness has one integer bit per root edge.

## The local relation

For bits \(p,q,r\), define

\[
S(p,q,r) \quad\Longleftrightarrow\quad \neg(q=r\ne p).
\]

This is exactly the condition that \(p\) is not opposite to both \(q\) and \(r\).

Use the six-ary relation

\[
R(a_1,a_2,a_3,b_1,b_2,b_3)
\Longleftrightarrow
\left(\bigoplus_{i=1}^{3}a_i\oplus\bigoplus_{i=1}^{3}b_i=0\right)
\land
\left((a_1=a_2=a_3)\lor(b_1=b_2=b_3)\right).
\]

Then

\[
R(p,q,q,p,r,r)\quad\Longleftrightarrow\quad p=q\ \lor\ p=r
\quad\Longleftrightarrow\quad S(p,q,r).
\]

Indeed, the parity equation is automatic because each of \(p,q,r\) occurs twice. The first triple \((p,q,q)\) is monochromatic exactly when \(p=q\); the second triple \((p,r,r)\) is monochromatic exactly when \(p=r\).

## Reduction F

First handle the two smallest source graphs.

- If n=1, output H=K5. Its line graph has no 2-Cut, as proved below.
- If n=2, connectedness forces G=K2, which is a YES instance. Output the fixed 7-vertex root H+=K7-E(C3 disjoint union C4). Its line graph has a 2-Cut, also proved below.

Now suppose n>=3. For every vertex v and every unordered pair of distinct neighbors {u,w} in N_G(v), add the R-constraint

\[
R(x_v,x_u,x_u,x_v,x_w,x_w).
\]

Let \(\Phi_G\) be this six-ary CSP instance. By the local-relation identity, an assignment satisfies \(\Phi_G\) exactly when it is a valid two-coloring of G in which no vertex has two opposite-colored neighbors. Requiring the assignment to be nonconstant therefore gives exactly a Matching Cut of G.

Let \(m=\sum_{v\in V}\binom{\deg_G(v)}2\) be the number of constraints. Each variable's total number of positions in \(\Phi_G\) is positive and even: every constraint containing \(x_v\) contains it in exactly two of its six positions. Positivity follows because a vertex of degree at least two is a center of a constraint; a degree-one vertex in a connected graph of order at least three is a neighbor in a constraint centered at its neighbor.

Split every position of every constraint into a fresh occurrence variable. If \(x_v\) had \(D_v\) positions, these give \(D_v\) occurrence copies of \(x_v\), where \(D_v\) is a positive even integer. Join these copies by a connected 3-regular multigraph \(Q_v\):

- for \(D_v=2\), use two vertices joined by three parallel edges;
- for even \(D_v\ge4\), take a cycle on the \(D_v\) vertices and add the perfect matching of opposite pairs.

For each multigraph edge \(pq\), add a fresh mediator \(t_{pq}\) and one constraint

\[
R(p,t_{pq},t_{pq},q,t_{pq},t_{pq}).
\]

The equality gadget obeys

\[
R(p,t,t,q,t,t)\quad\Longleftrightarrow\quad p=q=t.
\]

The parity condition forces \(p=q\); once this holds, the monochromatic-triple condition forces \(p=t\). Thus every occurrence copy and mediator equals the original \(x_v\). The transformation preserves satisfying assignments bijectively and preserves whether the assignment is nonconstant.

Every occurrence copy appears once in its original constraint and three times as an endpoint of synchronization constraints, for four total positions. Each mediator appears four times in its one synchronization constraint. Hence every variable in the resulting instance \(\Psi_G\) occurs exactly four times. The incidence graph remains connected: the source variable-constraint incidence graph is connected, and each original variable has been replaced by a connected synchronization network.

Expand \(\Psi_G\) into a root graph \(H_G\):

1. Replace every CSP variable by a private \(K_4\), with its four vertices serving as its four occurrence ports.
2. Replace every six-ary constraint by a private \(K_2\). Attach its first three occurrence ports to one endpoint and its last three ports to the other endpoint.

The graph \(H_G\) is simple. Every occurrence position uses a distinct port, including repeated positions of a mediator variable; each constraint has private endpoints, and every synchronization edge has distinct endpoint variables. It is 4-regular: a \(K_4\) vertex has three internal edges and one port edge; a \(K_2\) endpoint has one internal edge and three port edges. The incidence graph of \(\Psi_G\) is connected, so \(H_G\) is connected.

The target is the line graph \(L(H_G)\), represented by its root \(H_G\). Since \(H_G\) is simple and 4-regular, \(L(H_G)\) is connected, claw-free, and 6-regular.

## Why the root gadgets encode R

Color the edges of a connected simple 4-regular root \(H\) with bits, and let \(r(v)\) be the number of incident edges of color 1. For a root edge \(uv\) colored 1, its number of opposite-colored neighbors in \(L(H)\) is

\[
(4-r(u))+(4-r(v)).
\]

For an edge colored 0, that number is \(r(u)+r(v)\). The two incident-edge sets are disjoint apart from the edge itself, which is not counted as opposite, because \(H\) is simple.

If the coloring is a 2-Cut, a vertex with red degree 1 would have a red incident edge whose other endpoint has red degree at least 5, impossible. A vertex with red degree 3 would have a blue incident edge whose other endpoint must have red degree at most -1, also impossible. Thus \(r(v)\in\{0,2,4\}\). A vertex of red degree 2 has exactly two neighbors of red degree 0 and two of red degree 4. No edge joins red-degree 0 to red-degree 4, and no edge joins two red-degree-2 vertices.

Conversely, a partition \((X_0,X_2,X_4)\) of \(V(H)\) gives a 2-Cut precisely when there are no \(X_0X_4\) or \(X_2X_2\) edges and each \(X_2\) vertex has exactly two neighbors in \(X_0\) and two in \(X_4\). Color an edge 0 if it touches \(X_0\), and 1 if it touches \(X_4\). The stated conditions make this well-defined and ensure every line-graph vertex has at most two opposite neighbors. Both colors occur exactly when \(X_0\) and \(X_4\) are nonempty.

### Variable module

Every vertex of a variable \(K_4\) has exactly one edge leaving its module. If a module vertex were in \(X_2\), its three \(K_4\) neighbors would all lie in one of \(X_0,X_4\): they cannot lie in \(X_2\), and no \(X_0X_4\) edge is allowed. This gives it at least three neighbors on one side, contradicting its required 2-and-2 split. Therefore no \(K_4\) vertex lies in \(X_2\), and the whole \(K_4\) lies in \(X_0\) or the whole \(K_4\) lies in \(X_4\). Its module bit is consequently well-defined.

### Constraint module

Let \(A\) and \(B\) be the colors of the three variable modules attached to the left and right endpoints of a constraint \(K_2\).

- If both endpoints lie in the same outer class \(X_c\), all six ports must have color \(c\).
- If the left endpoint lies in \(X_2\) and the right endpoint in \(X_c\), then \(B=(c,c,c)\), and \(A\) has exactly one \(c\) and two \(1-c\) entries.
- The symmetric case has \(A=(c,c,c)\), and \(B\) has exactly one \(c\) and two \(1-c\) entries.

These are exactly the tuples accepted by \(R(A,B)\). To see the converse directly, if both triples are monochromatic, the parity equation forces their common color to agree. If exactly one triple is monochromatic with color \(c\), parity forces the other triple to contain exactly one \(c\) and two \(1-c\) entries. The endpoint placement is unique in every case. Thus every legal target cut decodes to a satisfying \(\Psi_G\) assignment, and every satisfying assignment extends to a legal root coloring.

If the source assignment is nonconstant, two variable modules lie on opposite outer classes, so the target cut is nontrivial. If all variable modules have one color \(c\), each relation has six ports of color \(c\); the unique local extension puts both constraint endpoints in \(X_c\), so every root edge has color \(c\). Therefore

\[
G\text{ has a Matching Cut}
\quad\Longleftrightarrow\quad
L(H_G)\text{ has a 2-Cut}.
\]

The reverse direction holds for every target 2-Cut, not only for the cut produced by the forward construction: module rigidity recovers all variable values, the constraint signature enforces every source neighbor-pair condition, and nontriviality ensures the recovered source coloring is nonconstant.

## Fixed small instances

### No instance \(L(K_5)\)

The root \(K_5\) is connected, simple, and 4-regular. In any 2-Cut of its line graph, the root characterization would give \(X_0,X_2,X_4\). Since \(K_5\) has every possible edge, \(X_0\) and \(X_4\) cannot both be nonempty. But every \(X_2\) vertex requires neighbors in both \(X_0\) and \(X_4\), so \(X_2\) must be empty. The coloring is then constant. Thus \(L(K_5)\) is a NO instance.

### Yes instance \(L(H^+)\)

Let \(H^+\) have vertices \(0,\ldots,6\) and all edges of \(K_7\) except the edges of a triangle on \(\{0,1,2\}\) and a 4-cycle \(3-4-5-6-3\). This is a connected simple 4-regular graph. Set

\[
X_2=\{0,1,2\},\qquad X_0=\{3,5\},\qquad X_4=\{4,6\}.
\]

There are no \(X_0X_4\) or \(X_2X_2\) edges, and every \(X_2\) vertex has two neighbors in each outer class. Hence this is a nontrivial 2-Cut of \(L(H^+)\). The implementation colors a root edge 1 exactly when it has an endpoint in \(X_4\).

## Recovery map G(x,y)

Given a legal source graph and any valid target edge coloring:

1. Reconstruct \(H_G\) and the edge order deterministically from the source graph.
2. Check that the target coloring is nonconstant and that every line-graph vertex has at most two opposite-colored neighbors.
3. For each source vertex, take the color of a fixed internal edge of the \(K_4\) corresponding to its first occurrence copy.

The variable-module lemma ensures this bit is independent of the chosen internal edge. Synchronization constraints ensure it agrees with every occurrence of that source variable. The constraint-module lemma proves all source neighbor-pair constraints, and the target's nontriviality proves the recovered assignment is nonconstant. Thus the output is a valid source Matching Cut for every valid target witness. For \(K_2\), return the fixed witness \((0,1)\). The \(K_1\) target has no valid witness.

Both construction and recovery are deterministic and polynomial-time. Let \(m=\sum_v\binom{\deg(v)}2\le6n\). The six-ary source constraints have \(6m\) positions. Synchronization adds \(9m\) mediator variables and constraints. The regularized instance has \(15m\) variables and \(10m\) constraints. Consequently \(H_G\) has \(80m\) vertices and \(160m\) edges; \(L(H_G)\) has \(160m\) vertices and \(480m\) edges. The root representation is therefore linear in \(n\) in size up to vertex-label encoding.

## NP-hardness source

Chvátal proved Matching Cut NP-complete for graphs of maximum degree at most four: V. Chvátal, “Recognizing decomposable graphs,” *Journal of Graph Theory* 8 (1984), 51–53, [doi:10.1002/jgt.3190080106](https://doi.org/10.1002/jgt.3190080106). Restricting to connected source graphs preserves NP-hardness. Every disconnected graph with at least two nonempty components is a YES instance, since one component can be separated from the others with no crossing edge; map it to \(K_2\). Map an empty NO instance, if permitted by the source encoding, to \(K_1\); retain connected inputs. The connected maximum-degree-four source problem is therefore NP-hard. Matching Cut is in NP, as is target 2-Cut, so the target is NP-complete even on line graphs of connected simple 4-regular roots.

## Reproduction

The implementation is in algorithm.py; standard-library tests are in tests/test_reduction.py. The tests exhaust the local relation tables and all connected simple source graphs through order four, check the fixed target instances, verify the constructed roots are connected simple 4-regular graphs, and compare decoded outputs against an independent source-witness checker.

Run the following from the package directory: py -3 -m unittest discover -s tests -v

No Lean formalization is part of this submission. The mathematical proof is supplied in full, and finite tests are supporting evidence rather than a substitute for the proof.
