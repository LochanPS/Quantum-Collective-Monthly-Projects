# Security Policy

## Reporting a Vulnerability

**Do not open a public GitHub Issue for security vulnerabilities.**

Email: **pokkalilochan@gmail.com**  
Subject: `[SECURITY] Quantum Collective — <brief description>`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

**Response time:** Within 72 hours.

## Scope

This repo contains:
- A quantum circuit simulator (pure Python/NumPy — classical computation only)
- A community circuit library (JSON files)
- GitHub Actions workflows

Likely security concerns:
- **Workflow injection** — malicious PR manipulating CI commands via input data
- **Dependency vulnerabilities** — NumPy, setuptools, pytest
- **Path traversal** — in circuit-library file handling scripts

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch | ✅ |
| Forks | ❌ (contact fork maintainer) |
