from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.quantum_info import StabilizerState
from qiskit.circuit.library import GraphState

import re
import ast
import stim

def map_stabilizer_circuit_to_graph_state_circuit(circuit: str | QuantumCircuit):
    """Finds the underlying graph state circuit (with the local unitaries in the back) of a stabilizer state ciruit

    Args:
        circuit:
            The stabilizer state circuit to map.
            If a string is given, it is interpreted as a QASM string or a filename.
            If a :class:`QuantumCircuit` is given, it is converted to a :class:`QuantumComputation`.

    Returns:
        A tuple containing the underlying graph state circuit under local clifford operations and the local unitaries represented in the way
        they get applied as (number of qubit, string description of gate) tuple
    """
      
    if isinstance(circuit, str):
        if circuit.endswith(".qasm"):
            circuit = QuantumCircuit.from_qasm_file(circuit)
        circuit = QuantumCircuit.from_qasm_str(circuit)
    
    # Convert the QuantumCircuit to a StabilizerState 
    stabilizers = str(StabilizerState(circuit))


    # Create a Tableau representation of the Satbilizer State                               
    stabilizers = re.search(r"StabilizerState\((\[.*?\])\)", stabilizers).group(1)
    stabilizers = ast.literal_eval(stabilizers)
    stabilizers = [s[0:] for s in stabilizers]
    pauli_list = [stim.PauliString(pauli) for pauli in stabilizers]
    stab_state = stim.Tableau.from_stabilizers(pauli_list)

    # Convert the Tableau to a graph state circuit with the local unitaries at the back
    g = stab_state.to_circuit("graph_state")

    # Exctract the adjacency matrix and the local unitaries from the graph state
    adjacency_matrix = [[0 for _ in range(g.num_qubits)] for _ in range(g.num_qubits)]
    local_unitaries: list[tuple[int, str]] = []
    reached_clifford_gates = 0
    for instruction in g:
        if instruction.name == 'CZ':
            targets = instruction.targets_copy()
            for a, b in zip(targets[::2], targets[1::2]):
                adjacency_matrix[a.value][b.value] = 1
                adjacency_matrix[b.value][a.value] = 1
        elif instruction.name == "TICK":
            reached_clifford_gates += 1
        elif reached_clifford_gates == 2:
            targets = instruction.targets_copy()
            for a in targets:
                local_unitaries.append((a.value, instruction.name))

    return GraphState(adjacency_matrix), local_unitaries

def append_local_unitaries_to_circuit(circuit: QuantumCircuit, local_unitaries: list[tuple[int, str]]):
    """Appends the give local unitaries to the end of a Quantumcircuit in the order they are provided

    Args:
        circuit:
            The circuit to add the unitaries to.
        local_unitaries:
            The unitaries to add to the back of the circuit, represented in a list of (number of qubit, string description of gate) tuples
            element describing the number

    Returns:
        The updated circuit with the unitaries in the back
    """
    for qubit, gate in local_unitaries:
        if gate == "X":
            circuit.x(qubit)
        elif gate == "Y":
            circuit.y(qubit)
        elif gate == "Z":
            circuit.z(qubit)
        elif gate == "H":
            circuit.h(qubit)
        elif gate == "S":
            circuit.s(qubit)
    return circuit