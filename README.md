## Minimal Architecture – Common Good Accelerator

Concrete implementation (minimal executable version)

---

# 1️⃣ Minimal instantiation of components

| Element                   | Minimal implementation             | Role                   |
| ------------------------- | ---------------------------------- | ---------------------- |
| **State (S)**             | Persistent `STATE.json`            | System memory          |
| **Anchoring function (f)**| Pure, verifiable external function | Objective measurement  |
| **Operator (π)**          | LLM or deterministic algorithm     | Proposes a correction  |
| **Log**                   | `RUNLOG.md`                        | Traceability           |

---

# 2️⃣ File structure

```
accelerator/
│
├── STATE.json
├── RUNLOG.md
├── anchor.py
├── operator.py
└── main.py
```

---

# 3️⃣ Concrete implementation example (minimal Python)

## 3.1 STATE.json (initial example)

```json
{
  "score": 0.2,
  "iteration": 0
}
```

---

## 3.2 anchor.py

Measurable hard constraint.

```python
def anchor_function(state: dict) -> float:
    """
    f(S) = distance from the Common Good.
    Here, we aim to maximize 'score' toward 1.0.
    Returns the error (1 - score).
    """
    return 1.0 - state["score"]
```

---

## 3.3 operator.py

The intelligence π.

```python
def operator(state: dict, error_signal: float) -> dict:
    """
    π(S, f(S)) → S'
    Simple proportional correction.
    """
    learning_rate = 0.1
    state["score"] += learning_rate * error_signal
    state["iteration"] += 1
    return state
```

---

## 3.4 main.py

Directed recursive loop.

```python
import json
from anchor import anchor_function
from operator import operator

STATE_FILE = "STATE.json"

def load_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def log(state, error):
    with open("RUNLOG.md", "a") as f:
        f.write(f"Iteration {state['iteration']} | Score={state['score']:.4f} | Error={error:.4f}\n")

def step():
    state = load_state()
    error = anchor_function(state)
    new_state = operator(state, error)
    save_state(new_state)
    log(new_state, error)

if __name__ == "__main__":
    for _ in range(50):
        step()
```

---

# 4️⃣ Formal correspondence

Direct implementation of:

[
S_{t+1} = \pi(S_t, f(S_t))
]

* `S_t` → contents of `STATE.json`
* `f(S_t)` → `anchor_function`
* `π` → `operator`
* Persistence → guaranteed by disk
* Logical hierarchy → `operator` cannot modify `anchor_function`

---

# 5️⃣ LLM version (intelligent π)

Replace `operator.py` with:

```python
import openai

def operator(state, error_signal):
    prompt = f"""
    Current state: {state}
    Measured error: {error_signal}
    Propose a minimal modification to reduce the error.
    Reply only in JSON.
    """
    # LLM call
    response = call_llm(prompt)
    return response
```

Critical condition:
The anchor remains external and non-modifiable.

---

# 6️⃣ Implemented security invariant

* `anchor.py` read-only
* External validation possible
* No self-scoring
* Immutable log

---

# 7️⃣ Minimal extension for real Common Good

Examples of possible anchoring functions:

| Domain         | Possible hard anchor              |
| -------------- | --------------------------------- |
| Energy         | kWh saved (real sensor)           |
| Pollution      | measured CO₂ ppm                  |
| Social         | real satisfaction rate            |
| Code           | % of tests passed                 |
| Disinformation | fact-check API score              |

---

# 8️⃣ Ultra-minimal version (pure concept)

3 logical lines are enough:

```python
while True:
    error = f(S)
    S = π(S, error)
```

Everything else is instrumentation.

---

# Summary

A minimal Common Good accelerator requires only:

1. **A persistent state**
2. **A hard external metric**
3. **An operator constrained by this metric**

Without a hard anchor → drift.
Without an operator → inertia.
Without state → no accumulation.

The structure is complete as soon as the loop runs.
