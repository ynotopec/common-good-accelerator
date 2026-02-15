"""Executable loop for the Common Good Accelerator."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import urllib.request
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


def load_external_score_from_command(evidence_command: str) -> float:
    """Load a reality-anchored score by executing an external command that outputs JSON."""
    result = subprocess.run(
        shlex.split(evidence_command),
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    score = float(payload.get("score", 0.0))
    return min(1.0, max(0.0, score))


def run_action(action_command: str, action_payload: dict) -> int:
    """Execute a real-world action command with JSON payload provided on stdin."""
    completed = subprocess.run(
        shlex.split(action_command),
        input=json.dumps(action_payload),
        text=True,
        check=True,
    )
    return completed.returncode


def send_webhook(action_webhook_url: str, action_payload: dict) -> int:
    """Send action payload to an HTTP endpoint to trigger external systems."""
    request = urllib.request.Request(
        action_webhook_url,
        data=json.dumps(action_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return int(response.status)


def write_human_report(human_report_file: Path, action_payload: dict) -> None:
    """Append a human-readable intervention report for operators."""
    human_report_file.parent.mkdir(parents=True, exist_ok=True)
    line = (
        f"Iteration {action_payload['iteration']} | observed={action_payload.get('observed_score')} "
        f"| proposed={action_payload.get('proposed_score')} | error={action_payload.get('error')}\n"
    )
    with human_report_file.open("a", encoding="utf-8") as report:
        report.write(line)


def log(
    state: dict,
    error: float,
    path: Path = RUNLOG_FILE,
    observed_score: float | None = None,
    proposed_score: float | None = None,
    action_status: str | None = None,
) -> None:
    with path.open("a", encoding="utf-8") as file:
        observed_part = ""
        if observed_score is not None:
            observed_part = f" | Observed={observed_score:.4f}"
        proposed_part = ""
        if proposed_score is not None:
            proposed_part = f" | Proposed={proposed_score:.4f}"
        action_part = ""
        if action_status is not None:
            action_part = f" | Action={action_status}"
        file.write(
            (
                f"Iteration {state['iteration']} | Score={state['score']:.4f}{observed_part}"
                f"{proposed_part}{action_part} | Error={error:.4f}\n"
            )
        )


def resolve_observed_score(evidence_path: Path | None = None, evidence_command: str | None = None) -> float | None:
    if evidence_command:
        return load_external_score_from_command(evidence_command)
    if evidence_path is not None and evidence_path.exists():
        return load_external_score(evidence_path)
    return None


def apply_action_outputs(
    action_payload: dict,
    action_command: str | None = None,
    action_webhook_url: str | None = None,
    human_report_file: Path | None = None,
) -> str | None:
    action_channels: list[str] = []
    if action_command:
        run_action(action_command, action_payload)
        action_channels.append("command")
    if action_webhook_url:
        send_webhook(action_webhook_url, action_payload)
        action_channels.append("webhook")
    if human_report_file is not None:
        write_human_report(human_report_file, action_payload)
        action_channels.append("human_report")
    if not action_channels:
        return None
    return ",".join(action_channels)


def step(
    state_path: Path = STATE_FILE,
    runlog_path: Path = RUNLOG_FILE,
    evidence_path: Path | None = None,
    evidence_command: str | None = None,
    action_command: str | None = None,
    action_webhook_url: str | None = None,
    human_report_file: Path | None = None,
) -> dict:
    state = load_state(state_path)
    observed_score = resolve_observed_score(evidence_path=evidence_path, evidence_command=evidence_command)
    if observed_score is not None:
        state["score"] = observed_score

    error = anchor_function(state)
    new_state = operator(state, error)

    proposed_score = None
    if observed_score is not None:
        proposed_score = new_state["score"]
        new_state["score"] = observed_score
        new_state["observed_score"] = observed_score
        new_state["proposed_score"] = proposed_score

    action_payload = {
        "iteration": new_state["iteration"],
        "observed_score": observed_score,
        "proposed_score": proposed_score,
        "error": error,
    }
    action_status = apply_action_outputs(
        action_payload,
        action_command=action_command,
        action_webhook_url=action_webhook_url,
        human_report_file=human_report_file,
    )
    if action_status is not None:
        new_state["last_action"] = action_payload

    save_state(new_state, state_path)
    log(
        new_state,
        error,
        runlog_path,
        observed_score=observed_score,
        proposed_score=proposed_score,
        action_status=action_status,
    )
    return new_state


def run(
    iterations: int,
    state_path: Path = STATE_FILE,
    runlog_path: Path = RUNLOG_FILE,
    evidence_path: Path | None = None,
    evidence_command: str | None = None,
    action_command: str | None = None,
    action_webhook_url: str | None = None,
    human_report_file: Path | None = None,
) -> dict:
    state = load_state(state_path)
    for _ in range(iterations):
        state = step(
            state_path=state_path,
            runlog_path=runlog_path,
            evidence_path=evidence_path,
            evidence_command=evidence_command,
            action_command=action_command,
            action_webhook_url=action_webhook_url,
            human_report_file=human_report_file,
        )
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
    parser.add_argument(
        "--evidence-command",
        type=str,
        default=None,
        help="Optional command that outputs JSON with a 'score' field.",
    )
    parser.add_argument(
        "--action-command",
        type=str,
        default=None,
        help="Optional command executed each iteration with action JSON sent on stdin.",
    )
    parser.add_argument(
        "--action-webhook-url",
        type=str,
        default=None,
        help="Optional webhook URL to receive action JSON each iteration.",
    )
    parser.add_argument(
        "--human-report-file",
        type=Path,
        default=None,
        help="Optional file where human-readable action lines are appended each iteration.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.evidence_file is None and args.evidence_command is None:
        print(
            "[simulation mode] No external evidence source provided. Score updates are internal and do not prove real-world impact."
        )
    final_state = run(
        args.iterations,
        evidence_path=args.evidence_file,
        evidence_command=args.evidence_command,
        action_command=args.action_command,
        action_webhook_url=args.action_webhook_url,
        human_report_file=args.human_report_file,
    )
    print(json.dumps(final_state, indent=2))
