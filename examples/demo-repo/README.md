# Demo Repository

This is a minimal, deterministic Python repository designed for testing Secure Code Reasoner.

## Contents

- `app.py`: Main application with basic functions
- `utils.py`: Utility functions for data processing
- `requirements.txt`: Dependency list (empty for this demo)

## Analyzing with Secure Code Reasoner

To analyze this repository:

```bash
scr analyze examples/demo-repo --format text
```

For JSON output:

```bash
scr analyze examples/demo-repo --format json
```

## Safety Guarantees

This repository contains:
- No network access
- No file write operations
- No subprocess execution
- Deterministic, pure functions only

It is safe to analyze and serves as a reference implementation for Secure Code Reasoner testing.
