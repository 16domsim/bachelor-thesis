"""Main entry point for the Clifford synthesis module."""

from __future__ import annotations
import re

from qiskit import QuantumCircuit


def count_single_qubit_gates(circuit: QuantumCircuit) -> int:
    """Counts the number of single qubit gates in the given circuit"""
    single_qubit_gates = 0

    for _, qubits, _ in circuit.data:
        if len(qubits) == 1:
            single_qubit_gates += 1

    return single_qubit_gates

def count_two_qubit_gates(circuit: QuantumCircuit) -> int:
    """Counts the number of two qubit gates in the given circuit"""
    two_qubit_gates = 0

    for _, qubits, _ in circuit.data:
        if len(qubits) == 2:
            two_qubit_gates += 1

    return two_qubit_gates

def extract_adjacency_matrix(circuit_name: str) -> list[list[int]]:
    """Extracts an adjacency matrix from the string representation of a Quiskit Graph State.

    Args:
        circuit_name:
            The string representation of a Quiskit Graph State.

    Returns:
       The adjacency matrix extracted from the string.
    """
    # Find all numbers in the string
    matches = re.findall(r'\d+', circuit_name)
    numbers = list(map(int, matches))

    # Define the size of the matrix
    n = int(len(numbers) ** 0.5)

    return [numbers[i * n:(i + 1) * n] for i in range(n)]