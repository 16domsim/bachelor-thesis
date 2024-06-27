class SynthesisResults:
    """ Helper class to return the Synthesis result
    """
    def __init__(self, circuit: str, depth: int, gates: int, runtime: float,
                 single_qubit_gates: int, solver_calls: int, tableau: str, two_qubit_gates: int) -> None:
        self._circuit = circuit
        self._depth = depth
        self._gates = gates
        self._runtime = runtime
        self._single_qubit_gates = single_qubit_gates
        self._solver_calls = solver_calls
        self._tableau = tableau
        self._two_qubit_gates = two_qubit_gates
        self._is_sat = True

    def sat(self) -> bool:
        return self._is_sat

    def unsat(self) -> bool:
        return not self._is_sat

    @property
    def circuit(self) -> str:
        return self._circuit

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def gates(self) -> int:
        return self._gates

    @property
    def runtime(self) -> float:
        return self._runtime

    @property
    def single_qubit_gates(self) -> int:
        return self._single_qubit_gates

    @property
    def solver_calls(self) -> int:
        return self._solver_calls

    @property
    def tableau(self) -> str:
        return self._tableau

    @property
    def two_qubit_gates(self) -> int:
        return self._two_qubit_gates