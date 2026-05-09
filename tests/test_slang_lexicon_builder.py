from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from common import write_jsonl
from build_slang_lexicon import build


class SlangLexiconBuilderTest(unittest.TestCase):
    def test_build_candidates_and_merged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cleaned = root / "cleaned.jsonl"
            lexicon = root / "lexicon.json"
            candidates_out = root / "candidates.jsonl"
            merged_out = root / "merged.json"

            rows = [
                {"content": "这波awsl yyds 太强了"},
                {"content": "awsl 真的awsl"},
                {"content": "爷青回 这也太好康了"},
                {"content": "awsl"},
                {"content": "yyds yyds"},
                {"content": "爷青回"},
                {"content": "awsl"},
                {"content": "awsl"},
                {"content": "awsl"},
            ]
            write_jsonl(cleaned, rows)
            lexicon.write_text(
                json.dumps(
                    {
                        "_meta": {"version": "v1"},
                        "awsl": {
                            "variants": ["awsl"],
                            "category": "情绪词",
                            "usage_rules": {"preferred_scene": ["弹幕短句"], "formality_max": "mid"},
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            summary = build(cleaned, lexicon, candidates_out, merged_out, min_freq=2)
            self.assertGreater(summary["stats"]["candidates"], 0)
            merged = json.loads(merged_out.read_text(encoding="utf-8"))
            self.assertIn("_meta", merged)
            self.assertIn("awsl", merged)


if __name__ == "__main__":
    unittest.main()
