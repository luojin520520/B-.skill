#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from common import read_jsonl, write_json, write_jsonl


def pick_cluster(record: dict) -> str:
    text = record.get("normalized_content", record["content"])
    if record["scene"] == "安利文案":
        return "真诚安利"
    if record["scene"] == "吐槽整活":
        return "整活吐槽"
    if record["scene"] == "理性分析":
        return "理性分析"
    if any(k in text for k in ("可爱", "喜欢", "治愈", "感动")):
        return "情绪共鸣"
    if any(k in text for k in ("高能", "起飞", "拉满")):
        return "高能反应"
    if any(k in text for k in ("破防", "绷不住", "逆天", "离谱")):
        return "整活吐槽"
    return "二创互动"


def to_weight(likes: int) -> float:
    if likes >= 1000:
        return 1.5
    if likes >= 100:
        return 1.2
    if likes >= 20:
        return 1.1
    return 1.0


def build(cleaned_path: Path, assets_dir: Path, per_cluster: int = 40) -> dict:
    rows = read_jsonl(cleaned_path)
    if not rows:
        raise ValueError(f"no rows found in {cleaned_path}")

    assets_dir.mkdir(parents=True, exist_ok=True)

    clusters: dict[str, list[dict]] = defaultdict(list)
    scene_dist = Counter()
    meme_dist = Counter()
    formality_dist = Counter()
    polarity_dist = Counter()

    for r in rows:
        c = pick_cluster(r)
        w = to_weight(int(r.get("likes", 0)))
        item = {
            "id": r["id"],
            "text": r.get("normalized_content", r["content"]),
            "raw_text": r["content"],
            "scene": r["scene"],
            "polarity": r["polarity"],
            "formality": r["formality"],
            "meme_density": r["meme_density"],
            "interaction_strength": r["interaction_strength"],
            "aggression_risk": r["aggression_risk"],
            "slang_vector": r.get("slang_vector", {}),
            "cluster": c,
            "weight": w,
            "source_id": r["id"],
        }
        clusters[c].append(item)
        scene_dist[r["scene"]] += 1
        meme_dist[r["meme_density"]] += 1
        formality_dist[r["formality"]] += 1
        polarity_dist[r["polarity"]] += 1

    anchors: list[dict] = []
    for cluster_name, items in clusters.items():
        items = sorted(items, key=lambda x: (x["weight"], len(x["text"])), reverse=True)
        anchors.extend(items[:per_cluster])

    write_jsonl(assets_dir / "anchors.jsonl", anchors)
    profile = {
        "profile_version": "v1",
        "rows": len(rows),
        "anchors": len(anchors),
        "distribution": {
            "scene": scene_dist,
            "meme_density": meme_dist,
            "formality": formality_dist,
            "polarity": polarity_dist,
        },
        "clusters": {k: len(v) for k, v in clusters.items()},
    }
    write_json(assets_dir / "profile.json", profile)
    return profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Build profile and anchor corpus from cleaned data")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("build")
    p.add_argument("--input", required=True, help="Path to cleaned.jsonl")
    p.add_argument("--assets-dir", required=True, help="Assets dir to write profile and anchors")
    p.add_argument("--per-cluster", type=int, default=40)
    args = parser.parse_args()

    profile = build(Path(args.input), Path(args.assets_dir), args.per_cluster)
    print(f"profile rows={profile['rows']} anchors={profile['anchors']}")


if __name__ == "__main__":
    main()
