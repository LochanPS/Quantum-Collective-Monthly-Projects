"""Metrics that quantify how far a noisy result drifted from the ideal one."""

from __future__ import annotations

from typing import Dict

import numpy as np

from .density import DensityMatrix


def fidelity(rho: DensityMatrix, sigma: DensityMatrix) -> float:
    """State fidelity F(rho, sigma) in [0, 1]; 1.0 iff the states are identical.

    Fast path when either state is pure (the common ideal-vs-noisy case):
    ``F = <psi|sigma|psi>``. Otherwise uses the Uhlmann form
    ``F = (Tr sqrt(sqrt(rho) sigma sqrt(rho)))^2``.

    Args:
        rho: First state.
        sigma: Second state.

    Returns:
        Fidelity as a float in [0, 1].
    """
    a = rho.matrix()
    b = sigma.matrix()

    # Pure-state fast path: if a is (near) rank-1, F = <psi| b |psi>.
    psi = _pure_vector(a)
    if psi is not None:
        return float(np.real(psi.conj() @ b @ psi))
    psi = _pure_vector(b)
    if psi is not None:
        return float(np.real(psi.conj() @ a @ psi))

    # General Uhlmann fidelity via eigen-decomposition sqrt (Hermitian PSD).
    sqrt_a = _sqrtm_psd(a)
    inner = sqrt_a @ b @ sqrt_a
    eigvals = np.linalg.eigvalsh(inner)
    eigvals = np.clip(eigvals.real, 0.0, None)
    return float(np.sum(np.sqrt(eigvals)) ** 2)


def trace_distance(rho: DensityMatrix, sigma: DensityMatrix) -> float:
    """Trace distance = 1/2 * sum |eigenvalues(rho - sigma)|, in [0, 1]."""
    diff = rho.matrix() - sigma.matrix()
    eigvals = np.linalg.eigvalsh((diff + diff.conj().T) / 2)
    return float(0.5 * np.sum(np.abs(eigvals)))


def tvd(dist_a: Dict[str, float], dist_b: Dict[str, float]) -> float:
    """Total-variation distance between two probability distributions.

    ``TVD = 1/2 * sum_x |a(x) - b(x)|`` over all bitstrings, in [0, 1].
    """
    keys = set(dist_a) | set(dist_b)
    return float(0.5 * sum(abs(dist_a.get(k, 0.0) - dist_b.get(k, 0.0)) for k in keys))


# --------------------------------------------------------------------------- #
#  helpers
# --------------------------------------------------------------------------- #

def _pure_vector(rho: np.ndarray, tol: float = 1e-9):
    """Return the state vector if ``rho`` is pure (rank 1), else None."""
    if abs(np.trace(rho @ rho).real - 1.0) > 1e-7:
        return None
    eigvals, eigvecs = np.linalg.eigh(rho)
    idx = int(np.argmax(eigvals))
    if abs(eigvals[idx] - 1.0) > 1e-6:
        return None
    return eigvecs[:, idx]


def _sqrtm_psd(a: np.ndarray) -> np.ndarray:
    """Matrix square root of a Hermitian PSD matrix via eigen-decomposition."""
    eigvals, eigvecs = np.linalg.eigh((a + a.conj().T) / 2)
    eigvals = np.clip(eigvals.real, 0.0, None)
    return (eigvecs * np.sqrt(eigvals)) @ eigvecs.conj().T
