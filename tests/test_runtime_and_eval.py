from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import json
import sys

TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import runtime_engine
from eval_style import gate


class RuntimeEvalTest(unittest.TestCase):
    def test_retrieve_and_version(self) -> None:
        hits = runtime_engine.retrieve("这波真的好康", 5)
        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("aggression_risk", hits[0])
        info = runtime_engine._version_info()
        self.assertIn("anchors_count", info)

    def test_gate_with_temp_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            assets = Path(td)
            (assets / "profile.json").write_text(
                json.dumps(
                    {
                        "thresholds": {
                            "min_style_score_avg": 10,
                            "min_style_score_bucket": 10,
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (assets / "evalset.jsonl").write_text(
                '{"bucket":"弹幕短句","input":"好康"}\n',
                encoding="utf-8",
            )
            result = gate(assets)
            self.assertTrue(result["pass"])

    def test_correction_writeback_updates_anchors(self) -> None:
        before = len(runtime_engine._load_anchors())
        runtime_engine._append_correction("太现代了", "这句不B站", "这波表达得更站味一点")
        after = len(runtime_engine._load_anchors())
        self.assertGreaterEqual(after, before + 1)


if __name__ == "__main__":
    unittest.main()
