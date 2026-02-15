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

Run the optimizer loop (simulation mode):

```bash
python -m accelerator.main --iterations 20
```

Run with an external evidence file (reality anchor):

```bash
python -m accelerator.main --iterations 20 --evidence-file ./evidence.json
```

Or pull real input from a command (must print JSON with `score`):

```bash
python -m accelerator.main --iterations 20 --evidence-command "python -c 'import json; print(json.dumps({\"score\": 0.42}))'"
```

Optionally trigger real outputs each iteration:

```bash
python -m accelerator.main --iterations 20 --evidence-file ./evidence.json --action-command "python ./do_action.py"
```

```bash
python -m accelerator.main --iterations 20 --evidence-file ./evidence.json --action-webhook-url "https://example.org/hook"
```

```bash
python -m accelerator.main --iterations 20 --evidence-file ./evidence.json --human-report-file ./reports/human.txt
```

Where `evidence.json` contains at least:

```json
{"score": 0.42}
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
* If `--evidence-file` or `--evidence-command` is provided, each iteration reads an observed external score, keeps `score` anchored to that observation, and logs both `Observed=...` and `Proposed=...` (the operator suggestion).
* If `--action-command` is provided, the loop executes that command each iteration and sends a JSON action payload on stdin (`iteration`, `observed_score`, `proposed_score`, `error`).
* If `--action-webhook-url` is provided, the same payload is POSTed as JSON to an HTTP endpoint (internet output).
* If `--human-report-file` is provided, each iteration appends a human-readable line for operators (human output channel).

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

In this repository, running without `--evidence-file` is an explicit simulation mode.
Use `--evidence-file` to connect the loop to observed reality signals.

Without a hard anchor → drift.
Without an operator → inertia.
Without state → no accumulation.
