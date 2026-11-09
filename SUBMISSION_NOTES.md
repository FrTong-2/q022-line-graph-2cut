# OpenQuestion submission notes

## Intended entry

Add this as an additional candidate solution to [Reduction Research Q022](https://codingthrust.github.io/problem-reductions/open-questions/line-graph-two-cut.html), “Degree-four Matching Cut → Line-graph 2-Cut.” The construction maps the entry's connected simple maximum-degree-four Matching Cut instances to line graphs, and the proof gives recovery from every valid target witness. Its outputs are more restricted than the entry asks for: line graphs of connected simple 4-regular roots. The existing Q022 record already has a submitted solution, so this should be appended as a separate solution record without changing the question or existing record.

This also gives a hardness result for the broader Q008 target class, but Q022 is the better fit because the produced targets are line graphs.

## Evidence included

- Full forward construction and universal witness-recovery proof: paper/proof.md.
- Deterministic implementation: algorithm.py.
- Reproducible standard-library checks: tests/test_reduction.py.
- Local test command: py -3 -m unittest discover -s tests -v.

The tests independently enumerate all source colorings for connected simple graphs through order four, compare the local R constraints against Matching Cut directly, validate every constructed root, construct target witnesses for source YES instances, and check recovery against an independent source oracle. A test-only target oracle counts opposite colors from root-edge incidences; it is cross-checked against the implementation on every coloring of the fixed K5 and 14-edge roots. The tests also check recovery from every valid target cut of the fixed 14-edge YES root.

## Status and limitations

This is a candidate solution, not an externally verified result. The proof has had an internal review, but no independent researcher has reviewed this package. This package is intended as a distinct, stronger-subclass proof. Its public status would be “Solution submitted” until maintainers review it.

Lean is not required for that status. The registry distinguishes a submitted complete proof awaiting verification from a Lean-kernel-checked proof. A Lean formalization would only be needed to claim the latter status.

The workspace package is not yet hosted on a public Git remote. Before opening a registry pull request, push this repository to a public remote, record its full commit hash, and add a separate solution record to the existing Q022 JSON registry entry. Keep the current Q022 question and existing solution record unchanged. The official submission instructions require links to proof, code, and tests at a full Git commit.

## Suggested pull-request summary

Add an explicit reduction from connected maximum-degree-four Matching Cut to 2-Cut on connected line graphs whose roots are simple 4-regular graphs. The proof composes the source's neighbor-pair constraints with an even-occurrence synchronization gadget and a K4/K2 line-graph expansion. It includes a deterministic decoder for every valid target cut, polynomial size bounds, executable construction/recovery code, and exhaustive small-instance checks. The result is a candidate pending independent review; no Lean status is claimed.
