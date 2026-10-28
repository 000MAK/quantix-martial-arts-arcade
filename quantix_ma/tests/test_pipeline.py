import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quantix_ma.data_loader import load_sequences  # noqa: E402
from quantix_ma.markov_model import MarkovTransitionModel  # noqa: E402
from quantix_ma.pipeline import run_pipeline  # noqa: E402
from quantix_ma.schema import BoutSequence  # noqa: E402


def bout(states, durations=None):
    return BoutSequence("a1", "b1", "bjj_no_gi", list(states), durations)


class MarkovModelTests(unittest.TestCase):
    def test_rows_sum_to_one_without_self_loops(self):
        model = MarkovTransitionModel()
        model.fit([bout(["guard", "half_guard", "side_control", "mount"])])
        for state, row in model.transition_matrix.items():
            self.assertEqual(row[state], 0.0)
            self.assertAlmostEqual(sum(row.values()), 1.0)

    def test_repeats_collapse_into_one_episode(self):
        model = MarkovTransitionModel(pseudocount=0.0)
        model.fit([bout(["guard", "guard", "mount"], [10, 5, 4])])
        self.assertEqual(model.transition_counts["guard"]["guard"], 0.0)
        self.assertEqual(model.transition_matrix["guard"]["mount"], 1.0)
        self.assertEqual(model.dwell_unit, "seconds")
        self.assertEqual(model.dwell_times["guard"], {"visits": 1, "mean": 15.0, "max": 15.0})

    def test_dwell_falls_back_to_steps_without_durations(self):
        model = MarkovTransitionModel()
        model.fit([bout(["guard", "guard", "guard", "mount"])])
        self.assertEqual(model.dwell_unit, "steps")
        self.assertEqual(model.dwell_times["guard"]["mean"], 3.0)

    def test_save_load_roundtrip(self):
        model = MarkovTransitionModel()
        model.fit([bout(["guard", "mount"], [3, 4])])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model.json"
            model.save(path)
            loaded = MarkovTransitionModel.load(path)
        self.assertEqual(loaded.transition_matrix, model.transition_matrix)
        self.assertEqual(loaded.dwell_times, model.dwell_times)


class LoaderAndPipelineTests(unittest.TestCase):
    def test_synthetic_fallback_is_not_written_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            sequences = load_sequences(tmp)
            self.assertTrue(all(seq.source == "synthetic" for seq in sequences))
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_strict_mode_requires_real_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                load_sequences(tmp, allow_synthetic=False)

    def test_csv_with_durations(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "bjj_sequences.csv").write_text(
                "athlete_id,bout_id,states,durations\n"
                "a1,b1,guard|half_guard|mount,12|8|20\n",
                encoding="utf-8",
            )
            [seq] = load_sequences(tmp)
        self.assertEqual(seq.durations, [12.0, 8.0, 20.0])
        self.assertEqual(seq.source, "labeled")

    def test_mismatched_durations_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "bjj_sequences.json").write_text(
                json.dumps([{"states": ["guard", "mount"], "durations": [1]}]), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                load_sequences(tmp)

    def test_pipeline_marks_synthetic_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = run_pipeline(tmp)
            report = Path(summary["report_path"]).read_text(encoding="utf-8")
        self.assertEqual(summary["data_source"], "synthetic")
        self.assertEqual(summary["dwell_unit"], "seconds")
        self.assertIn("Synthetic data", report)


if __name__ == "__main__":
    unittest.main()
