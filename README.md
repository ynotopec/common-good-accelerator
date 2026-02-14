## Minimal Architecture – Common Good Accelerator

This repository now includes a runnable reference implementation of the minimal accelerator loop described in `project.md`.

## Repository structure

```text
.
├── accelerator/
│   ├── __init__.py
│   ├── STATE.json
│   ├── RUNLOG.md
│   ├── anchor.py
│   ├── operator.py
│   └── main.py
├── tests/
│   └── test_accelerator.py
├── project.md
└── README.md
```

## Quick start

Run the optimizer loop:

```bash
python -m accelerator.main --iterations 20
```

Run tests:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

---

# 1️⃣ Minimal instantiation of components

| Element                   | Minimal implementation             | Role                   |
| ------------------------- | ---------------------------------- | ---------------------- |
| **State (S)**             | Persistent `STATE.json`            | System memory          |
| **Anchoring function (f)**| Pure, verifiable external function | Objective measurement  |
| **Operator (π)**          | Deterministic algorithm            | Proposes a correction  |
| **Log**                   | `RUNLOG.md`                        | Traceability           |

---

# 2️⃣ Concrete implementation summary

* `anchor_function(state)` computes the error as `1.0 - score` (bounded).
* `operator(state, error)` applies a proportional correction and increments iteration.
* `run(iterations)` repeatedly applies the recursive update loop and persists each state.

Formal recurrence:

[
S_{t+1} = \pi(S_t, f(S_t))
]

---

# 3️⃣ Security invariant

* `anchor.py` is logically separate from `operator.py`.
* The operator uses the anchor signal; it does not define the metric.
* Iterations are traceable via append-only run logging.

---

# 4️⃣ Why this is useful

A minimal Common Good accelerator requires only:

1. **A persistent state**
2. **A hard external metric**
3. **An operator constrained by this metric**

Without a hard anchor → drift.
Without an operator → inertia.
Without state → no accumulation.
