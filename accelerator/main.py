"""Executable loop for the Common Good Accelerator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .anchor import anchor_function
from .operator import operator

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "STATE.json"
RUNLOG_FILE = BASE_DIR / "RUNLOG.md"


def load_state(path: Path = STATE_FILE) -> dict:
    if not path.exists():
        return {"score": 0.2, "iteration": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict, path: Path = STATE_FILE) -> None:
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_external_score(evidence_path: Path) -> float:
    """Load a reality-anchored score from an external JSON evidence file."""
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    score = float(payload.get("score", 0.0))
    return min(1.0, max(0.0, score))


def log(state: dict, error: float, path: Path = RUNLOG_FILE, observed_score: float | None = None) -> None:
    with path.open("a", encoding="utf-8") as file:
        observed_part = ""
        if observed_score is not None:
            observed_part = f" | Observed={observed_score:.4f}"
        file.write(
            f"Iteration {state['iteration']} | Score={state['score']:.4f}{observed_part} | Error={error:.4f}\n"
        )


def step(
    state_path: Path = STATE_FILE,
    runlog_path: Path = RUNLOG_FILE,
    evidence_path: Path | None = None,
) -> dict:
    state = load_state(state_path)
    observed_score = None
    if evidence_path is not None and evidence_path.exists():
        observed_score = load_external_score(evidence_path)
        state["score"] = observed_score
    error = anchor_function(state)
    new_state = operator(state, error)
    if observed_score is not None:
        new_state["observed_score"] = observed_score
    save_state(new_state, state_path)
    log(new_state, error, runlog_path, observed_score=observed_score)
    return new_state


def run(
    iterations: int,
    state_path: Path = STATE_FILE,
    runlog_path: Path = RUNLOG_FILE,
    evidence_path: Path | None = None,
) -> dict:
    state = load_state(state_path)
    for _ in range(iterations):
        observed_score = None
        if evidence_path is not None and evidence_path.exists():
            observed_score = load_external_score(evidence_path)
            state["score"] = observed_score
        error = anchor_function(state)
        state = operator(state, error)
        if observed_score is not None:
            state["observed_score"] = observed_score
        save_state(state, state_path)
        log(state, error, runlog_path, observed_score=observed_score)
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Common Good Accelerator loop")
    parser.add_argument("--iterations", type=int, default=50, help="Number of update steps")
    parser.add_argument(
        "--evidence-file",
        type=Path,
        default=None,
        help="Optional external JSON file with a 'score' field representing observed reality.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.evidence_file is None:
        print(
            "[simulation mode] No --evidence-file provided. Score updates are internal and do not prove real-world impact."
        )
    final_state = run(args.iterations, evidence_path=args.evidence_file)
    print(json.dumps(final_state, indent=2))
