import unittest
import sys
import os
from parameterized import parameterized
from qiskit.quantum_info import StabilizerState

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map_stabilizer_circuit_to_graph_state_circuit import map_stabilizer_circuit_to_graph_state_circuit, append_local_unitaries_to_circuit
from clifford_synthesis import optimize_clifford
from circuit_provider import CircuitProvider


class TestMapStabilizerCircuitToGraphCircuit(unittest.TestCase):

    @parameterized.expand([
        ("example_circuit"),
        ("only_h_gates"),
        ("circuit_1"),
    ])
    def test_generate_tableau(self, name):
        quantumcircuit = CircuitProvider.get_clifford_circuit(name)
        result, clifford_gates = map_stabilizer_circuit_to_graph_state_circuit(quantumcircuit)
        result = append_local_unitaries_to_circuit(result, clifford_gates)
        s1 = StabilizerState(quantumcircuit)
        s2 = StabilizerState(result)
        self.assertTrue(s1.equiv(s2))

class TestMapStabilizerCircuitToGraphCircuitWithDepthOptimalSynthesis(unittest.TestCase):

    @parameterized.expand([
        ("example_circuit", 1),
        ("only_h_gates", 0),
        ("circuit_1", 3),
    ])
    def test_generate_tableau(self, name, depth):
        quantumcircuit = CircuitProvider.get_clifford_circuit(name)
        result_circuit, result = optimize_clifford(quantumcircuit, map_to_graph_state=True)
        s1 = StabilizerState(quantumcircuit)
        s2 = StabilizerState(result_circuit)
        self.assertTrue(s1.equiv(s2))
        self.assertEquals(result.depth, depth)

if __name__ == '__main__':
    unittest.main()
