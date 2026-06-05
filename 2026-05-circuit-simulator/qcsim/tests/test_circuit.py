"""Core correctness tests for qcsim.

Run with: pytest tests/ -v
"""

from __future__ import annotations

import numpy as np
import pytest

from qcsim import QuantumCircuit
from qcsim.exceptions import QubitIndexError


# ================================================================== #
#  Initial state
# ================================================================== #

class TestInitialState:
    def test_zero_state_probability(self):
        qc = QuantumCircuit(3)
        probs = qc.probabilities()
        assert abs(probs.get("000", 0) - 1.0) < 1e-10

    def test_zero_state_statevector(self):
        qc = QuantumCircuit(4)
        sv = qc.statevector()
        assert abs(sv[0] - 1.0) < 1e-10
        assert np.all(np.abs(sv[1:]) < 1e-10)

    def test_norm_is_one(self):
        qc = QuantumCircuit(5)
        assert abs(qc._state.norm() - 1.0) < 1e-10


# ================================================================== #
#  Pauli gates
# ================================================================== #

class TestPauliGates:
    def test_x_flips(self):
        qc = QuantumCircuit(1)
        qc.x(0)
        assert abs(qc.probabilities().get("1", 0) - 1.0) < 1e-10

    def test_x_x_identity(self):
        qc = QuantumCircuit(1)
        qc.x(0).x(0)
        assert abs(qc.probabilities().get("0", 0) - 1.0) < 1e-10

    def test_y_on_zero(self):
        """Y|0⟩ = i|1⟩"""
        qc = QuantumCircuit(1)
        qc.y(0)
        sv = qc.statevector()
        assert abs(sv[0]) < 1e-10
        assert abs(sv[1] - 1j) < 1e-10

    def test_z_phase_flip(self):
        """Z|+⟩ = |−⟩: amplitude on |1⟩ negates."""
        qc = QuantumCircuit(1)
        qc.h(0).z(0)
        sv = qc.statevector()
        assert abs(sv[0] - 1 / np.sqrt(2)) < 1e-10
        assert abs(sv[1] + 1 / np.sqrt(2)) < 1e-10

    def test_z_z_identity(self):
        qc = QuantumCircuit(1)
        qc.h(0).z(0).z(0)
        ref = QuantumCircuit(1)
        ref.h(0)
        assert np.allclose(qc.statevector(), ref.statevector())


# ================================================================== #
#  Hadamard
# ================================================================== #

class TestHadamard:
    def test_h_superposition(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        probs = qc.probabilities()
        assert abs(probs.get("0", 0) - 0.5) < 1e-10
        assert abs(probs.get("1", 0) - 0.5) < 1e-10

    def test_h_h_identity(self):
        qc = QuantumCircuit(1)
        qc.h(0).h(0)
        assert abs(qc.probabilities().get("0", 0) - 1.0) < 1e-10

    def test_h_all_uniform(self):
        n = 4
        qc = QuantumCircuit(n)
        for i in range(n):
            qc.h(i)
        probs = qc.probabilities()
        assert len(probs) == 2 ** n
        for p in probs.values():
            assert abs(p - 1 / 2 ** n) < 1e-10


# ================================================================== #
#  Phase gates (S, T)
# ================================================================== #

class TestPhaseGates:
    def test_s_on_one(self):
        """S|1⟩ = i|1⟩"""
        qc = QuantumCircuit(1)
        qc.x(0).s(0)
        sv = qc.statevector()
        assert abs(sv[1] - 1j) < 1e-10

    def test_s_sdg_identity(self):
        qc = QuantumCircuit(1)
        qc.x(0).s(0).sdg(0)
        assert abs(qc.probabilities().get("1", 0) - 1.0) < 1e-10

    def test_t_on_one(self):
        """T|1⟩ = e^(iπ/4)|1⟩"""
        qc = QuantumCircuit(1)
        qc.x(0).t(0)
        sv = qc.statevector()
        assert abs(sv[1] - np.exp(1j * np.pi / 4)) < 1e-10

    def test_t_tdg_identity(self):
        qc = QuantumCircuit(1)
        qc.x(0).t(0).tdg(0)
        assert abs(qc.probabilities().get("1", 0) - 1.0) < 1e-10

    def test_s_s_equals_z(self):
        """S² = Z"""
        qc1 = QuantumCircuit(1)
        qc1.h(0).s(0).s(0)
        qc2 = QuantumCircuit(1)
        qc2.h(0).z(0)
        assert np.allclose(qc1.statevector(), qc2.statevector())


# ================================================================== #
#  Rotation gates
# ================================================================== #

class TestRotationGates:
    def test_rx_pi_equals_x(self):
        """Rx(π) = -iX (same up to global phase)."""
        qc = QuantumCircuit(1)
        qc.rx(0, np.pi)
        assert abs(qc.probabilities().get("1", 0) - 1.0) < 1e-10

    def test_ry_pi_equals_y_up_to_phase(self):
        qc = QuantumCircuit(1)
        qc.ry(0, np.pi)
        assert abs(qc.probabilities().get("1", 0) - 1.0) < 1e-10

    def test_rz_preserves_probabilities(self):
        """Rz is a phase gate — probabilities unchanged."""
        qc = QuantumCircuit(1)
        qc.h(0).rz(0, np.pi / 3)
        probs = qc.probabilities()
        assert abs(probs.get("0", 0) - 0.5) < 1e-10

    def test_rx_half_pi_superposition(self):
        """Rx(π/2)|0⟩ is equal superposition (same as H up to phase)."""
        qc = QuantumCircuit(1)
        qc.rx(0, np.pi / 2)
        probs = qc.probabilities()
        assert abs(probs.get("0", 0) - 0.5) < 1e-5
        assert abs(probs.get("1", 0) - 0.5) < 1e-5

    def test_probabilities_sum_one_after_rotation(self):
        qc = QuantumCircuit(3)
        qc.rx(0, 0.3).ry(1, 1.2).rz(2, 2.5)
        assert abs(sum(qc.probabilities().values()) - 1.0) < 1e-10


# ================================================================== #
#  CNOT gate
# ================================================================== #

class TestCNOT:
    def test_bell_state_exact(self):
        """H(0) + CNOT(0,1) → 50% |00⟩, 50% |11⟩."""
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        probs = qc.probabilities()
        assert abs(probs.get("00", 0) - 0.5) < 1e-10
        assert abs(probs.get("11", 0) - 0.5) < 1e-10
        assert probs.get("01", 0) < 1e-10
        assert probs.get("10", 0) < 1e-10

    def test_bell_state_measurement(self):
        np.random.seed(0)
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        counts = qc.measure_all(shots=10_000)
        assert counts.get("01", 0) == 0
        assert counts.get("10", 0) == 0
        for outcome in ("00", "11"):
            ratio = counts.get(outcome, 0) / 10_000
            assert 0.47 < ratio < 0.53

    def test_cnot_non_adjacent(self):
        """CNOT(0, 2) skipping qubit 1."""
        qc = QuantumCircuit(3)
        qc.x(0).cnot(0, 2)
        probs = qc.probabilities()
        assert abs(probs.get("101", 0) - 1.0) < 1e-10

    def test_cnot_reverse(self):
        """CNOT(1, 0) — control is higher-index qubit."""
        qc = QuantumCircuit(2)
        qc.x(1).cnot(1, 0)  # |10⟩ → |11⟩
        probs = qc.probabilities()
        assert abs(probs.get("11", 0) - 1.0) < 1e-10

    def test_cnot_cnot_identity(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1).cnot(0, 1)
        ref = QuantumCircuit(2)
        ref.h(0)
        assert np.allclose(qc.statevector(), ref.statevector())


# ================================================================== #
#  GHZ state
# ================================================================== #

class TestGHZ:
    def test_ghz_3_qubits(self):
        qc = QuantumCircuit(3)
        qc.h(0).cnot(0, 1).cnot(1, 2)
        probs = qc.probabilities()
        assert abs(probs.get("000", 0) - 0.5) < 1e-10
        assert abs(probs.get("111", 0) - 0.5) < 1e-10
        assert len(probs) == 2

    def test_ghz_5_qubits(self):
        n = 5
        qc = QuantumCircuit(n)
        qc.h(0)
        for i in range(n - 1):
            qc.cnot(i, i + 1)
        probs = qc.probabilities()
        assert abs(probs.get("0" * n, 0) - 0.5) < 1e-10
        assert abs(probs.get("1" * n, 0) - 0.5) < 1e-10


# ================================================================== #
#  SWAP gate
# ================================================================== #

class TestSWAP:
    def test_swap_basic(self):
        qc = QuantumCircuit(2)
        qc.x(0).swap(0, 1)  # |01⟩ → |10⟩
        probs = qc.probabilities()
        assert abs(probs.get("10", 0) - 1.0) < 1e-10

    def test_swap_non_adjacent(self):
        qc = QuantumCircuit(3)
        qc.x(0).swap(0, 2)  # |001⟩ → |100⟩
        probs = qc.probabilities()
        assert abs(probs.get("100", 0) - 1.0) < 1e-10

    def test_swap_swap_identity(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1).swap(0, 1).swap(0, 1)
        ref = QuantumCircuit(2)
        ref.h(0).cnot(0, 1)
        assert np.allclose(qc.statevector(), ref.statevector())


# ================================================================== #
#  CZ gate
# ================================================================== #

class TestCZ:
    def test_cz_phase_flip(self):
        """CZ|11⟩ = -|11⟩"""
        qc = QuantumCircuit(2)
        qc.x(0).x(1).cz(0, 1)
        sv = qc.statevector()
        # |11⟩ is index 3 in LSB: both bits set → index 1*2^0 + 1*2^1 = 3
        assert abs(sv[3] + 1.0) < 1e-10

    def test_cz_no_flip_on_zero(self):
        """CZ|00⟩ = |00⟩ (no effect)"""
        qc = QuantumCircuit(2)
        qc.cz(0, 1)
        sv = qc.statevector()
        assert abs(sv[0] - 1.0) < 1e-10

class TestSXdg:
    def test_sxdg_exact_amplitudes_on_zero(self):
        qc = QuantumCircuit(1)
        qc.sxdg(0)
        sv = qc.statevector()
        assert abs(sv[0] - 0.5 * (1 - 1j)) < 1e-10
        assert abs(sv[1] - 0.5 * (1 + 1j)) < 1e-10

    def test_sxdg_twice_equals_x(self):
        qc = QuantumCircuit(1)
        qc.sxdg(0).sxdg(0)
        probs = qc.probabilities()
        assert abs(probs.get("1", 0) - 1.0) < 1e-10

    def test_sxdg_inverts_sx(self):
        qc = QuantumCircuit(1)
        qc.sx(0).sxdg(0)
        probs = qc.probabilities()
        assert abs(probs.get("0", 0) - 1.0) < 1e-10


# ================================================================== #
#  Toffoli gate
# ================================================================== #

class TestToffoli:
    def test_toffoli_both_controls_one(self):
        """CCX|110⟩ = |111⟩"""
        qc = QuantumCircuit(3)
        qc.x(1).x(2).toffoli(1, 2, 0)
        probs = qc.probabilities()
        assert abs(probs.get("111", 0) - 1.0) < 1e-10

    def test_toffoli_one_control_zero(self):
        """CCX does nothing when a control is |0⟩"""
        qc = QuantumCircuit(3)
        qc.x(2).toffoli(1, 2, 0)  # ctrl1=0 → no flip
        probs = qc.probabilities()
        assert abs(probs.get("100", 0) - 1.0) < 1e-10


# ================================================================== #
#  5-qubit circuits
# ================================================================== #

class TestFiveQubits:
    def test_uniform_superposition(self):
        n = 5
        qc = QuantumCircuit(n)
        for i in range(n):
            qc.h(i)
        probs = qc.probabilities()
        assert len(probs) == 32
        for p in probs.values():
            assert abs(p - 1 / 32) < 1e-10

    def test_bell_on_non_adjacent_5q(self):
        """Bell state on qubits 0 and 4 in a 5-qubit circuit."""
        qc = QuantumCircuit(5)
        qc.h(0).cnot(0, 4)
        probs = qc.probabilities()
        assert abs(probs.get("00000", 0) - 0.5) < 1e-10
        assert abs(probs.get("10001", 0) - 0.5) < 1e-10

    def test_norm_preserved_after_many_gates(self):
        qc = QuantumCircuit(5)
        for i in range(5):
            qc.h(i)
        for i in range(4):
            qc.cnot(i, i + 1)
        qc.toffoli(0, 1, 4)
        assert abs(sum(qc.probabilities().values()) - 1.0) < 1e-10


# ================================================================== #
#  Measurement
# ================================================================== #

class TestMeasurement:
    def test_state_preserved_after_measure(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        sv_before = qc.statevector().copy()
        qc.measure_all(shots=500)
        qc.measure_all(shots=500)
        assert np.allclose(sv_before, qc.statevector())

    def test_measure_total_shots(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        counts = qc.measure_all(shots=777)
        assert sum(counts.values()) == 777

    def test_deterministic_state_collapses_to_one_outcome(self):
        qc = QuantumCircuit(1)
        qc.x(0)  # deterministic |1⟩
        counts = qc.measure_all(shots=100)
        assert counts == {"1": 100}


# ================================================================== #
#  Circuit operations
# ================================================================== #

class TestCircuitOps:
    def test_reset(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        qc.reset()
        assert abs(qc.probabilities().get("00", 0) - 1.0) < 1e-10
        assert len(qc._log) == 0

    def test_compose(self):
        """Composing two half-circuits equals the full circuit."""
        qc_full = QuantumCircuit(2)
        qc_full.h(0).cnot(0, 1)

        qc_a = QuantumCircuit(2)
        qc_a.h(0)
        qc_b = QuantumCircuit(2)
        qc_b.cnot(0, 1)
        qc_a.compose(qc_b)

        assert np.allclose(qc_full.statevector(), qc_a.statevector())


# ================================================================== #
#  Error handling
# ================================================================== #

class TestErrorHandling:
    def test_invalid_qubit_raises(self):
        qc = QuantumCircuit(2)
        with pytest.raises(QubitIndexError):
            qc.h(5)

    def test_zero_qubits_raises(self):
        with pytest.raises(QubitIndexError):
            QuantumCircuit(0)

    def test_too_many_qubits_raises(self):
        with pytest.raises(QubitIndexError):
            QuantumCircuit(21)

    def test_cnot_same_qubit_raises(self):
        qc = QuantumCircuit(2)
        with pytest.raises(QubitIndexError):
            qc.cnot(1, 1)

    def test_shots_zero_raises(self):
        qc = QuantumCircuit(1)
        with pytest.raises(ValueError):
            qc.measure_all(shots=0)

    def test_swap_same_qubit_raises(self):
        qc = QuantumCircuit(2)
        with pytest.raises(QubitIndexError):
            qc.swap(0, 0)


# ================================================================== #
#  Quantum algorithm correctness
# ================================================================== #

class TestAlgorithms:
    def test_deutsch_jozsa_constant_f0(self):
        """Constant f(x)=0: input qubit 0 (LSB) always measures |0⟩."""
        qc = QuantumCircuit(2)
        qc.x(1).h(0).h(1)
        # Oracle for f(x) = 0: do nothing
        qc.h(0)
        probs = qc.probabilities()
        # For a constant function, the input register (rightmost bit = qubit 0)
        # always measures |0⟩ regardless of what qubit 1 (ancilla) does.
        p_q0_zero = sum(p for s, p in probs.items() if s[-1] == "0")
        assert abs(p_q0_zero - 1.0) < 1e-10

    def test_deutsch_jozsa_balanced(self):
        """Balanced f(x)=x: qubit 0 measures |1⟩ always."""
        qc = QuantumCircuit(2)
        qc.x(1).h(0).h(1)
        # Oracle for f(x) = x: CNOT(0, 1)
        qc.cnot(0, 1)
        qc.h(0)
        probs = qc.probabilities()
        p_q0_one = sum(p for s, p in probs.items() if s[-1] == "1")
        assert abs(p_q0_one - 1.0) < 1e-10

    def test_grover_2qubit(self):
        """Grover's algorithm (1 iteration) on 2 qubits finds |11⟩."""
        qc = QuantumCircuit(2)
        # Initialise uniform superposition
        qc.h(0).h(1)
        # Oracle: mark |11⟩ with a phase flip (CZ)
        qc.cz(0, 1)
        # Diffusion operator
        qc.h(0).h(1)
        qc.x(0).x(1)
        qc.cz(0, 1)
        qc.x(0).x(1)
        qc.h(0).h(1)
        probs = qc.probabilities()
        # After 1 Grover iteration on 2 qubits, |11⟩ should dominate
        assert probs.get("11", 0) > 0.95


# ================================================================== #
#  Qiskit export
# ================================================================== #

class TestQiskitExport:
    def test_export_returns_string(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        code = qc.to_qiskit_code()
        assert isinstance(code, str)

    def test_export_contains_qiskit_import(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        code = qc.to_qiskit_code()
        assert "from qiskit import QuantumCircuit" in code

    def test_export_circuit_size(self):
        qc = QuantumCircuit(3)
        code = qc.to_qiskit_code()
        assert "QuantumCircuit(3, 3)" in code

    def test_export_single_qubit_gates(self):
        qc = QuantumCircuit(1)
        qc.h(0).x(0).y(0).z(0).s(0).t(0)
        code = qc.to_qiskit_code()
        assert "qc.h(0)" in code
        assert "qc.x(0)" in code
        assert "qc.y(0)" in code
        assert "qc.z(0)" in code
        assert "qc.s(0)" in code
        assert "qc.t(0)" in code

    def test_export_cnot(self):
        qc = QuantumCircuit(2)
        qc.cnot(0, 1)
        code = qc.to_qiskit_code()
        assert "qc.cx(0, 1)" in code

    def test_export_swap(self):
        qc = QuantumCircuit(2)
        qc.swap(0, 1)
        code = qc.to_qiskit_code()
        assert "qc.swap(0, 1)" in code

    def test_export_rotation_gates(self):
        import math
        qc = QuantumCircuit(1)
        qc.rx(0, math.pi / 2)
        code = qc.to_qiskit_code()
        assert "qc.rx(" in code
        assert ", 0)" in code

    def test_export_sxdg(self):
        qc = QuantumCircuit(1)
        qc.sxdg(0)
        code = qc.to_qiskit_code()
        assert "qc.sxdg(0)" in code

    def test_export_toffoli(self):
        qc = QuantumCircuit(3)
        qc.toffoli(0, 1, 2)
        code = qc.to_qiskit_code()
        assert "qc.ccx(0, 1, 2)" in code

    def test_export_custom_var_name(self):
        qc = QuantumCircuit(2)
        qc.h(0)
        code = qc.to_qiskit_code(var="bell")
        assert "bell = QuantumCircuit(2, 2)" in code
        assert "bell.h(0)" in code

    def test_export_includes_measure(self):
        qc = QuantumCircuit(2)
        qc.h(0).cnot(0, 1)
        code = qc.to_qiskit_code()
        assert "measure" in code

    def test_export_ghz_is_valid_python(self):
        """The exported code must be syntactically valid Python."""
        import ast
        qc = QuantumCircuit(3)
        qc.h(0).cnot(0, 1).cnot(0, 2)
        code = qc.to_qiskit_code()
        # Will raise SyntaxError if invalid
        ast.parse(code)


# ================================================================== #
#  OpenQASM 2.0 export
# ================================================================== #

class TestQASM2Export:
    def test_qasm_header(self):
        qc = QuantumCircuit(2)
        qasm = qc.to_qasm2()
        assert "OPENQASM 2.0;" in qasm
        assert 'include "qelib1.inc";' in qasm

    def test_qasm_registers(self):
        qc = QuantumCircuit(3)
        qasm = qc.to_qasm2()
        assert "qreg q[3];" in qasm
        assert "creg c[3];" in qasm

    def test_qasm_measure(self):
        qc = QuantumCircuit(2)
        qasm = qc.to_qasm2()
        assert "measure q -> c;" in qasm

    def test_qasm_single_qubit_gates(self):
        qc = QuantumCircuit(1)
        qc.h(0).x(0).y(0).z(0).s(0).t(0)
        qasm = qc.to_qasm2()
        assert "h q[0];" in qasm
        assert "x q[0];" in qasm
        assert "y q[0];" in qasm
        assert "z q[0];" in qasm
        assert "s q[0];" in qasm
        assert "t q[0];" in qasm

    def test_qasm_cnot(self):
        qc = QuantumCircuit(2)
        qc.cnot(0, 1)
        qasm = qc.to_qasm2()
        assert "cx q[0],q[1];" in qasm

    def test_qasm_swap(self):
        qc = QuantumCircuit(2)
        qc.swap(0, 1)
        qasm = qc.to_qasm2()
        assert "swap q[0],q[1];" in qasm

    def test_qasm_rotation_gates(self):
        import math
        qc = QuantumCircuit(1)
        qc.rx(0, math.pi)
        qasm = qc.to_qasm2()
        assert "rx(" in qasm
        assert ") q[0];" in qasm

    def test_qasm_toffoli(self):
        qc = QuantumCircuit(3)
        qc.toffoli(0, 1, 2)
        qasm = qc.to_qasm2()
        assert "ccx q[0],q[1],q[2];" in qasm

    def test_qasm_sxdg(self):
        qc = QuantumCircuit(1)
        qc.sxdg(0)
        qasm = qc.to_qasm2()
        assert "sxdg q[0];" in qasm

    def test_qasm_ghz_returns_string(self):
        qc = QuantumCircuit(3)
        qc.h(0).cnot(0, 1).cnot(0, 2)
        qasm = qc.to_qasm2()
        assert isinstance(qasm, str)
        assert len(qasm) > 0
