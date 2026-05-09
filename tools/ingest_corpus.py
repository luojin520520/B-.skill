#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from common import is_noise, load_json, sanitize_author, sanitize_content, tokenize, write_json, write_jsonl


def infer_scene(text: str) -> str:
    if len(text) <= 14:
        return "弹幕短句"
    if any(k in text for k in ("建议", "推荐", "入坑", "二刷")):
        return "安利文案"
    if any(k in text for k in ("离谱", "绷不住", "破防", "逆天")):
        return "吐槽整活"
    if any(k in text for k in ("因为", "所以", "逻辑", "分析")):
        return "理性分析"
    return "评论区互动"


def polarity(text: str) -> str:
    pos = ("好", "赞", "强", "可爱", "喜欢", "神")
    neg = ("差", "烂", "难看", "逆天", "无语")
    p = sum(1 for k in pos if k in text)
    n = sum(1 for k in neg if k in text)
    if p > n:
        return "pos"
    if n > p:
        return "neg"
    return "neu"


def formality(text: str) -> str:
    if any(k in text for k in ("请问", "您好", "感谢", "因此")):
        return "high"
    if any(k in text for k in ("哈哈", "awsl", "yyds", "呜呜")):
        return "low"
    return "mid"


def meme_density(text: str, lexicon: dict) -> str:
    score = 0
    low = text.lower()
    for key, value in lexicon.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        variants = [key] + value.get("variants", [])
        for v in variants:
            if v.lower() in low:
                score += 1
    if score >= 3:
        return "high"
    if score >= 1:
        return "med"
    return "low"


def aggression_risk(text: str) -> str:
    if any(k in text for k in ("孤儿", "滚", "脑残", "傻")):
        return "high"
    if any(k in text for k in ("开喷", "离谱", "无语")):
        return "med"
    return "low"


def normalize_slang(text: str, lexicon: dict) -> tuple[str, list[dict]]:
    normalized = text
    hits: list[dict] = []
    low = text.lower()
    for canonical, meta in lexicon.items():
        if canonical.startswith("_") or not isinstance(meta, dict):
            continue
        variants = [canonical] + meta.get("variants", [])
        matched = [v for v in variants if v.lower() in low]
        if not matched:
            continue
        for m in sorted(matched, key=len, reverse=True):
            normalized = normalized.replace(m, canonical)
        hits.append(
            {
                "canonical": canonical,
                "matched": matched,
                "category": meta.get("category", "unknown"),
                "preferred_scene": meta.get("usage_rules", {}).get("preferred_scene", []),
                "formality_max": meta.get("usage_rules", {}).get("formality_max", "mid"),
            }
        )
    return normalized, hits


def infer_source_type(raw: dict) -> str:
    # Keep this as configurable inference point for future datasets.
    if raw.get("last_ep_index"):
        return "番剧评论"
    return "bilibili_comment"


def interaction_strength(likes: int, text: str) -> str:
    if likes >= 50:
        return "high"
    if likes >= 5:
        return "med"
    if len(text) >= 25:
        return "med"
    return "low"


def ingest_csv(input_path: Path, out_dir: Path, lexicon_path: Path) -> dict:
    lexicon = load_json(lexicon_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = out_dir / "cleaned.jsonl"
    stats_path = out_dir / "stats.json"

    seen: set[str] = set()
    rows: list[dict] = []
    counts = Counter()

    with input_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            content = sanitize_content(raw.get("content", ""))
            if is_noise(content):
                counts["dropped_noise"] += 1
                continue
            h = content
            if h in seen:
                counts["dropped_dup"] += 1
                continue
            seen.add(h)

            ts = raw.get("date") or raw.get("ctime") or ""
            try:
                dt = datetime.fromtimestamp(int(raw.get("ctime", "0"))).isoformat() if raw.get("ctime") else ts
            except ValueError:
                dt = ts

            normalized_content, slang_hits = normalize_slang(content, lexicon)
            slang_vector = {
                "hit_count": len(slang_hits),
                "categories": sorted({h["category"] for h in slang_hits}),
                "canonicals": sorted({h["canonical"] for h in slang_hits}),
            }

            record = {
                "id": f"r{len(rows)+1}",
                "source_type": infer_source_type(raw),
                "source_cursor": raw.get("cursor", ""),
                "author_hash": sanitize_author(raw.get("author", "")),
                "score": raw.get("score", ""),
                "likes": int(raw.get("likes", "0") or 0),
                "timestamp": dt,
                "content": content,
                "normalized_content": normalized_content,
                "tokens": tokenize(content),
                "normalized_tokens": tokenize(normalized_content),
                "scene": infer_scene(normalized_content),
                "polarity": polarity(normalized_content),
                "formality": formality(normalized_content),
                "meme_density": meme_density(normalized_content, lexicon),
                "interaction_strength": interaction_strength(int(raw.get("likes", "0") or 0), normalized_content),
                "aggression_risk": aggression_risk(content),
                "slang_hits": slang_hits,
                "slang_vector": slang_vector,
            }
            rows.append(record)
            counts["kept"] += 1

    write_jsonl(cleaned_path, rows)
    summary = {"input": str(input_path), "output": str(cleaned_path), "counts": counts, "rows": len(rows)}
    write_json(stats_path, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest and clean Bilibili corpus CSV")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("ingest")
    p.add_argument("--input", required=True, help="Path to bilibilib_gongzuoxibao.csv")
    p.add_argument("--out-dir", required=True, help="Output directory for processed artifacts")
    p.add_argument("--lexicon", default="assets/slang_lexicon.json", help="Path to slang lexicon JSON")
    args = parser.parse_args()

    summary = ingest_csv(Path(args.input), Path(args.out_dir), Path(args.lexicon))
    print(f"ingested rows: {summary['rows']}")
    print(f"written: {summary['output']}")


if __name__ == "__main__":
    main()
