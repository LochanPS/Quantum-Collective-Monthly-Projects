# Adding an Algorithm to qviz

The most common contribution. This walks through adding a new algorithm
module end to end. Prerequisite reading: [Architecture.md](Architecture.md)
and the **Grover bug** section in [Developer-Guide.md](Developer-Guide.md#the-grover-bug--read-before-writing-any-algorithm-with-a-bitstring-parameter).

## The contract

Your module exposes one function that builds a qcsim circuit and returns
an `AlgorithmResult`:

```python
from qcsim import QuantumCircuit
from .base import (
    PHASE_PREPARATION, PHASE_ORACLE, PHASE_INTERFERENCE,
    AlgorithmResult, ExecutionSummary, input_register,
)

def my_algorithm(param: str) -> AlgorithmResult:
    qc = QuantumCircuit(n)
    annotations: list[str] = []
    phases: list[str] = []

    def add(note: str, phase: str) -> None:
        annotations.append(note)
        phases.append(phase)

    # ... build the circuit, calling add(...) once per gate ...

    def summarize(step) -> str:
        return "plain-English answer read from the final step"

    def outcome(step) -> ExecutionSummary:
        return ExecutionSummary(measured=..., expected=..., success=..., takeaway=...)

    return AlgorithmResult(
        circuit=qc,
        annotations=annotations,
        title="My Algorithm",
        phases=phases,
        info={"Parameter": param},
        registers={"input": [...], "ancilla": [...]},
        summarize=summarize,
        outcome=outcome,
    )
```

## The one rule that breaks silently

**`annotations` and `phases` must each have exactly one entry per gate in
`circuit._log`, in order.** The CLI zips them onto steps by position. If
you apply a gate without calling `add(...)`, every later label attaches to
the wrong gate — no error, just wrong output.

The `add()` helper above ties "apply a gate" and "append its
annotation+phase" together so they can't drift. Use it. When a step
applies several gates (e.g. Hadamard on every qubit), call `add()` once
per gate.

## Phases

Tag each gate with one of the constants in `base.py`:
`PHASE_PREPARATION`, `PHASE_ORACLE`, `PHASE_DIFFUSION`,
`PHASE_INTERFERENCE`, `PHASE_TRANSFORM`, `PHASE_MEASUREMENT`. These drive
the progress bar and the windowed circuit view. Pick the phase that
matches the algorithm's conceptual stage. Free-form strings work too, but
sticking to the constants keeps the progress bar consistent across
algorithms.

## Bitstring parameters — the label-orientation trap

qcsim labels states `q(n-1)...q0` (leftmost = highest qubit). If your
parameter is a bitstring where `param[i]` should mean qubit `i`, reverse
it before indexing:

```python
target_bits = param[::-1]           # now target_bits[i] is qubit i
```

To read a result back out of a final state in the parameter's orientation,
use `input_register(bitstring, k)` from `base.py`.

**Test rule:** include at least one **non-palindromic** bitstring case
(`"01"`/`"10"`, `"100"`) in your tests. Symmetric inputs (`"11"`, `"101"`)
hide orientation bugs.

## Wire it up

1. Create `qviz/algorithms/my_algorithm.py`.
2. Export it in `qviz/algorithms/__init__.py`.
3. Add a builder + menu entry in `qviz/cli.py` (`_ALGORITHMS`,
   `_ALGORITHM_NAMES`).
4. Add tests in `tests/test_stepper.py`:
   - annotation count == gate count == step count
   - phases align (or rely on `test_phases_align_with_gates` if you add
     yours to its loop)
   - correctness (final state / recovered answer), with a non-palindrome case
   - `outcome().success` is `True` on a correct run

## Minimal example: a self-inverse "identity check"

```python
def echo(bits: str) -> AlgorithmResult:
    n = len(bits)
    qc = QuantumCircuit(n)
    ann, ph = [], []
    def add(note, phase): ann.append(note); ph.append(phase)

    order = bits[::-1]  # bits[i] -> qubit i
    for i, b in enumerate(order):
        if b == "1":
            qc.x(i); add(f"Set q{i} to |1>", PHASE_PREPARATION)

    def summarize(step):
        top = max(step.probabilities.items(), key=lambda kv: kv[1])[0]
        return f"State is |{top}>."

    def outcome(step):
        top = max(step.probabilities.items(), key=lambda kv: kv[1])[0]
        return ExecutionSummary(top, bits[::-1] and top, top == "".join(order),
                                "Trivial state prep — a template, not a real algorithm.")

    return AlgorithmResult(qc, ann, "Echo", ph, {"Bits": bits},
                           {"input": list(range(n))}, summarize, outcome)
```

## Checklist before you PR

- [ ] Returns an `AlgorithmResult`
- [ ] `annotations` and `phases` each == one per gate
- [ ] Phases use the `base.py` constants
- [ ] Bitstring params reversed correctly; non-palindrome test included
- [ ] `summarize` and `outcome` read from the final step
- [ ] Registered in `__init__.py` and `cli.py`
- [ ] Tests pass; `black --line-length 100` clean

See [Contributing.md](Contributing.md) for the submission workflow.
