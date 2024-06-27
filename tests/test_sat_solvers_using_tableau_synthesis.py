import unittest
import sys
import os
from parameterized import parameterized

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clifford_synthesis import optimize_clifford
from synthesis import sat_solvers_synthesis as gst
from circuit_provider import CircuitProvider


class TestGenerateTableau(unittest.TestCase):
    @parameterized.expand([
        ("example_circuit", [
            [0, 0, 1, 1, 0],
            [1, 1, 0, 0, 0]
        ]),
        ("only_h_gates", [
            [0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0]
        ]),
        ("circuit_1", [
            [1, 1, 1, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0, 0]
        ]),
    ])
    def test_generate_tableau(self, circuit_name, expected_tableau):
        qc = CircuitProvider.get_clifford_circuit(circuit_name)
        result = gst.get_stabilizer_tableau_representation(qc)
        self.assertEqual(result, expected_tableau)

class TestSATSolver(unittest.TestCase):

    @parameterized.expand([
        ("graph_circuit_2qubit", 1, 3, 2),
        ("graph_circuit_4qubit_1", 3, 9, 3),
        ("graph_circuit_4qubit_2", 3, 10, 3),
        ("graph_circuit_6qubit_1", 3, 12, 2),
        ("graph_circuit_6qubit_2", 3, 12, 2),
        ("graph_circuit_10qubit_1", 4, 25, 5),
        ("graph_circuit_10qubit_2", 4, 25, 5)
    ])
    def test_sat_solver_default(self, circuit_name, depth, gate_count, solver_calls):
        qc = CircuitProvider.get_graph_circuit(circuit_name)
        _, result = optimize_clifford(qc, graph_state=True)
        self.assertEqual(result.depth, depth)
        self.assertEqual(result.gates, gate_count)
        self.assertEqual(result.solver_calls, solver_calls)
    
    @parameterized.expand([
        ("graph_circuit_2qubit", 1, 3, 2),
        ("graph_circuit_4qubit_1", 3, 9, 3),
        ("graph_circuit_4qubit_2", 3, 10, 3),
        ("graph_circuit_6qubit_1", 3, 12, 2),
        ("graph_circuit_6qubit_2", 3, 12, 2),
        ("graph_circuit_10qubit_1", 4, 25, 5),
        ("graph_circuit_10qubit_2", 4, 25, 5)
    ])
    def test_sat_solver_symmetry_breakers(self, circuit_name, depth, gate_count, solver_calls):
        qc = CircuitProvider.get_graph_circuit(circuit_name)
        _, result = optimize_clifford(qc, graph_state=True, use_symmetry_breaking=True)
        self.assertEqual(result.depth, depth)
        self.assertEqual(result.gates, gate_count)
        self.assertEqual(result.solver_calls, solver_calls)

    @parameterized.expand([
        ("graph_circuit_2qubit", 1, 3, 2),
        ("graph_circuit_4qubit_1", 3, 9, 4),
        ("graph_circuit_4qubit_2", 3, 10, 4),
        ("graph_circuit_6qubit_1", 3, 12, 4),
        ("graph_circuit_6qubit_2", 3, 12, 4),
        ("graph_circuit_10qubit_1", 4, 25, 5),
        ("graph_circuit_10qubit_2", 4, 25, 5)
    ])
    def test_sat_solver_linear_search(self, circuit_name, depth, gate_count, solver_calls):
        qc = CircuitProvider.get_graph_circuit(circuit_name)
        _, result = optimize_clifford(qc, graph_state=True, linear_search=True)
        self.assertEqual(result.depth, depth)
        self.assertEqual(result.gates, gate_count)
        self.assertEqual(result.solver_calls, solver_calls)

if __name__ == '__main__':
    unittest.main()
