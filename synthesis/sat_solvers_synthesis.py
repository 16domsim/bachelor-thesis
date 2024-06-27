"""Main entry point for perforimng depth optimal synthesis of a Graph State using edge colouring"""

from __future__ import annotations

from typing import Any
from z3 import *
import time
import re
import ast
from qiskit import QuantumCircuit
from qiskit.quantum_info import StabilizerState

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from synthesis.synthesis_result import SynthesisResults
from utils import extract_adjacency_matrix, count_single_qubit_gates, count_two_qubit_gates

from z3 import *
import time
import re
import ast

def get_stabilizer_tableau_representation(circuit: QuantumCircuit):
    """Computes the stabilizer tableau of a Clifford Circuit"""

    # Get the stabilizer string of the circuit
    stabilizers = str(StabilizerState(circuit))
    stabilizers = re.search(r"StabilizerState\((\[.*?\])\)", stabilizers).group(1)
    stabilizers = ast.literal_eval(stabilizers)
    stabilizers = [s[1:] for s in stabilizers]
    
     # Compute the stabilizer tableau
    number_of_qubits = len(stabilizers[0])
    tableau = [[0] * (2 * number_of_qubits + 1) for _ in range(number_of_qubits)]  

    for i, stabilizer in enumerate(stabilizers):
        for j, pauli in enumerate(stabilizer):
            if pauli == 'X':
                tableau[i][j] = 1
            elif pauli == 'Z':
                tableau[i][number_of_qubits + j] = 1
            elif pauli == 'Y':
                tableau[i][j] = 1
                tableau[i][number_of_qubits + j] = 1
    
    return tableau

def synthesize_graph_state_sat_solver (circuit: QuantumCircuit, use_symmetry_breaking: bool = False, use_linear_search: bool = False):
    """Synthesizes a depth-optimal QuantumCircuit representation of a graph state using SAT solvers.

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
        two_qubit_gates = two_qubit_gates)

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
    """Performs linear search to find the minimum depth number for the sat solver appraoch on the given adjacency matrix.

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
    minimum_depth = 0
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
    """Performs binary search to find the minimum depth number for the sat solver appraoch on the given adjacency matrix.

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
    left_bound_depth = 0
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
    """Synthesizes a depth-optimal mapping of gates based on the given adjacency matrix, 
    optionally using symmetry breaking to encode more constraints.

    Args:
        adjacency_matrix:
            The adjacency matrix describing the graph.
        depth:
            The maximum number of colors that can be used for edges.
        use_symmetry_breaking:
            Flag indicating whether symmetry breaking should be used.

    Returns:
            A dictionary mapping each depth to a list of gates if the SAT encoding is satisfiable, 
            otherwise an empty dictionary.
    """
    n = len(adjacency_matrix)
    
    s = Solver()

    # Create SAT variables for each CZ Gate with constraints about the depth and the identity
    cz_gates = {}
    identities = {}
  
    for i in range(n):
            for j in range(i):
                if adjacency_matrix[i][j] == 1:
                    cz_gates[(i, j)] = Int(f'CZ_{i}_{j}')
                    s.add(cz_gates[(i, j)] >= 0, cz_gates[(i, j)] < depth)
                else:
                    identities[(i, j)] = Int(f'I_{i}_{j}')
                    s.add(identities[(i, j)] >= 0)

    # Add constraints to ensure that gates do not get applied at the same time on the same qubits
    for i in range(n):
        for j in range(i):
            if adjacency_matrix[i][j] == 1:
                for k in range(j):
                    if adjacency_matrix[i][k] == 1:
                        s.add(cz_gates[(i, j)] != cz_gates[(i, k)])
                    else:
                        s.add(cz_gates[(i, j)] != identities[(i, k)])
                for k in range(i):
                    if(k == j):
                        continue
                    if adjacency_matrix[j][k] == 1:
                        if j>k:
                            s.add(cz_gates[(i, j)] != cz_gates[(j, k)])
                        else:
                            s.add(cz_gates[(i, j)] != cz_gates[(k, j)])
                    else:
                        if j>k:
                            s.add(cz_gates[(i, j)] != identities[(j, k)])
                        else:
                            s.add(cz_gates[(i, j)] != identities[(k, j)])

    
    # When flag is set, add constraints to prevent equivalent gate permutations
    if use_symmetry_breaking:
         for i in range(n):
            for j in range(i):
                if adjacency_matrix[i][j] == 1:
                    for k in range(j):
                        if adjacency_matrix[i][k] != 1:
                            s.add(cz_gates[(i, j)] < identities[(i, k)])
                    for k in range(i):
                        if(k == j):
                            continue
                        if adjacency_matrix[j][k] != 1:
                            if j>k:
                                s.add(cz_gates[(i, j)] < identities[(j, k)])
                            else:
                                s.add(cz_gates[(i, j)] < identities[(k, j)])

    # Check satisfiability and return the result
    if s.check() == sat:
        model = s.model()
        result: dict[int, list[tuple[int, int]]] = {}
        
        for (i, j), var in cz_gates.items():
            color = model[var].as_long()
            if color not in result:
                result[color] = []
            result[color].append((i, j))
        return result
    else:
        return {}


def _map_synthesis_depth_optimal_mapping_to_qcircuit(depth_optimal_mapping: dict[int, list[tuple[int, int]]], adjacency_matrix: list[list[int]] ) -> QuantumCircuit:
    """Maps depth-optimal mapping of gates returned from the syntehsis of a graph with the given adjacency matrix to a QuantumCircuit.

    Args:
        depth_optimal_mapping:
            A dictionary mapping depth levels to lists of gates.
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