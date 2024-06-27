from qiskit import QuantumCircuit
from qiskit.circuit.library import GraphState

class CircuitProvider:
    @staticmethod
    def get_clifford_circuit(name):
        if name == "example_circuit":
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.cx(0, 1)
            qc.h(0)
            qc.h(1)
            return qc
        elif name == "only_h_gates":
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.h(1)
            return qc
        elif name == "circuit_1":
            qc = QuantumCircuit(4)
            qc.h(0)
            qc.cx(0, 1)
            qc.cx(0, 2)
            qc.cy(1, 3)
            qc.s(0)
            return qc
        else:
            raise ValueError(f"Unknown circuit name: {name}")
        
    @staticmethod
    def get_graph_circuit(name):
        if name == "graph_circuit_2qubit":
            adjsmat= [
                [0, 1],
                [1, 0]
            ]
            return GraphState(adjsmat)
        if name == "graph_circuit_4qubit_1":
            adjsmat= [
                [0, 1, 1, 0],
                [1, 0, 1, 1],
                [1, 1, 0, 1],
                [0, 1, 1, 0]
            ]
            return GraphState(adjsmat)
        elif name == "graph_circuit_4qubit_2":
            adjsmat = [
                [0, 1, 1, 1],
                [1, 0, 1, 1],
                [1, 1, 0, 1],
                [1, 1, 1, 0]
            ]
            return GraphState(adjsmat)
        elif name == "graph_circuit_6qubit_1":
            adjsmat= [
                [0, 1, 0, 0, 0, 0],
                [1, 0, 1, 0, 0, 0],
                [0, 1, 0, 1, 0, 1],
                [0, 0, 1, 0, 1, 0],
                [0, 0, 0, 1, 0, 1],
                [0, 0, 1, 0, 1, 0]
            ]
            return GraphState(adjsmat)
        elif name == "graph_circuit_6qubit_2":
            adjsmat = [
                [0, 1, 0, 0, 0, 0],
                [1, 0, 1, 1, 0, 0],
                [0, 1, 0, 1, 0, 0],
                [0, 1, 1, 0, 1, 0],
                [0, 0, 0, 1, 0, 1],
                [0, 0, 0, 0, 1, 0]
            ]
            return GraphState(adjsmat)
        elif name == "graph_circuit_10qubit_1":
            adjsmat = [
                [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                [1, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
                [1, 0, 0, 1, 0, 1, 0, 0, 1, 0],
                [0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
                [0, 0, 1, 0, 0, 1, 0, 1, 0, 0],
                [0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                [0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
            ]
            return GraphState(adjsmat)
        elif name == "graph_circuit_10qubit_2":
            adjsmat = [
                [0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
                [1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
                [1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                [0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 1, 0, 1, 0]
            ]
            return GraphState(adjsmat)
        else:
            raise ValueError(f"Unknown circuit name: {name}")
