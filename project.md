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
