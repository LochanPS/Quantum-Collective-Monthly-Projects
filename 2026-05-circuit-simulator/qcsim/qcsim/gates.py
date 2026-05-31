"""Standard quantum gate matrices.

All public functions return numpy arrays of dtype complex128.
Gate definitions follow Nielsen & Chuang unless otherwise noted.

Single-qubit gates return 2x2 arrays.
Two-qubit gates return 4x4 arrays (used internally; the circuit applies them
to arbitrary qubit pairs via Kronecker expansion).
Three-qubit gates return 8x8 arrays.
"""

from __future__ import annotations

import numpy as np

_S2 = 1.0 / np.sqrt(2.0)  # 1/√2


# ================================================================== #
#  Single-qubit gates
# ================================================================== #

def I() -> np.ndarray:
    """Identity gate. No-op.

    Returns:
        2x2 identity matrix.
    """
    return np.eye(2, dtype=complex)


def H() -> np.ndarray:
    """Hadamard gate. Creates equal superposition.

    H|0⟩ = (|0⟩ + |1⟩) / √2
    H|1⟩ = (|0⟩ - |1⟩) / √2

    Returns:
        2x2 complex array [[1,1],[1,-1]] / √2.
    """
    return np.array([[1, 1], [1, -1]], dtype=complex) * _S2


def X() -> np.ndarray:
    """Pauli-X (NOT) gate. Bit flip.

    X|0⟩ = |1⟩,  X|1⟩ = |0⟩

    Returns:
        2x2 complex array [[0,1],[1,0]].
    """
    return np.array([[0, 1], [1, 0]], dtype=complex)


def Y() -> np.ndarray:
    """Pauli-Y gate.

    Y|0⟩ = i|1⟩,  Y|1⟩ = -i|0⟩

    Returns:
        2x2 complex array [[0,-i],[i,0]].
    """
    return np.array([[0, -1j], [1j, 0]], dtype=complex)


def Z() -> np.ndarray:
    """Pauli-Z gate. Phase flip.

    Z|0⟩ = |0⟩,  Z|1⟩ = -|1⟩

    Returns:
        2x2 complex array [[1,0],[0,-1]].
    """
    return np.array([[1, 0], [0, -1]], dtype=complex)


def S() -> np.ndarray:
    """S gate (phase gate). S = √Z.

    S|0⟩ = |0⟩,  S|1⟩ = i|1⟩

    Returns:
        2x2 complex array [[1,0],[0,i]].
    """
    return np.array([[1, 0], [0, 1j]], dtype=complex)


def Sdg() -> np.ndarray:
    """S-dagger gate (inverse of S). Sdg = S†.

    Sdg|0⟩ = |0⟩,  Sdg|1⟩ = -i|1⟩

    Returns:
        2x2 complex array [[1,0],[0,-i]].
    """
    return np.array([[1, 0], [0, -1j]], dtype=complex)


def T() -> np.ndarray:
    """T gate (π/8 gate). T = √S.

    T|0⟩ = |0⟩,  T|1⟩ = e^(iπ/4)|1⟩

    Returns:
        2x2 complex array [[1,0],[0,e^(iπ/4)]].
    """
    return np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)


def Tdg() -> np.ndarray:
    """T-dagger gate (inverse of T). Tdg = T†.

    Returns:
        2x2 complex array [[1,0],[0,e^(-iπ/4)]].
    """
    return np.array([[1, 0], [0, np.exp(-1j * np.pi / 4)]], dtype=complex)


def SX() -> np.ndarray:
    """SX gate (√X gate). SX = (I + iX) / 2.

    Returns:
        2x2 complex array.
    """
    return np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex) * 0.5


def Rx(theta: float) -> np.ndarray:
    """Rotation around the X-axis by angle theta (radians).

    Rx(θ) = exp(-iθX/2) = [[cos(θ/2), -i·sin(θ/2)],
                             [-i·sin(θ/2), cos(θ/2)]]

    Args:
        theta: Rotation angle in radians.

    Returns:
        2x2 complex rotation matrix.
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=complex)


def Ry(theta: float) -> np.ndarray:
    """Rotation around the Y-axis by angle theta (radians).

    Ry(θ) = exp(-iθY/2) = [[cos(θ/2), -sin(θ/2)],
                             [sin(θ/2),  cos(θ/2)]]

    Args:
        theta: Rotation angle in radians.

    Returns:
        2x2 complex rotation matrix.
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def Rz(theta: float) -> np.ndarray:
    """Rotation around the Z-axis by angle theta (radians).

    Rz(θ) = exp(-iθZ/2) = [[e^(-iθ/2), 0],
                             [0, e^(iθ/2)]]

    Args:
        theta: Rotation angle in radians.

    Returns:
        2x2 complex rotation matrix.
    """
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
    )


def P(lam: float) -> np.ndarray:
    """Phase gate. Adds phase e^(iλ) to |1⟩, leaves |0⟩ unchanged.

    P(λ) = [[1, 0], [0, e^(iλ)]]
    Note: P(π/2) = S,  P(π/4) = T,  P(π) = Z.

    Args:
        lam: Phase angle lambda in radians.

    Returns:
        2x2 complex phase matrix.
    """
    return np.array([[1, 0], [0, np.exp(1j * lam)]], dtype=complex)


def U(theta: float, phi: float, lam: float) -> np.ndarray:
    """Generic single-qubit unitary gate (IBM U gate).

    U(θ,φ,λ) = [[cos(θ/2),        -e^(iλ)·sin(θ/2)],
                 [e^(iφ)·sin(θ/2),  e^(i(φ+λ))·cos(θ/2)]]

    Args:
        theta: Polar angle (rotation). 0 ≤ θ ≤ π.
        phi: Azimuthal start angle. 0 ≤ φ ≤ 2π.
        lam: Azimuthal end angle. 0 ≤ λ ≤ 2π.

    Returns:
        2x2 complex unitary matrix.
    """
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array(
        [
            [c, -np.exp(1j * lam) * s],
            [np.exp(1j * phi) * s, np.exp(1j * (phi + lam)) * c],
        ],
        dtype=complex,
    )


# ================================================================== #
#  Two-qubit gate matrices (4x4)
#  These are the standard matrices; the circuit embeds them at
#  arbitrary qubit positions via Kronecker expansion.
# ================================================================== #

def CNOT() -> np.ndarray:
    """CNOT gate matrix (control qubit first, then target qubit).

    Standard 4x4 matrix in computational basis {|00⟩, |01⟩, |10⟩, |11⟩}.
    Flips target when control is |1⟩.

    Returns:
        4x4 complex array.
    """
    return np.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex
    )


def CZ_mat() -> np.ndarray:
    """CZ gate matrix. Applies Z to target when control is |1⟩.

    Returns:
        4x4 complex array.
    """
    return np.diag([1.0, 1.0, 1.0, -1.0]).astype(complex)


def SWAP_mat() -> np.ndarray:
    """SWAP gate matrix. Exchanges two qubit states.

    Returns:
        4x4 complex array.
    """
    return np.array(
        [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex
    )


# ================================================================== #
#  Convenience: catalogue of all named single-qubit gates
# ================================================================== #

#: Maps gate name → factory function (for gates with no parameters).
SINGLE_QUBIT_GATES: dict[str, object] = {
    "I": I, "H": H, "X": X, "Y": Y, "Z": Z,
    "S": S, "Sdg": Sdg, "T": T, "Tdg": Tdg, "SX": SX,
}
