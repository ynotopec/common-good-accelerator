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


def log(state: dict, error: float, path: Path = RUNLOG_FILE) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(
            f"Iteration {state['iteration']} | Score={state['score']:.4f} | Error={error:.4f}\n"
        )


def step(state_path: Path = STATE_FILE, runlog_path: Path = RUNLOG_FILE) -> dict:
    state = load_state(state_path)
    error = anchor_function(state)
    new_state = operator(state, error)
    save_state(new_state, state_path)
    log(new_state, error, runlog_path)
    return new_state


def run(iterations: int, state_path: Path = STATE_FILE, runlog_path: Path = RUNLOG_FILE) -> dict:
    state = load_state(state_path)
    for _ in range(iterations):
        error = anchor_function(state)
        state = operator(state, error)
        save_state(state, state_path)
        log(state, error, runlog_path)
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Common Good Accelerator loop")
    parser.add_argument("--iterations", type=int, default=50, help="Number of update steps")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    final_state = run(args.iterations)
    print(json.dumps(final_state, indent=2))
