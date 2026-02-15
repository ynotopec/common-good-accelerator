# Minimal Architecture – Common Good Accelerator
(Reference Specification)

## 1. Fundamental Principle
Optimization does not arise from software architecture, but from the **resistance of reality**.
For there to be direction (improvement), there must be constraint (anchoring).

## 2. Irreducible Triad

1.  **State ($S$)**
    The current representation of the system.

2.  **Anchoring Function ($f$)**
    Measures the divergence between state $S$ and the Common Good.
    *Critical condition:* $f$ must be a **hard constraint** (data, oracle, rules), not a self-evaluation.

3.  **Update Operator ($\pi$)**
    The intelligence that transforms the error signal into a correction.

## 3. Formalization

The system is a directed recursive function:

[
S_{t+1} = \pi\big(S_t, f(S_t)\big)
]

**Details of the signal $f(S_t)$:**
It provides the **direction** of correction.
*   *Continuous case:* Mathematical gradient (magnitude + vector).
*   *Discrete case:* Binary signal, error report, or scalar score.

## 4. Security Invariant

Physical separation is optional.
Logical hierarchy is absolute:

> **The anchoring function $f$ constrains the operator $\pi$.**
> (Intelligence serves the metric; it does not define it.)

---

## Conclusion

The minimal system is:
**A persistent state ($S$) steered by an intelligence ($\pi$) constrained by measurable reality ($f$).**


## 5. Status Project File (Current Execution Design)

### (A) Router / Decision Flow

```text
START
  |
  v
Load STATE.json
  |
  v
Evidence source available?
  |-- yes: --evidence-command -> execute command -> parse {"score": ...}
  |-- yes: --evidence-file    -> read JSON file -> parse {"score": ...}
  |-- no: simulation score from state
  |
  v
Compute error = f(state) = 1 - bounded(score)
  |
  v
Compute proposal with operator pi(state, error)
  |
  v
If observed evidence exists:
  - keep reported score anchored to observed_score
  - keep operator suggestion in proposed_score
  |
  v
Dispatch outputs (0..N channels):
  - action-command (stdin JSON)
  - action-webhook-url (HTTP POST JSON)
  - human-report-file (append readable line)
  |
  v
Persist STATE.json + append RUNLOG.md
  |
  v
END ITERATION
```

### (B) Single Sequence for a Critical Test Case

**Critical case:** observed reality + webhook + human report in the same iteration.

1. Initialize state at `{"score": 0.0, "iteration": 0}`.
2. Provide evidence input `{"score": 0.52}`.
3. Run one iteration with:
   - `--evidence-file <path>`
   - `--action-webhook-url <local test server>`
   - `--human-report-file <report path>`
4. System computes error from observed score and generates a proposal.
5. System keeps final persisted `score == 0.52` and stores `proposed_score` separately.
6. System POSTs payload to webhook with `iteration`, `observed_score`, `proposed_score`, `error`.
7. System appends one human-readable line in report file.
8. System appends one runlog line including `Action=...` metadata.
9. Assertions for pass:
   - exactly one webhook payload received,
   - report file contains `Iteration 1`,
   - final state contains `last_action`.
