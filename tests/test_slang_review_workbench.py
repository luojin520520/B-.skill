from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from common import write_jsonl
from review_slang_lexicon import export_csv, import_review


class SlangReviewWorkbenchTest(unittest.TestCase):
    def test_export_and_import_review_csv(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidates = root / "candidates.jsonl"
            csv_path = root / "review.csv"
            base = root / "base.json"
            out = root / "reviewed.json"

            write_jsonl(
                candidates,
                [
                    {
                        "canonical": "awsl",
                        "variants": ["awsl", "AWSL"],
                        "category_guess": "玩梗词",
                        "preferred_scene_guess": ["弹幕短句"],
                        "frequency": 100,
                        "manual_review": {"review_status": "pending", "confidence": 0.4, "notes": "auto"},
                    }
                ],
            )
            base.write_text(json.dumps({"_meta": {"version": "v1"}}, ensure_ascii=False), encoding="utf-8")

            exported = export_csv(candidates, csv_path)
            self.assertEqual(exported["rows"], 1)

            rows = []
            with csv_path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["review_status"] = "approved"
                    row["reviewer"] = "tester"
                    row["category_override"] = "情绪词"
                    row["preferred_scene_override"] = "评论区互动|吐槽整活"
                    row["formality_max_override"] = "low"
                    row["notes"] = "looks good"
                    rows.append(row)
            with csv_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            imported = import_review(csv_path, base, out)
            self.assertEqual(imported["applied"], 1)
            reviewed = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("awsl", reviewed)
            self.assertEqual(reviewed["awsl"]["category"], "情绪词")


if __name__ == "__main__":
    unittest.main()
