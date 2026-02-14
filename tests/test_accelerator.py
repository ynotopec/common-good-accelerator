import json
import tempfile
import unittest
from pathlib import Path

from accelerator.anchor import anchor_function
from accelerator.main import load_external_score, load_state, run, save_state
from accelerator.operator import operator


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
            self.assertGreater(final_state["score"], 0.75)

    def test_load_external_score_clamps_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_path = Path(tmpdir) / "evidence.json"
            evidence_path.write_text(json.dumps({"score": 8.0}), encoding="utf-8")
            self.assertEqual(load_external_score(evidence_path), 1.0)


if __name__ == "__main__":
    unittest.main()
