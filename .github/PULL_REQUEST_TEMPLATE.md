## What does this PR do?

<!-- One sentence summary -->

## Type of change

- [ ] 🐛 Bug fix (challenge files, README, tests)
- [ ] ✨ New gate (adds gate to qcsim)
- [ ] 📚 New circuit (adds circuit to circuit-library)
- [ ] 📝 Documentation improvement
- [ ] 🔧 CI / tooling

---

## For new gates (`feat(gates): ...`)

- [ ] Gate matrix is unitary (`U†U = I`) — verified with check in `docs/adding-gates.md`
- [ ] Gate added to `qcsim/gates.py` with docstring
- [ ] Circuit method added to `qcsim/circuit.py`
- [ ] TUI key binding added to `qcsim/tui.py`
- [ ] Gate help text added (`?` overlay)
- [ ] Tests added to `tests/test_circuit.py` (minimum 3 tests)
- [ ] Gate is not a duplicate of existing gate matrix
- [ ] All 52 existing tests still pass: `pytest tests/ -v`

## For new circuits (`feat(library): ...`)

- [ ] Built and tested in the TUI (`qcsim-interactive`)
- [ ] Exported and submitted via `add_circuit.py` (no manual index edits)
- [ ] Description, category, difficulty, tags filled in
- [ ] Circuit runs correctly (press R in TUI to verify output)

## For bug fixes / docs

- [ ] Change is minimal and targeted
- [ ] No solution code added to main repo (solutions go in Discussions)
- [ ] Tested locally

---

## Notes for reviewer

<!-- Anything the reviewer should know -->
