import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qiskit.quantum_info import random_clifford

from clifford_synthesis import optimize_clifford
from map_stabilizer_circuit_to_graph_state_circuit import map_stabilizer_circuit_to_graph_state_circuit

def test_performance(num_qubits:int, num_runs:int = 10, use_edge_coloring: bool = False,
    use_symmetry_breaking: bool = False, test_clifford_circuit = False):
    """
    Test the performance of the depth optimal synthesis of graph states on randomly generated graph states.
    Specifically the average runtime and depth gets computed. There is also the possibility to test mqt qmaps
    sythesis of a random Clifford circuit as comparison.

    Args:
        num_qubits:
            Number of qubits in the Clifford circuits.
        num_runs:
            Number of Clifford circuits to test the runtime and depth on.
        use_edge_coloring:
            Flag to use the edge coloring approach.
        use_symmetry_breaking:
            Flag to enable symmetry breaking optimizations.
        use_symmetry_breaking:
            Flag to enable symmetry breaking optimizations.
        test_clifford_circuit:
            Flag to use mqt qmap synthesis of a random Clifford circuit.

    Returns:
        None

    Prints:
        Outputs average depth and runtime of the optimization process.
    """

    num_qubits = num_qubits
    num_runs = num_runs

    depths = 0
    runtimes = 0

    for i in range(num_runs):
        clifford_op = random_clifford(num_qubits, i)
        qc = clifford_op.to_circuit()
        if not test_clifford_circuit:
            qc, _ = map_stabilizer_circuit_to_graph_state_circuit(qc)
        _, result = optimize_clifford(qc, graph_state=not test_clifford_circuit, use_edge_coloring=use_edge_coloring, use_symmetry_breaking=use_symmetry_breaking)
        depths += result.depth + 1
        runtimes += result.runtime

    average_depth = depths/num_runs
    average_runtime = runtimes/num_runs
    print( f"Qubits:\t{num_qubits}\tRuns:\t{num_runs}\tAverage depth:\t{average_depth}\tAverage runtime:\t{average_runtime}")

print("Testing mqt qmap Clifford Synthesis:")
for i in range(2, 5):
    test_performance(i, test_clifford_circuit=True)
print("Testing SAT solvers approach:")
for i in range(2, 12):
    test_performance(i)
print("Testing edge coloring approach:")
for i in range(2, 13):
    test_performance(i, use_edge_coloring=True)
print("Testing edge coloring approach with symmetry breakers:")
for i in range(2, 26):
    test_performance(i, use_edge_coloring=True, use_symmetry_breaking=True)