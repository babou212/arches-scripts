#!/usr/bin/env python3
"""Compare nodes between two arches model JSON files based on nodeid.

This script loads two arches model JSON files and:
1. Extracts all nodes from the graph[].nodes arrays
2. Compares nodes based on their nodeid
3. Outputs a JSON summary showing:
   - Nodes present only in first file
   - Nodes present only in second file 
   - Nodes present in both files with field-by-field differences

Example usage:
    python compare_models.py model1.json model2.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def generate_output_filename(file1: str, file2: str) -> str:
    """Generate an output filename based on the input model filenames."""
    name1 = Path(file1).stem
    name2 = Path(file2).stem
    
    return f"compare_{name1}_vs_{name2}_results.txt"


def load_nodes_by_id(filepath: str) -> Dict[str, Dict[str, Any]]:
    """Load a model JSON file and return a map of nodeid -> node."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes_by_id = {}
    
    graphs = data.get('graph', [])
    if not isinstance(graphs, list):
        graphs = [graphs]
    
    for graph in graphs:
        if not isinstance(graph, dict):
            continue
            
        nodes = graph.get('nodes', [])
        if not isinstance(nodes, list):
            continue
            
        for node in nodes:
            if not isinstance(node, dict):
                continue
                
            nodeid = node.get('nodeid')
            if nodeid:
                nodeid = str(nodeid)
                nodes_by_id[nodeid] = node

    return nodes_by_id


def cast_node(x: Dict[str, Any]) -> Dict[str, Any]:
    for k in ("nodeid", "nodegroup_id", "alias"):
        if k in x and x[k] is not None:
            try:
                x[k] = str(x[k])
            except Exception:
                pass
    return x


def compare_nodes(file_a_nodes: Dict[str, Dict], 
                 file_b_nodes: Dict[str, Dict]) -> Dict[str, Any]:
    """Compare two node dictionaries and return differences."""
    all_nodeids = set(file_a_nodes.keys()) | set(file_b_nodes.keys())
    
    results = {
        'only_in_first_file': [],
        'only_in_second_file': [],
        'present_in_both': [],
        'differing_fields': {}
    }
    
    for nodeid in sorted(all_nodeids):
        node_a = file_a_nodes.get(nodeid)
        node_b = file_b_nodes.get(nodeid)
        
        if node_a and not node_b:
            results['only_in_first_file'].append({
                'nodeid': nodeid,
                'name': node_a.get('name', 'Unknown'),
                'nodegroup_id': f"NODE_GROUP_ID: {node_a.get('nodegroup_id', 'Unknown')}"
            })
        elif node_b and not node_a:
            results['only_in_second_file'].append({
                'nodeid': nodeid,
                'name': node_b.get('name', 'Unknown'),
                'nodegroup_id': f"NODE_GROUP_ID: {node_b.get('nodegroup_id', 'Unknown')}"
            })
        else:
            results['present_in_both'].append({
                'nodeid': nodeid,
                'name': node_a.get('name', 'Unknown'),
                'nodegroup_id': f"NODE_GROUP_ID: {node_a.get('nodegroup_id', 'Unknown')}"
            })
            
            if node_a != node_b:
                differences = {}
                all_keys = set(node_a.keys()) | set(node_b.keys())
                
                for key in sorted(all_keys):
                    val_a = node_a.get(key)
                    val_b = node_b.get(key)
                    if val_a != val_b:
                        differences[key] = {
                            'first_file': val_a,
                            'second_file': val_b
                        }
                
                if differences:
                    results['differing_fields'][nodeid] = differences
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Compare nodes between two arches models based on nodeid'
    )
    parser.add_argument('file1', help='Path to first Model JSON file')
    parser.add_argument('file2', help='Path to second Model JSON file')
    parser.add_argument(
        '--output', '-o',
        help='Output file for comparison results (default: compare_[model1]_vs_[model2].txt)'
    )
    
    args = parser.parse_args()
    
    try:
        nodes_a = load_nodes_by_id(args.file1)
        nodes_b = load_nodes_by_id(args.file2)
        
        results = compare_nodes(nodes_a, nodes_b)
        
        results['summary'] = {
            'total_nodes_file1': len(nodes_a),
            'total_nodes_file2': len(nodes_b),
            'only_in_file1_count': len(results['only_in_first_file']),
            'only_in_file2_count': len(results['only_in_second_file']),
            'common_nodes_count': len(results['present_in_both']),
            'nodes_with_differences': len(results['differing_fields'])
        }
        
        def format_node_list(nodes):
            return '\n'.join(f"Node ID - {node['nodeid']} - Node name - {node['name']} - [{node['nodegroup_id']}]" 
                           for node in nodes)
        
        output_text = f"""Model JSON Node Comparison

Summary:
--------
Total nodes in file 1: {results['summary']['total_nodes_file1']}
Total nodes in file 2: {results['summary']['total_nodes_file2']}
Nodes only in file 1: {results['summary']['only_in_file1_count']}
Nodes only in file 2: {results['summary']['only_in_file2_count']}

Nodes only in first file:
------------------------
{format_node_list(results['only_in_first_file'])}

Nodes only in second file:
-------------------------
{format_node_list(results['only_in_second_file'])}

Nodes present in both files:
--------------------------
{format_node_list(results['present_in_both'])}
"""
        
        output_file = args.output if args.output else generate_output_filename(args.file1, args.file2)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"Results written to {output_file}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
