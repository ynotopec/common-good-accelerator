"""Anchor function for the Common Good Accelerator."""


def anchor_function(state: dict) -> float:
    """Return error signal as distance from ideal score of 1.0."""
    score = float(state.get("score", 0.0))
    bounded_score = min(1.0, max(0.0, score))
    return 1.0 - bounded_score
