#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_json, read_jsonl
from runtime_engine import retrieve

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def _bucket_score(text: str, bucket: str) -> float:
    hits = retrieve(text, 5)
    if not hits:
        return 40.0
    scene_match = 1.0 if any(h["scene"] == bucket for h in hits) else 0.5
    mean_rank = sum(h["score"] for h in hits[:3]) / max(1, len(hits[:3]))
    slang_naturalness = min(1.0, sum(1 for h in hits if "unknown" not in h["cluster"]) / 3.0)
    score = 100 * (0.55 * scene_match + 0.35 * min(1.0, mean_rank) + 0.10 * slang_naturalness)
    return round(score, 2)


def score_text(text: str) -> dict:
    hits = retrieve(text, 5)
    score = 60 + min(30, len(hits) * 4)
    return {"style_score": score, "anchors": hits}


def gate(assets_dir: Path) -> dict:
    profile = load_json(assets_dir / "profile.json")
    evalset = read_jsonl(assets_dir / "evalset.jsonl")
    by_bucket: dict[str, list[float]] = {}
    for row in evalset:
        s = _bucket_score(row["input"], row["bucket"])
        by_bucket.setdefault(row["bucket"], []).append(s)
    bucket_avg = {k: round(sum(v) / len(v), 2) for k, v in by_bucket.items()}
    avg = round(sum(bucket_avg.values()) / len(bucket_avg), 2)
    min_bucket = min(bucket_avg.values()) if bucket_avg else 0.0

    thresholds = profile.get("thresholds", {})
    pass_flag = avg >= thresholds.get("min_style_score_avg", 78.0) and min_bucket >= thresholds.get("min_style_score_bucket", 70.0)
    return {"pass": pass_flag, "avg": avg, "min_bucket": min_bucket, "bucket_avg": bucket_avg}


def main() -> None:
    parser = argparse.ArgumentParser(description="Style evaluation and gate")
    sub = parser.add_subparsers(dest="action", required=True)

    p = sub.add_parser("score")
    p.add_argument("--text", required=True)

    g = sub.add_parser("gate")
    g.add_argument("--assets-dir", default=str(ASSETS))
    args = parser.parse_args()

    if args.action == "score":
        print(json.dumps(score_text(args.text), ensure_ascii=False, indent=2))
        return

    result = gate(Path(args.assets_dir))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
