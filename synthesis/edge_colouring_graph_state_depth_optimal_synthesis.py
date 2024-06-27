"""Main entry point for perforimng depth optimal synthesis of a Graph State using edge colouring"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from z3 import *
import time
import networkx as nx
import pynauty as nauty

from qiskit import QuantumCircuit

from synthesis.synthesis_result import SynthesisResults
from utils import extract_adjacency_matrix, count_single_qubit_gates, count_two_qubit_gates


def synthesize_graph_state_edge_colouring (circuit: QuantumCircuit, use_symmetry_breaking: bool = False, use_linear_search: bool = False):
    """Synthesizes a depth-optimal QuantumCircuit representation of a graph state based leveraging the edge colouring problem.

    Args:
        circuit:
            Either a file path (.qasm) or a QuantumCircuit instance.
        use_symmetry_breaking:
            Flag indicating whether symmetry breaking should be used during the synthesis.
        use_linear_search:
            Flag indicating whether to use linear search (True) or binary search (False) to find the smallest chromatic number.

    Returns:
        A tuple containing the depth-optimal QuantumCircuit and synthesis results.
    """
    
    # Extract adjacency matrix from circuit name
    adjacency_matrix = extract_adjacency_matrix(circuit.name)

    # If adjacency matrix is all zeros, return the original circuit with no results
    if( all(all(cell == 0 for cell in row) for row in adjacency_matrix)):
        # Create SynthesisResults object with empty synthesis outcomes
        single_qubit_gates = count_single_qubit_gates(circuit)
        two_qubit_gates = count_two_qubit_gates(circuit)

        result: SynthesisResults = SynthesisResults(
        circuit = circuit.draw(),
        depth = 0,
        gates = single_qubit_gates + two_qubit_gates,
        runtime = 0,
        single_qubit_gates = single_qubit_gates,
        solver_calls = 0,
        tableau = "Not available yet",
        two_qubit_gates = two_qubit_gates
        )

        return circuit, result

    result: SynthesisResults
    depth_optimal_circuit : QuantumCircuit

    # Measure time for runtime calculation
    start_time = time.time()

    if use_linear_search:
        depth_optimal_circuit, depth, solver_calls = _linear_search(adjacency_matrix, use_symmetry_breaking)
    else:
        depth_optimal_circuit, depth, solver_calls = _binary_search(adjacency_matrix, use_symmetry_breaking)

    end_time = time.time()
    runtime = end_time - start_time

    single_qubit_gates = count_single_qubit_gates(depth_optimal_circuit)
    two_qubit_gates = count_two_qubit_gates(depth_optimal_circuit)

    # Create SynthesisResults object with the synthesis outcomes
    result: SynthesisResults = SynthesisResults(
        circuit = depth_optimal_circuit.draw(),
        depth = depth,
        gates = single_qubit_gates + two_qubit_gates,
        runtime = runtime,
        single_qubit_gates = single_qubit_gates,
        solver_calls = solver_calls,
        tableau = "Not available yet",
        two_qubit_gates = two_qubit_gates
    )

    return depth_optimal_circuit, result


def _linear_search(adjacency_matrix:list[list[int]], use_symmetry_breaking: bool) -> QuantumCircuit:
    """Performs linear search to find the smallest chromatic number for the edge colouring problem applied on the given adjacency matrix.

    Args:
        adjacency_matrix:
            The adjacency matrix describing the graph.
        use_symmetry_breaking:
            Flag indicating whether symmetry breaking should be used during the synthesis.

    Returns:
            A tuple containing the depth-optimal quantum circuit, the optimal depth, and the number of solver calls made.
    """
    depth = 0
    solver_calls = 0

    depth_optimal_mapping: dict[int, list[tuple[int, int]]] = []

    # Minimal and maxmial bounds where the smallest chromatic number will be found
    minimum_depth = _max_outgoing_connections(adjacency_matrix)
    maximum_depth = len(adjacency_matrix)

    # Find the depth iteratively
    for depth in range(minimum_depth, maximum_depth + 1):
        mapping = _synthesis(adjacency_matrix, depth, use_symmetry_breaking)
        solver_calls += 1

        if mapping:
            depth_optimal_mapping = mapping
            break
    
    return _map_synthesis_depth_optimal_mapping_to_qcircuit(depth_optimal_mapping, adjacency_matrix), depth, solver_calls

def _binary_search(adjacency_matrix:list[list[int]], use_symmetry_breaking: bool):
    """Performs binary search to find the smallest chromatic number for the edge colouring problem applied on the given adjacency matrix.

    Args:
        adjacency_matrix:
            The adjacency matrix describing the graph.
        use_symmetry_breaking:
            Flag indicating whether symmetry breaking should be used during the synthesis.

    Returns:
            A tuple containing the depth-optimal quantum circuit, the optimal depth, and the number of solver calls made.
    """
    solver_calls = 0
    depth_optimal_mapping: dict[int, list[tuple[int, int]]] = {}
    mappings_at_depth: dict[int, dict[int, list[tuple[int, int]]]] = {}

    # Initial bounds for binary search
    left_bound_depth = _max_outgoing_connections(adjacency_matrix)
    right_bound_depth = len(adjacency_matrix)

    found_optimal_depth = False

    while not found_optimal_depth:
        current_depth:int = (left_bound_depth + right_bound_depth) // 2

        # Perform synthesis at current depth if not already computed
        if current_depth not in mappings_at_depth:
            mappings_at_depth[current_depth] = _synthesis(adjacency_matrix, current_depth, use_symmetry_breaking)
            solver_calls += 1

        # Perform synthesis at previous depth if not at lower bound and already computed
        if current_depth != left_bound_depth and current_depth - 1 not in mappings_at_depth:
            mappings_at_depth[current_depth - 1] = _synthesis(adjacency_matrix, current_depth - 1, use_symmetry_breaking)
            solver_calls += 1

        depth_optimal_mapping = mappings_at_depth[current_depth]

        # Adjust bounds based on synthesis results
        if not mappings_at_depth[current_depth]:
            left_bound_depth = current_depth + 1
        elif current_depth != left_bound_depth and mappings_at_depth[current_depth - 1]:
            right_bound_depth = current_depth - 1
        else:
            found_optimal_depth = True

    return _map_synthesis_depth_optimal_mapping_to_qcircuit(depth_optimal_mapping, adjacency_matrix), current_depth, solver_calls 

def _synthesis(adjacency_matrix:list[list[int]], depth:int, use_symmetry_breaking: bool) -> dict[int, list[tuple[int, int]]]:
    """Synthesizes a depth-optimal mapping of edges based on the given adjacency matrix by endoding it in SAT given the maximum number of colors, 
    optionally using symmetry breaking to encode more constraints.

    Args:
        adjacency_matrix:
            The adjacency matrix describing the graph.
        depth:
            The maximum number of colors that can be used for edges.
        use_symmetry_breaking:
            Flag indicating whether symmetry breaking should be used.

    Returns:
            A dictionary mapping each color (depth level) to a list of edge tuples if the SAT encoding is satisfiable, 
            otherwise an empty dictionary.
    """
    n = len(adjacency_matrix)
    
    s = Solver()

    # Create SAT variables for each edge and SAT constraint defining the minimum and maximum color of an edge
    edge_color = {}
    edge_index = {}
    num_edges = 0
    for i in range(n):
            for j in range(i):
                if adjacency_matrix[i][j] == 1:
                    edge_color[(i, j)] = Int(f'edge_{i}_{j}')
                    s.add(edge_color[(i, j)] >= 0, edge_color[(i, j)] < depth)
                    edge_index[(i, j)] = num_edges
                    num_edges += 1

    # Add constraints to ensure adjacent edges have different colors
    for i in range(n):
        for j in range(i):
            if adjacency_matrix[i][j] == 1:
                for k in range(j):
                    if adjacency_matrix[i][k] == 1:
                        if i>k:
                            s.add(edge_color[(i, j)] != edge_color[(i, k)])
                        else:
                            s.add(edge_color[(i, j)] != edge_color[(k, i)])
                for k in range(i):
                    if adjacency_matrix[k][j] == 1:
                        if j>k:
                            s.add(edge_color[(i, j)] != edge_color[(j, k)])
                        else:
                            s.add(edge_color[(i, j)] != edge_color[(k, j)])


    # When flag is set, add constraints to encode each color for biggest cluster of adjacent edges
    if use_symmetry_breaking:

        # Find the biggest cluster
        max_ones = -1
        row_index_with_max_ones = -1
        for i, row in enumerate(adjacency_matrix):
            count_ones = sum(row)
            if count_ones > max_ones:
                max_ones = count_ones
                row_index_with_max_ones = i
        
        # Set colors of the edges
        color = 0
        for i, value in enumerate(adjacency_matrix[row_index_with_max_ones]):
            if value != 1:
                continue
            if row_index_with_max_ones > i:
                s.add(edge_color[(row_index_with_max_ones, i)] == color)
            else:
                s.add(edge_color[(i, row_index_with_max_ones)] == color)
            color += 1

    # Check satisfiability and return the result
    if s.check() == sat:
        model = s.model()
        result: dict[int, list[tuple[int, int]]] = {}
        
        for (i, j), var in edge_color.items():
            color = model[var].as_long()
            if color not in result:
                result[color] = []
            result[color].append((i, j))
        return result
    else:
        return {}


def _map_synthesis_depth_optimal_mapping_to_qcircuit(depth_optimal_mapping: dict[int, list[tuple[int, int]]], adjacency_matrix: list[list[int]] ) -> QuantumCircuit:
    """Maps depth-optimal mapping of edges returned from the synthsis of a graph with the given adjacency matrix to a QuantumCircuit.

    Args:
        depth_optimal_mapping:
            A dictionary mapping depth levels to lists of edge tuples, where each tuple represents an edge between two qubits.
        adjacency_matrix:
            The adjacency matrix describing the graph.

    Returns:
        The depth-optimal QuantumCircuit representing the graph.
    """
    
    num_qubits = len(adjacency_matrix)
    depth_optimal_circuit = QuantumCircuit(num_qubits, name="Depth optimal circuit of Graphstate g: %s" % (adjacency_matrix))
    
    # Apply Hadamard gates to all qubits
    depth_optimal_circuit.h(range(num_qubits))

    # Iterate over each depth level and apply CZ gates for each edge in the mapping
    for _, edges in depth_optimal_mapping.items():
        for edge in edges:
            depth_optimal_circuit.cz(edge[0], edge[1])
    
    return depth_optimal_circuit

def _max_outgoing_connections(adjacency_matrix: list[list[int]]) -> int:
    """Finds the maximum number of outgoing connections from any node in a graph 
    described by an adjacency matrix.

    Args:
        adjacency_matrix:
            The adjacency matrix describing the graph.

    Returns:
        The maximum number of outgoing connections from any node.
    """
        
    max_outgoing_connections = -1
    
    for i in range(len(adjacency_matrix)):
        temp_connections = 0
        for j in range(i + 1):
            if adjacency_matrix[i][j] == 1:
                temp_connections += 1
        max_outgoing_connections = max(max_outgoing_connections, temp_connections)
    
    return max_outgoing_connections



def _find_symmetric_edges(adjacency_matrix):
    """Finds the symmetric edges of a graph given an adjacency matrix. This function is for future use, potentially
    to encode more symmertry breakers.

    Args:
        adjacency_matrix:
            The adjacency matrix describing the graph.

    Returns:
        A dictionary containg sets of all the symmetric edges
    """
    
     # Create the line graph underlying the given asjacewncy matrix
    G = _adjacency_matrix_to_graph(adjacency_matrix)
    L = nx.line_graph(G)

    # Convert networkx graph to pynauty graph format
    g, node_to_index = _nx_to_pynauty(L)

    # Compute automorphism group and orbits using pynauty
    _, _, _, orbits, _ = nauty.autgrp(g)

    # Map the symmetric edges into a dictionary
    symmetric_edges = {}
    for i, value in enumerate(orbits):
        corresponding_tuple = [k for k, v in node_to_index.items() if v == i]
        if value not in symmetric_edges:
            symmetric_edges[value] = []
        symmetric_edges[value].extend(corresponding_tuple)

    return symmetric_edges

def _adjacency_matrix_to_graph(adjacency_matrix):
    """Converts an adjacency matrix to an nx Graph Object"""
    G = nx.Graph()
    num_nodes = len(adjacency_matrix)
    for i in range(num_nodes):
        for j in range(i + 1):
            if adjacency_matrix[i][j] == 1:
                G.add_edge(i, j)
    return G


def _nx_to_pynauty(G):
    """Converts an nx Graph to a pynauty graph, also return a mpaping between node and index to later map symmetric edges into a dictionary"""
    # Create a mapping from node to index 
    node_to_index = {node: idx for idx, node in enumerate(G.nodes())}

    # Convert adjacency list to indexed adjacency dictionary
    adjacency_dict = {node_to_index[node]: [node_to_index[neighbor] for neighbor in neighbors]
                      for node, neighbors in G.adjacency()}
    
    g = nauty.Graph(number_of_vertices=len(G), adjacency_dict=adjacency_dict)
    return g, node_to_index