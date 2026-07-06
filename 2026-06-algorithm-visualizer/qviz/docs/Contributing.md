# Contributing to qviz

## Pick something to build

See [Roadmap.md](Roadmap.md) — tasks are grouped Beginner → Expert by
theme. The two most common contributions:
- A new algorithm module → [Algorithm-Development.md](Algorithm-Development.md)
- A rendering/UI feature → [Rendering-Guide.md](Rendering-Guide.md)

## Setup

```bash
git clone https://github.com/LochanPS/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects/2026-06-algorithm-visualizer/qviz
python -m venv .venv
.venv\Scripts\activate                                 # Windows
pip install -e ../../2026-05-circuit-simulator/qcsim   # qcsim first
pip install -e ".[dev]"
pytest tests/ -v
```

## Updating your checkout

If you already cloned the repo earlier, pull the latest and refresh both
editable installs (both use `-e`, so `git pull` picks up source changes,
but re-run the installs if entry points or deps changed):

```bash
cd Quantum-Collective-Monthly-Projects
git pull origin main

cd 2026-06-algorithm-visualizer/qviz
pip install -e ../../2026-05-circuit-simulator/qcsim   # refresh qcsim
pip install -e .                                        # refresh qviz
```

If `qviz-step` isn't found after pulling, the entry point is new in your
checkout — re-run `pip install -e .`.

## Formatting — required, CI enforces it

The repo uses **Black, line length 100**. CI rejects unformatted code.
Before committing:

```bash
black qviz/ tests/ --line-length 100
```

(Historical note: the CI Black check silently rejected fork PRs for a
while because the baseline itself was never formatted. The whole repo is
Black-clean now — keep it that way.)

## Tests — required

Add tests for anything you build. Run the suite:

```bash
pytest tests/ -v          # 54 passing as of this writing
```

**Non-negotiable for bitstring parameters:** include a non-palindromic
case (`"01"`/`"10"`, `"100"`). Symmetric inputs (`"11"`, `"101"`) hide the
label-orientation bug described in
[Developer-Guide.md](Developer-Guide.md#the-grover-bug--read-before-writing-any-algorithm-with-a-bitstring-parameter).

## Commit style

Match the existing history (`git log --oneline -10`): a terse, specific
subject line, and a body that explains **why**, not just what. Example
shape:

```
feat(qviz): add Simon's algorithm module

Simon's finds a hidden period in one query per bit. Returns an
AlgorithmResult with Oracle/Interference phases; oracle uses CNOT
fan-out keyed on the secret string. Non-palindromic secret tested.
```

Scope guardrails

Keep qviz focused on its terminal-first design. Do not add graphical interfaces, browser-based views, or GUI frameworks such as matplotlib. New visualization features should extend the existing terminal renderer while preserving ASCII compatibility.

Keep layers clean. Interpretation logic → interpret.py; formatting → render.py; algorithm meaning → algorithms/. See Architecture.md.

## Submitting

Fork → branch → build → test → format → PR against `main`. Describe what
and why, and note the tests you added.
