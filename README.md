# compare_models.py

Compare nodes between two Arches model JSON files by `nodeid`.

This small command-line script loads two Arches model JSON files and compares the nodes found under the `graph[].nodes` arrays. It produces a human-readable text report summarizing:

- nodes only present in the first file
- nodes only present in the second file
- nodes present in both files (list)
- a summary with counts for each category

The script is intended as a quick way to spot node differences between two model exports.

## Requirements

- Python 3.7+ (uses only the standard library)

## Location

The script is `compare_models.py` at the repository root.

## Usage

Run from a shell:

    python compare_models.py path/to/model1.json path/to/model2.json

Options:

- `--output` / `-o`  : Write results to the specified file. If omitted, the script writes to a default filename generated from the two input filenames in the form `compare_<model1>_vs_<model2>_results.txt`.


## What the script does (details)

- Loads each input JSON file and looks for a top-level `graph` key. `graph` may be either an object or a list; the script handles both.
- From each graph object the script reads the `nodes` array (if present) and builds a mapping from `nodeid` -> node object.
- Nodes are compared by `nodeid`. For each `nodeid` the script classifies it into:
  - only in first file
  - only in second file
  - present in both files

## Output file

The default output file (if `--output` is not passed) is named:

```
compare_<model1>_vs_<model2>_results.txt
```

The text report contains:

- a Summary block with total node counts and counts for nodes only in file1, only in file2, and common nodes
- three sections listing nodes only in first file, only in second file, and nodes present in both files. Each list line follows the format:

  Node ID - <nodeid> - Node name - <name> - [NODE_GROUP_ID: <nodegroup_id>]

If you need a machine-readable output (JSON) with full field-level diffs, consider modifying the script to dump the `results` dictionary as JSON instead of (or in addition to) the current text report.

## Examples

1) Basic comparison and default report filename:

    python compare_models.py models/architecture_v1.json models/architecture_v2.json

Output:

    Results written to compare_architecture_v1_vs_architecture_v2_results.txt

2) Write to a custom filename:

    python compare_models.py a.json b.json --output diff_report.txt
