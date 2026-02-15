import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from accelerator.anchor import anchor_function
from accelerator.main import load_external_score, load_state, run, save_state, step
from accelerator.operator import operator


class _WebhookHandler(BaseHTTPRequestHandler):
    payloads = []

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size).decode("utf-8")
        _WebhookHandler.payloads.append(json.loads(body))
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return


class AcceleratorTests(unittest.TestCase):
    def test_anchor_bounds_score(self):
        self.assertEqual(anchor_function({"score": 1.5}), 0.0)
        self.assertEqual(anchor_function({"score": -1}), 1.0)

    def test_operator_increments_iteration_and_improves_score(self):
        state = {"score": 0.2, "iteration": 0}
        next_state = operator(state, 0.8)
        self.assertEqual(next_state["iteration"], 1)
        self.assertGreater(next_state["score"], state["score"])

    def test_load_save_and_run_with_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "STATE.json"
            runlog_path = Path(tmpdir) / "RUNLOG.md"
            save_state({"score": 0.0, "iteration": 0}, state_path)

            initial = load_state(state_path)
            self.assertEqual(initial["iteration"], 0)

            final_state = run(5, state_path=state_path, runlog_path=runlog_path)
            self.assertEqual(final_state["iteration"], 5)
            self.assertGreater(final_state["score"], 0.0)
            self.assertTrue(runlog_path.exists())

    def test_repeated_updates_converge(self):
        state = {"score": 0.2, "iteration": 0}
        for _ in range(10):
            state = operator(state, anchor_function(state))
        self.assertGreater(state["score"], 0.6)

    def test_external_score_is_used_when_provided(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "STATE.json"
            runlog_path = Path(tmpdir) / "RUNLOG.md"
            evidence_path = Path(tmpdir) / "evidence.json"

            save_state({"score": 0.0, "iteration": 0}, state_path)
            evidence_path.write_text(json.dumps({"score": 0.75}), encoding="utf-8")

            final_state = run(
                1,
                state_path=state_path,
                runlog_path=runlog_path,
                evidence_path=evidence_path,
            )
            self.assertEqual(final_state["iteration"], 1)
            self.assertAlmostEqual(final_state["observed_score"], 0.75, places=6)
            self.assertAlmostEqual(final_state["score"], 0.75, places=6)
            self.assertGreater(final_state["proposed_score"], 0.75)

    def test_score_does_not_artificially_increase_without_new_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "STATE.json"
            runlog_path = Path(tmpdir) / "RUNLOG.md"
            evidence_path = Path(tmpdir) / "evidence.json"

            save_state({"score": 0.0, "iteration": 0}, state_path)
            evidence_path.write_text(json.dumps({"score": 0.4}), encoding="utf-8")

            final_state = run(
                3,
                state_path=state_path,
                runlog_path=runlog_path,
                evidence_path=evidence_path,
            )
            self.assertEqual(final_state["iteration"], 3)
            self.assertAlmostEqual(final_state["score"], 0.4, places=6)
            self.assertGreater(final_state["proposed_score"], 0.4)

    def test_load_external_score_clamps_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_path = Path(tmpdir) / "evidence.json"
            evidence_path.write_text(json.dumps({"score": 8.0}), encoding="utf-8")
            self.assertEqual(load_external_score(evidence_path), 1.0)

    def test_evidence_command_is_used_as_real_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "STATE.json"
            runlog_path = Path(tmpdir) / "RUNLOG.md"
            save_state({"score": 0.0, "iteration": 0}, state_path)

            evidence_command = f"{sys.executable} -c \"import json; print(json.dumps({{'score': 0.33}}))\""
            state = step(
                state_path=state_path,
                runlog_path=runlog_path,
                evidence_command=evidence_command,
            )
            self.assertAlmostEqual(state["score"], 0.33, places=6)
            self.assertAlmostEqual(state["observed_score"], 0.33, places=6)

    def test_action_command_receives_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "STATE.json"
            runlog_path = Path(tmpdir) / "RUNLOG.md"
            evidence_path = Path(tmpdir) / "evidence.json"
            action_out = Path(tmpdir) / "action.json"

            save_state({"score": 0.0, "iteration": 0}, state_path)
            evidence_path.write_text(json.dumps({"score": 0.6}), encoding="utf-8")

            action_command = (
                f"{sys.executable} -c \"import pathlib,sys; "
                f"pathlib.Path(r'{action_out}').write_text(sys.stdin.read(), encoding='utf-8')\""
            )
            final_state = run(
                1,
                state_path=state_path,
                runlog_path=runlog_path,
                evidence_path=evidence_path,
                action_command=action_command,
            )
            payload = json.loads(action_out.read_text(encoding="utf-8"))
            self.assertEqual(payload["iteration"], 1)
            self.assertAlmostEqual(payload["observed_score"], 0.6, places=6)
            self.assertAlmostEqual(payload["proposed_score"], final_state["proposed_score"], places=6)
            self.assertIn("last_action", final_state)

    def test_action_webhook_and_human_report_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _WebhookHandler.payloads = []
            server = HTTPServer(("127.0.0.1", 0), _WebhookHandler)
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            try:
                state_path = Path(tmpdir) / "STATE.json"
                runlog_path = Path(tmpdir) / "RUNLOG.md"
                evidence_path = Path(tmpdir) / "evidence.json"
                report_path = Path(tmpdir) / "human_report.txt"

                save_state({"score": 0.0, "iteration": 0}, state_path)
                evidence_path.write_text(json.dumps({"score": 0.52}), encoding="utf-8")

                final_state = run(
                    1,
                    state_path=state_path,
                    runlog_path=runlog_path,
                    evidence_path=evidence_path,
                    action_webhook_url=f"http://127.0.0.1:{server.server_port}/hook",
                    human_report_file=report_path,
                )

                self.assertEqual(len(_WebhookHandler.payloads), 1)
                payload = _WebhookHandler.payloads[0]
                self.assertEqual(payload["iteration"], 1)
                self.assertAlmostEqual(payload["observed_score"], 0.52, places=6)
                report = report_path.read_text(encoding="utf-8")
                self.assertIn("Iteration 1", report)
                self.assertIn("human_report", runlog_path.read_text(encoding="utf-8"))
                self.assertIn("last_action", final_state)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
