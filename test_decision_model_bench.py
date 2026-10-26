# PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
# written-by: unknown (pre-provenance) | 2026-10-15 | b698260
# modified-by: codex/gpt-5.6-sol | 2026-10-26 | pending | provenance block added
# END PROVENANCE
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import decision_model_bench as bench


class BenchTests(unittest.TestCase):
    def test_load_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text('{"id":"one","prompt":"safe","expected":"allow"}\n', encoding="utf-8")
            self.assertEqual(bench.load_cases(path)[0].case_id, "one")

    def test_load_cases_rejects_bad_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text('{"id":"one"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1"):
                bench.load_cases(path)

    def test_normalize_short_verdict(self):
        self.assertEqual(bench.normalize(" Allow.\nExplanation"), "allow")

    @patch("decision_model_bench.completion")
    def test_run_scores_and_reports_metrics(self, fake_completion):
        fake_completion.side_effect = ["allow.", "deny"]
        cases = [bench.Case("a", "safe example", "allow"), bench.Case("b", "unsafe example", "deny")]
        report = bench.run(cases, "synthetic-endpoint", "synthetic-model", 2)
        self.assertEqual(report["accuracy"], 1.0)
        self.assertEqual(report["cases"], 2)
        self.assertGreaterEqual(report["latency_ms"]["p95"], 0)
        self.assertGreater(report["runner_peak_rss_mib"], 0)


if __name__ == "__main__":
    unittest.main()
