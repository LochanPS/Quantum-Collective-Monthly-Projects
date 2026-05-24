# FAQ

## General

**Do I need a quantum physics degree?**  
No. You need Python, NumPy, and basic matrix multiplication. The challenge README explains the math you actually need.

**Can I use Qiskit / PennyLane / Cirq?**  
No — build it yourself. Reading their source for inspiration is fine. Your code must be original.

**Can I work with a partner?**  
Yes. Include both names in your Discussion submission post.

**Is there a prize?**  
Community recognition and feedback from maintainers. No cash prizes.

---

## Submissions

**Where do I submit?**  
[Discussions → Submissions](../../discussions/categories/submissions). Post your fork link + a brief description. No PR needed.

**What if my code isn't finished or perfect?**  
Submit anyway. An incomplete solution with a README explaining what you got stuck on is valuable. This is a learning community.

**Can I update after submitting?**  
Yes — push to your fork and update your Discussion post with the new link or note the changes.

---

## Quantum Concepts

**What is a qubit?**  
A unit of quantum information. Unlike a classical bit (0 or 1), a qubit can be in superposition — both simultaneously — until measured.

**What is the state vector?**  
For N qubits: 2^N complex numbers. Each is an amplitude. Probability of measuring a given state = |amplitude|².

**What is the Kronecker product?**  
A way to combine matrices. Used to apply a 2×2 gate to one qubit in an N-qubit system. NumPy: `np.kron(A, B)`.

**Where to learn more:**
- [Qiskit Textbook](https://qiskit.org/learn/) — free, interactive, code-first
- [Quantum Computing: An Applied Approach](https://link.springer.com/book/10.1007/978-3-030-23922-0)
- [3Blue1Brown: Linear Algebra series](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) — the math foundation you need
