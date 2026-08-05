# Contributing

## Participating in a Challenge

### 1. Fork the repo

Click **Fork** on GitHub. Build your solution in your own fork — you own it completely.

### 2. Work in your fork

```bash
git clone https://github.com/<your-username>/Quantum-Collective-Monthly-Projects.git
cd Quantum-Collective-Monthly-Projects
```

Build your solution anywhere in your fork. Suggested layout:

```
my-solution/
    src/
    tests/
    README.md    ← explain your approach, decisions, what you'd do next
```

### 3. Submit via Discussions

Go to [Discussions → Submissions](../../discussions/categories/submissions) and open a new post:

**Title:** `[June 2026] Beginner — <your username>`

**Body:**
- Link to your fork (or specific folder/branch)
- Your tier: Beginner / Intermediate / Advanced
- 2–3 sentences on your approach
- Anything you want feedback on

### 4. Get feedback

Maintainers and community members will comment on your Discussion post. No merge conflicts, no waiting in a PR queue.

---

## Contributing to Challenge Files

Found a bug in the problem statement, starter code, or tests? Open an Issue or PR directly to this repo.

PRs to this repo should only modify challenge files — not add solution code.

### PR process

```bash
git checkout -b fix/may-starter-code-typo
# make your change
git commit -m "fix: correct CNOT matrix in starter-code"
git push origin fix/may-starter-code-typo
# open PR on GitHub
```

### Code style (for starter-code files)

- Python: PEP 8, enforced by `black`
- Type hints on all public functions
- Docstrings on all public functions/classes
- Run `black .` before committing

---

## Questions?

Open a [Discussion in Q&A](../../discussions/categories/q-a) — not an Issue.
Issues are for bugs only.
