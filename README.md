# Q022 candidate reduction package

This standalone package contains a candidate deterministic polynomial-time reduction from connected simple Matching Cut instances of maximum degree at most four to 2-Cut on connected line graphs. Every produced line graph is represented by a connected simple 4-regular root, so every output line graph is 6-regular.

The proof includes both directions: it constructs a target 2-Cut from every source Matching Cut, and recovers a source Matching Cut from **every** valid target 2-Cut. The result is a candidate for independent review; it is not presented as externally verified or Lean checked.

## Contents

- paper/proof.md — complete reduction and recovery proof.
- algorithm.py — forward construction, target-witness construction, and recovery.
- tests/test_reduction.py — standard-library tests and exhaustive checks on small source graphs.
- SUBMISSION_NOTES.md — registry placement, status, and remaining publication steps.
- .gitignore — excludes generated Python caches and temporary directories from a future repository commit.
- .gitattributes — keeps tracked text files in a consistent line-ending format.

## Run

Requires Python 3.10 or later and only the standard library.

From this directory:

    py -3 -m unittest discover -s tests -v

Input graphs use JSON of the form {"n": 3, "edges": [[0,1],[1,2]]}. The target root graph is output in the same format; its sorted edges define the target witness-bit order.

Reduce a source graph:

    py -3 algorithm.py reduce source.json > target-root.json

Construct a target witness from a known source Matching Cut:

    py -3 algorithm.py witness source.json source-colors.json > target-colors.json

Recover a source Matching Cut from a target edge coloring:

    py -3 algorithm.py recover source.json target-colors.json > recovered-source-colors.json

The witness files have the shapes {"colors":[...]} and {"edge_colors":[...]} respectively.

## Verification status

The included test suite has been run in the prepared workspace: all seven tests pass. It checks the local relation, equality and synchronization gadgets, all connected simple source graphs through order four, both fixed small targets, and the stdin command-line path. Target cuts are checked by a test-only oracle that counts opposite colors directly from root-edge incidences, independently of the production checker. The source-witness oracle is also independent. These finite checks support the proof; they do not replace the universal argument in paper/proof.md. No Lean formalization is included. The package is not yet published and no registry pull request has been opened.
