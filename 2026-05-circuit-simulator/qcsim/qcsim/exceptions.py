"""Custom exception hierarchy for qcsim."""


class QCSimError(Exception):
    """Base exception for all qcsim errors."""


class QubitIndexError(QCSimError, ValueError):
    """Raised when a qubit index is out of range for the circuit."""


class CircuitCompositionError(QCSimError, ValueError):
    """Raised when two circuits cannot be composed (qubit count mismatch, etc.)."""


class GateError(QCSimError, ValueError):
    """Raised when an invalid gate matrix is provided."""
