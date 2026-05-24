# Expected Usage Patterns

Your API doesn't have to match exactly — behavior must be equivalent.

## Bell State (Beginner minimum)

```python
qc = QuantumCircuit(2)
qc.h(0)
qc.cnot(0, 1)

counts = qc.measure_all(shots=1024)
# {'00': ~512, '11': ~512}
# '01' and '10' must not appear
```

## Chained API (Intermediate)

```python
counts = QuantumCircuit(2).h(0).cnot(0, 1).measure_all(shots=1000)
```

## Exact Probabilities (Intermediate)

```python
qc = QuantumCircuit(2)
qc.h(0).cnot(0, 1)

qc.probabilities()   # {'00': 0.5, '11': 0.5}
qc.statevector()     # array([0.707+0j, 0+0j, 0+0j, 0.707+0j])
```

## GHZ State — 3 qubits (Intermediate)

```python
qc = QuantumCircuit(3)
qc.h(0).cnot(0, 1).cnot(1, 2)
qc.probabilities()   # {'000': 0.5, '111': 0.5}
```

## Rotation Gates (Intermediate)

```python
import math
qc = QuantumCircuit(1)
qc.ry(0, math.pi / 2)   # equivalent to H up to global phase
```

## Large Circuit (Advanced)

```python
qc = QuantumCircuit(15)
for i in range(15):
    qc.h(i)
# All 2^15 = 32768 basis states have equal probability ~3e-5
```
