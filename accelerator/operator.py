"""State update operator for the Common Good Accelerator."""


def operator(state: dict, error_signal: float, learning_rate: float = 0.1) -> dict:
    """Apply proportional correction to the score and increment iteration."""
    next_state = dict(state)
    next_state["score"] = min(1.0, max(0.0, float(next_state.get("score", 0.0)) + learning_rate * error_signal))
    next_state["iteration"] = int(next_state.get("iteration", 0)) + 1
    return next_state
