# Channel Development — add a noise channel

Adding a noise channel is the headline contributor task. It's small: define the
channel's **Kraus operators**, and the engine handles the rest.

## What a channel is

A noise channel transforms the density matrix as
`rho -> Σₖ Kₖ rho Kₖ†`. You supply the list of 2×2 matrices `{Kₖ}` (channels are
single-qubit; the engine embeds them on whichever qubit the channel acts on).

For the channel to conserve probability, its operators must satisfy the
**completeness relation**:

```
Σₖ Kₖ† Kₖ = I
```

There's a built-in check for this: `channel.is_trace_preserving()`.

## The recipe

Add a subclass of `NoiseChannel` to `qnoise/channels.py`:

```python
class MyChannel(NoiseChannel):
    """One-line description of the physical process."""

    name = "my_channel"

    def __init__(self, p: float) -> None:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"p must be in [0, 1], got {p}")
        self.p = p

    def kraus(self) -> list[np.ndarray]:
        # Return your 2x2 Kraus operators as complex numpy arrays.
        return [
            np.sqrt(1 - self.p) * _I,
            np.sqrt(self.p) * _X,   # e.g. a bit-flip-like process
        ]
```

Then:
1. Export it in `qnoise/__init__.py` (add to the imports and `__all__`).
2. Add a test in `tests/test_channels.py` — at minimum
   `test_completeness_relation` and a trace/validity check (parametrize your
   channel into the existing lists).
3. Optionally add it to a preset in `qnoise/model.py`.

## Worked example: the phase-flip channel

Physical process: apply Z with probability `p`, do nothing with probability
`1 - p`. That's two Kraus operators:

```
K0 = sqrt(1 - p) · I      K1 = sqrt(p) · Z
```

Check completeness:
`K0†K0 + K1†K1 = (1-p)·I + p·Z†Z = (1-p)·I + p·I = I`. ✓

That's exactly the `PhaseFlip` channel already in `channels.py` — read it as a
template.

## Ideas for new channels (see the Roadmap for more)

- **Coherent over-rotation** — a gate that rotates slightly too far every time
  (a *unitary* error; single Kraus operator `Rz(ε)`-style).
- **Biased dephasing** — asymmetric phase noise.
- **Leakage** — population escaping to a non-computational level (needs care:
  either approximate within the qubit space or document the limitation).
- **Generalized amplitude damping** — T1 relaxation toward a thermal (non-zero
  temperature) state.

## Verifying your channel

```python
from qnoise import DensityMatrix, apply_channel
import numpy as np

ch = MyChannel(0.2)
assert ch.is_trace_preserving()

dm = DensityMatrix.from_statevector(np.array([1, 1]) / np.sqrt(2))  # |+>
apply_channel(dm, ch, 0)
assert dm.is_valid()          # Hermitian, trace 1, positive semidefinite
print(dm.purity())            # should drop below 1.0 if the channel adds noise
```
