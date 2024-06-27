"""Main entry point for the Clifford synthesis module."""

from __future__ import annotations

from qiskit import QuantumCircuit
from synthesis.synthesis_result import SynthesisResults

from mqt import qmap

import map_stabilizer_circuit_to_graph_state_circuit as mstg

from synthesis import sat_solvers_synthesis as sat_solver
from synthesis import edge_colouring_graph_state_depth_optimal_synthesis as edge_colouring

def optimize_clifford(
    circuit: str | QuantumCircuit,
    graph_state = False,
    map_to_graph_state = False,
    use_edge_coloring = False,
    use_symmetry_breaking = False,
    linear_search = False
) -> tuple[QuantumCircuit, SynthesisResults]:
    """Optimize a Clifford circuit using mqt qmap.
    There is the possibility to specifically optimize a graph circuit or
    mapping the Clifford circuit to a graph circuit and then optimize it as such.

    Args:
        circuit:
            The circuit to optimize.
            If a string is given, it is interpreted as a QASM string or a filename.
            If a :class:`QuantumCircuit` is given, it is converted to a :class:`QuantumComputation`.
        graph_state:
            Flag to set whether a graph circuit should be optimized.
        map_to_graph_state:
            Flag to set whether the give Clifford circuit should be mapped to its underlying graph state with its unitaries.
        use_edge_coloring:
            Flag to set whether a graph circuit should be optimized.
        use_symmetry_breaking:
            Flag to set whether symmetry breaking optimisatins should be used in the optimzation
        linear_search:
            Flag to set whether linear seach should be used to find the optimal depth in the varous approaches.

    Returns:
        A tuple containing the optimized circuit and the synthesis results.
    """
    circuit = _import_circuit(circuit)

    if(map_to_graph_state):
            circuit, unitaries = mstg.map_stabilizer_circuit_to_graph_state_circuit(circuit)
            graph_state = True

    if(graph_state):

        if(use_edge_coloring):
            circuit, result = edge_colouring.synthesize_graph_state_edge_colouring(circuit, use_symmetry_breaking, linear_search)
        else:
            circuit, result = sat_solver.synthesize_graph_state_sat_solver(circuit, use_symmetry_breaking, linear_search)
            
        if(map_to_graph_state):
            circuit = mstg.append_local_unitaries_to_circuit(circuit, unitaries)
    else:
        circuit, result = qmap.optimize_clifford(circuit, use_symmetry_breaking=use_symmetry_breaking, linear_search=linear_search)

    return circuit, result

def _import_circuit(circuit: str | QuantumCircuit ) -> QuantumCircuit:
    """Import a circuit from a string"""
    if isinstance(circuit, str):
        if circuit.endswith(".qasm"):
            circuit = QuantumCircuit.from_qasm_file(circuit)
        circuit = QuantumCircuit.from_qasm_str(circuit)
    return circuit