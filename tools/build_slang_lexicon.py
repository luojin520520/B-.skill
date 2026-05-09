#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from common import load_json, read_jsonl, write_json, write_jsonl

LATIN_RE = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_]{1,15}\b")
CJK_RE = re.compile(r"[\u4e00-\u9fff]{2,6}")

STOP_CJK = {
    "真的",
    "这个",
    "那个",
    "我们",
    "你们",
    "他们",
    "就是",
    "感觉",
    "一个",
    "好看",
    "不错",
    "哈哈",
    "可以",
    "没有",
    "但是",
}


def _extract_candidates(rows: list[dict], min_freq: int) -> tuple[list[dict], dict]:
    latin_counter: Counter[str] = Counter()
    cjk_counter: Counter[str] = Counter()
    examples: defaultdict[str, list[str]] = defaultdict(list)

    for row in rows:
        text = row.get("content", "")
        low = text.lower()
        for token in LATIN_RE.findall(low):
            if len(token) <= 1:
                continue
            latin_counter[token] += 1
            if len(examples[token]) < 3:
                examples[token].append(text)
        for token in CJK_RE.findall(text):
            if token in STOP_CJK:
                continue
            # keep likely slang-ish tokens (contains emotion markers or uncommon forms)
            if len(token) >= 2 and (
                any(ch in token for ch in ("梗", "草", "破防", "离谱", "逆天", "好康", "高能", "整活", "绷"))
                or token.endswith(("党", "怪", "帝", "人", "王", "侠"))
                or token in {"爷青回", "下饭", "好康", "整活", "爆杀", "绷不住", "寄了", "起飞", "上头", "逆天"}
            ):
                cjk_counter[token] += 1
                if len(examples[token]) < 3:
                    examples[token].append(text)

    candidates: list[dict] = []
    for token, freq in latin_counter.items():
        if freq < min_freq:
            continue
        candidates.append(
            {
                "canonical": token.lower(),
                "variants": sorted({token, token.upper(), token.lower()}),
                "candidate_source": "auto_latin",
                "frequency": freq,
                "category_guess": "玩梗词",
                "preferred_scene_guess": ["弹幕短句", "评论区互动"],
                "manual_review": {
                    "review_status": "pending",
                    "reviewer": "",
                    "reviewed_at": "",
                    "confidence": 0.4,
                    "notes": "auto extracted from latin token frequency",
                },
                "examples": examples[token][:3],
            }
        )
    for token, freq in cjk_counter.items():
        if freq < min_freq:
            continue
        candidates.append(
            {
                "canonical": token,
                "variants": [token],
                "candidate_source": "auto_cjk",
                "frequency": freq,
                "category_guess": "情绪词",
                "preferred_scene_guess": ["评论区互动", "吐槽整活"],
                "manual_review": {
                    "review_status": "pending",
                    "reviewer": "",
                    "reviewed_at": "",
                    "confidence": 0.45,
                    "notes": "auto extracted from CJK phrase frequency",
                },
                "examples": examples[token][:3],
            }
        )

    candidates.sort(key=lambda x: x["frequency"], reverse=True)
    stats = {
        "latin_terms": len(latin_counter),
        "cjk_terms": len(cjk_counter),
        "candidates": len(candidates),
    }
    return candidates, stats


def _merge_lexicon(base_lexicon: dict, candidates: list[dict]) -> dict:
    merged = dict(base_lexicon)
    meta = merged.get("_meta", {})
    meta.setdefault("version", "v1")
    meta["generated_candidates"] = len(candidates)
    meta["schema"] = "bili_slang_v1"
    merged["_meta"] = meta

    for item in candidates:
        key = item["canonical"]
        if key in merged:
            entry = merged[key]
            if isinstance(entry, dict):
                existing_variants = set(entry.get("variants", []))
                entry["variants"] = sorted(existing_variants | set(item["variants"]))
                entry.setdefault("review", {})
                entry["review"].setdefault("review_status", "approved")
                entry["review"]["auto_frequency"] = item["frequency"]
                entry["review"]["last_auto_seen"] = "v1"
            continue
        merged[key] = {
            "variants": item["variants"],
            "category": item["category_guess"],
            "usage_rules": {
                "preferred_scene": item["preferred_scene_guess"],
                "formality_max": "mid",
            },
            "review": item["manual_review"],
            "evidence": {
                "frequency": item["frequency"],
                "source": item["candidate_source"],
                "examples": item["examples"],
            },
        }
    return merged


def build(
    cleaned_path: Path,
    lexicon_path: Path,
    candidates_out: Path,
    merged_out: Path,
    min_freq: int,
) -> dict:
    rows = read_jsonl(cleaned_path)
    base_lexicon = load_json(lexicon_path)
    candidates, stats = _extract_candidates(rows, min_freq=min_freq)
    write_jsonl(candidates_out, candidates)
    merged = _merge_lexicon(base_lexicon, candidates)
    write_json(merged_out, merged)
    summary = {
        "cleaned_rows": len(rows),
        "stats": stats,
        "candidates_path": str(candidates_out),
        "merged_path": str(merged_out),
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build B站高频词典 v1 from cleaned corpus")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("build")
    p.add_argument("--cleaned", required=True, help="Path to cleaned.jsonl")
    p.add_argument("--lexicon", required=True, help="Base slang_lexicon.json")
    p.add_argument("--candidates-out", default="assets/slang_candidates_v1.jsonl")
    p.add_argument("--merged-out", default="assets/slang_lexicon.v1.generated.json")
    p.add_argument("--min-freq", type=int, default=8)
    args = parser.parse_args()

    summary = build(
        cleaned_path=Path(args.cleaned),
        lexicon_path=Path(args.lexicon),
        candidates_out=Path(args.candidates_out),
        merged_out=Path(args.merged_out),
        min_freq=args.min_freq,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
