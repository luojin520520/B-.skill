#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from common import load_json, read_jsonl, write_json


CSV_COLUMNS = [
    "canonical",
    "variants",
    "category_guess",
    "preferred_scene_guess",
    "frequency",
    "review_status",
    "reviewer",
    "confidence",
    "category_override",
    "preferred_scene_override",
    "formality_max_override",
    "notes",
]


def export_csv(candidates_path: Path, out_csv: Path) -> dict:
    rows = read_jsonl(candidates_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for item in rows:
            review = item.get("manual_review", {})
            writer.writerow(
                {
                    "canonical": item.get("canonical", ""),
                    "variants": "|".join(item.get("variants", [])),
                    "category_guess": item.get("category_guess", ""),
                    "preferred_scene_guess": "|".join(item.get("preferred_scene_guess", [])),
                    "frequency": item.get("frequency", 0),
                    "review_status": review.get("review_status", "pending"),
                    "reviewer": review.get("reviewer", ""),
                    "confidence": review.get("confidence", 0.4),
                    "category_override": "",
                    "preferred_scene_override": "",
                    "formality_max_override": "",
                    "notes": review.get("notes", ""),
                }
            )
    return {"rows": len(rows), "csv": str(out_csv)}


def _parse_list(value: str) -> list[str]:
    return [v.strip() for v in value.split("|") if v.strip()]


def import_review(review_csv: Path, base_lexicon_path: Path, out_lexicon_path: Path) -> dict:
    lexicon = load_json(base_lexicon_path)
    now = datetime.now(timezone.utc).isoformat()
    applied = 0

    with review_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            canonical = row.get("canonical", "").strip()
            if not canonical:
                continue
            status = row.get("review_status", "pending").strip() or "pending"
            if status == "rejected":
                continue
            category = row.get("category_override", "").strip() or row.get("category_guess", "").strip() or "玩梗词"
            preferred_scene = _parse_list(row.get("preferred_scene_override", "")) or _parse_list(
                row.get("preferred_scene_guess", "")
            )
            formality_max = row.get("formality_max_override", "").strip() or "mid"
            variants = _parse_list(row.get("variants", ""))
            reviewer = row.get("reviewer", "").strip()
            confidence = float(row.get("confidence", "0.5") or 0.5)
            notes = row.get("notes", "").strip()
            frequency = int(float(row.get("frequency", "0") or 0))

            lexicon[canonical] = {
                "variants": sorted(set(variants or [canonical])),
                "category": category,
                "usage_rules": {
                    "preferred_scene": preferred_scene or ["评论区互动"],
                    "formality_max": formality_max,
                },
                "review": {
                    "review_status": status,
                    "reviewer": reviewer,
                    "reviewed_at": now if status in {"approved", "tuned"} else "",
                    "confidence": confidence,
                    "notes": notes,
                },
                "evidence": {
                    "frequency": frequency,
                    "source": "manual_review_csv",
                    "examples": [],
                },
            }
            applied += 1

    meta = lexicon.get("_meta", {})
    meta["last_review_import_at"] = now
    meta["last_review_applied"] = applied
    lexicon["_meta"] = meta
    write_json(out_lexicon_path, lexicon)
    return {"applied": applied, "out": str(out_lexicon_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Review workbench for slang lexicon")
    sub = parser.add_subparsers(dest="action", required=True)

    ex = sub.add_parser("export-csv")
    ex.add_argument("--candidates", default="assets/slang_candidates_v1.jsonl")
    ex.add_argument("--out-csv", default="assets/slang_review_sheet_v1.csv")

    im = sub.add_parser("import-csv")
    im.add_argument("--review-csv", default="assets/slang_review_sheet_v1.csv")
    im.add_argument("--base-lexicon", default="assets/slang_lexicon.json")
    im.add_argument("--out-lexicon", default="assets/slang_lexicon.v1.reviewed.json")

    args = parser.parse_args()
    if args.action == "export-csv":
        result = export_csv(Path(args.candidates), Path(args.out_csv))
    else:
        result = import_review(Path(args.review_csv), Path(args.base_lexicon), Path(args.out_lexicon))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
