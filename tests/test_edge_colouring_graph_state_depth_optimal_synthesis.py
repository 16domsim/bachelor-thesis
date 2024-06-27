import unittest
import sys
import os
from parameterized import parameterized

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clifford_synthesis import optimize_clifford
from circuit_provider import CircuitProvider


class TestEdgeColouring(unittest.TestCase):

    @parameterized.expand([
        ("graph_circuit_2qubit", 1, 3, 1),
        ("graph_circuit_4qubit_1", 3, 9, 2),
        ("graph_circuit_4qubit_2", 3, 10, 1),
        ("graph_circuit_6qubit_1", 3, 12, 3),
        ("graph_circuit_6qubit_2", 3, 12, 3),
        ("graph_circuit_10qubit_1", 4, 25, 5),
        ("graph_circuit_10qubit_2", 4, 25, 4)
    ])
    def test_edge_clouring_default(self, circuit_name, depth, gate_count, solver_calls):
        qc = CircuitProvider.get_graph_circuit(circuit_name)
        _, result = optimize_clifford(qc, graph_state=True, use_edge_coloring=True)
        self.assertEqual(result.depth, depth)
        self.assertEqual(result.gates, gate_count)
        self.assertEqual(result.solver_calls, solver_calls)
    
    @parameterized.expand([
        ("graph_circuit_2qubit", 1, 3, 1),
        ("graph_circuit_4qubit_1", 3, 9, 2),
        ("graph_circuit_4qubit_2", 3, 10, 1),
        ("graph_circuit_6qubit_1", 3, 12, 3),
        ("graph_circuit_6qubit_2", 3, 12, 3),
        ("graph_circuit_10qubit_1", 4, 25, 5),
        ("graph_circuit_10qubit_2", 4, 25, 4)
    ])
    def test_edge_clouring_symmetry_breakers(self, circuit_name, depth, gate_count, solver_calls):
        qc = CircuitProvider.get_graph_circuit(circuit_name)
        _, result = optimize_clifford(qc, graph_state=True, use_edge_coloring=True, use_symmetry_breaking=True)
        self.assertEqual(result.depth, depth)
        self.assertEqual(result.gates, gate_count)
        self.assertEqual(result.solver_calls, solver_calls)

    @parameterized.expand([
        ("graph_circuit_2qubit", 1, 3, 1),
        ("graph_circuit_4qubit_1", 3, 9, 2),
        ("graph_circuit_4qubit_2", 3, 10, 1),
        ("graph_circuit_6qubit_1", 3, 12, 2),
        ("graph_circuit_6qubit_2", 3, 12, 2),
        ("graph_circuit_10qubit_1", 4, 25, 3),
        ("graph_circuit_10qubit_2", 4, 25, 2)
    ])
    def test_edge_clouring_linear_search(self, circuit_name, depth, gate_count, solver_calls):
        qc = CircuitProvider.get_graph_circuit(circuit_name)
        _, result = optimize_clifford(qc, graph_state=True, use_edge_coloring=True, linear_search=True)
        self.assertEqual(result.depth, depth)
        self.assertEqual(result.gates, gate_count)
        self.assertEqual(result.solver_calls, solver_calls)

if __name__ == '__main__':
    unittest.main()
