from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import sys

TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from ingest_corpus import ingest_csv
from build_profile import build
from common import load_json, read_jsonl


class PipelineTest(unittest.TestCase):
    def test_ingest_and_build_profile(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            csv_path = root / "in.csv"
            lexicon_path = root / "lexicon.json"
            out_dir = root / "processed"
            assets_dir = root / "assets"

            lexicon_path.write_text(
                '{"_meta":{"version":"v1"},"awsl":{"variants":["AWSL"],"usage_rules":{"preferred_scene":["弹幕短句"]}}}',
                encoding="utf-8",
            )
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["author", "score", "likes", "ctime", "content", "date", "cursor"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "author": "u1",
                        "score": "10",
                        "likes": "5",
                        "ctime": "1710000000",
                        "content": "这波真的AWSL",
                        "date": "2024-01-01 00:00:00",
                        "cursor": "1",
                    }
                )
                writer.writerow(
                    {
                        "author": "u2",
                        "score": "10",
                        "likes": "0",
                        "ctime": "1710000010",
                        "content": "。",
                        "date": "2024-01-01 00:00:10",
                        "cursor": "2",
                    }
                )

            summary = ingest_csv(csv_path, out_dir, lexicon_path)
            self.assertEqual(summary["rows"], 1)
            cleaned = read_jsonl(out_dir / "cleaned.jsonl")
            self.assertEqual(cleaned[0]["meme_density"], "med")
            self.assertIn("normalized_content", cleaned[0])
            self.assertIn("slang_vector", cleaned[0])
            self.assertGreaterEqual(cleaned[0]["slang_vector"]["hit_count"], 1)

            profile = build(out_dir / "cleaned.jsonl", assets_dir, per_cluster=3)
            self.assertEqual(profile["rows"], 1)
            anchors = read_jsonl(assets_dir / "anchors.jsonl")
            self.assertGreaterEqual(len(anchors), 1)
            p = load_json(assets_dir / "profile.json")
            self.assertIn("distribution", p)


if __name__ == "__main__":
    unittest.main()
