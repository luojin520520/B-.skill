#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import load_json, read_jsonl, tokenize, write_jsonl

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SESSION_PATH = ASSETS / "session_state.json"


def _load_anchors() -> list[dict]:
    return read_jsonl(ASSETS / "anchors.jsonl")


def _load_lexicon() -> dict:
    return load_json(ASSETS / "slang_lexicon.json")


def _load_profile() -> dict:
    return load_json(ASSETS / "profile.json")


def _load_session() -> dict:
    if SESSION_PATH.exists():
        return load_json(SESSION_PATH)
    return {"style_density": "med", "formality": "mid", "max_aggression": "low"}


def _save_session(payload: dict) -> None:
    SESSION_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _contains_slang(text: str, lexicon: dict) -> int:
    low = text.lower()
    hits = 0
    for k, v in lexicon.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        values = [k] + v.get("variants", [])
        if any(x.lower() in low for x in values):
            hits += 1
    return hits


def _score(query: str, anchor: dict, lexicon: dict) -> float:
    q_tokens = set(tokenize(query))
    a_tokens = set(tokenize(anchor["text"]))
    overlap = len(q_tokens & a_tokens) / max(1, len(q_tokens))
    slang = _contains_slang(query, lexicon) * 0.08
    scene_bonus = 0.15 if anchor.get("scene") in query else 0.0
    slang_vector = anchor.get("slang_vector", {})
    slang_cat_bonus = 0.04 * len(slang_vector.get("categories", []))
    risk_penalty = 0.0
    if anchor.get("aggression_risk") == "high":
        risk_penalty = 0.08
    elif anchor.get("aggression_risk") == "med":
        risk_penalty = 0.03
    return overlap + slang + scene_bonus + slang_cat_bonus + float(anchor.get("weight", 1.0)) * 0.01 - risk_penalty


def retrieve(query: str, top_k: int) -> list[dict]:
    anchors = _load_anchors()
    lexicon = _load_lexicon()
    scored = sorted(
        (
            {
                "id": a["id"],
                "text": a["text"],
                "scene": a.get("scene", "评论区互动"),
                "score": round(_score(query, a, lexicon), 4),
                "cluster": a.get("cluster", "unknown"),
                "aggression_risk": a.get("aggression_risk", "low"),
            }
            for a in anchors
        ),
        key=lambda x: x["score"],
        reverse=True,
    )
    picked = scored[:top_k]
    if len(picked) > 3:
        clusters = {p["cluster"] for p in picked}
        if len(clusters) < 2 and len(scored) > top_k:
            picked[-1] = scored[top_k]
    return picked


def _render(mode: str, user_text: str, anchors: list[dict], session: dict) -> dict:
    if not anchors:
        return {
            "mode": mode,
            "output": f"未检索到足够锚点，先给你中性版本：{user_text}",
            "anchors": [],
            "style_density": session["style_density"],
            "note": "evidence_insufficient",
        }
    # Control meme overload by reducing quote count when style_density is low.
    quote_size = 2 if session["style_density"] == "low" else 3
    quote = " | ".join(a["text"] for a in anchors[:quote_size])
    prefix = {
        "chat": "站味回复",
        "rewrite": "改写结果",
        "vibe": "氛围文案",
        "mimic": "复刻结果",
    }.get(mode, "分析结果")
    out = f"{prefix}（density={session['style_density']}）:\n{user_text}\n参考锚点: {quote}"
    if session.get("max_aggression") == "low":
        out = out.replace("滚", "先冷静")
    return {
        "mode": mode,
        "output": out,
        "anchors": anchors,
        "style_density": session["style_density"],
    }


def _append_correction(input_text: str, feedback: str, expected: str) -> dict:
    rows = read_jsonl(ASSETS / "corrections.jsonl")
    anchors = _load_anchors()
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "input": input_text,
        "feedback": feedback,
        "expected": expected,
        "action": "reweighted",
    }
    rows.append(row)
    write_jsonl(ASSETS / "corrections.jsonl", rows)
    # Immediate writeback: down-weight similar anchors, add expected sentence as new anchor.
    lowered = input_text.lower()
    for anchor in anchors:
        if any(tok in anchor["text"].lower() for tok in tokenize(lowered)[:4]):
            anchor["weight"] = max(0.3, float(anchor.get("weight", 1.0)) - 0.2)
    anchors.append(
        {
            "id": f"c{len(anchors)+1}",
            "text": expected,
            "scene": "评论区互动",
            "polarity": "neu",
            "formality": "mid",
            "meme_density": "med",
            "interaction_strength": "med",
            "aggression_risk": "low",
            "cluster": "纠偏新增",
            "weight": 1.1,
            "source_id": "correction",
        }
    )
    write_jsonl(ASSETS / "anchors.jsonl", anchors)
    return row


def _version_info() -> dict[str, Any]:
    profile = _load_profile()
    return {
        "profile_version": profile.get("profile_version", "unknown"),
        "anchors_count": len(_load_anchors()),
        "corrections_count": len(read_jsonl(ASSETS / "corrections.jsonl")),
        "updated_at": profile.get("updated_at", "unknown"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Local runtime engine for Bilibili culture skill")
    sub = parser.add_subparsers(dest="action", required=True)

    for act in ("chat", "rewrite", "analyze", "vibe", "mimic", "retrieve"):
        p = sub.add_parser(act)
        p.add_argument("--input", required=True)
        p.add_argument("--top-k", type=int, default=8)
        p.add_argument("--scene", default="评论区互动")

    lex = sub.add_parser("lexicon")
    lex.add_argument("--term", required=True)

    cal = sub.add_parser("calibrate")
    cal.add_argument("--style-density", choices=["low", "med", "high"], required=True)
    cal.add_argument("--formality", choices=["low", "mid", "high"], required=True)
    cal.add_argument("--max-aggression", choices=["low", "med", "high"], required=True)

    cor = sub.add_parser("correct")
    cor.add_argument("--input", required=True)
    cor.add_argument("--feedback", required=True)
    cor.add_argument("--expected", required=True)

    sub.add_parser("version")
    args = parser.parse_args()
    session = _load_session()

    if args.action == "retrieve":
        print(json.dumps(retrieve(args.input, args.top_k), ensure_ascii=False, indent=2))
        return
    if args.action == "lexicon":
        lexicon = _load_lexicon()
        data = lexicon.get(args.term.lower()) or lexicon.get(args.term)
        print(json.dumps(data or {"message": "term_not_found"}, ensure_ascii=False, indent=2))
        return
    if args.action == "calibrate":
        session = {
            "style_density": args.style_density,
            "formality": args.formality,
            "max_aggression": args.max_aggression,
        }
        _save_session(session)
        print(json.dumps(session, ensure_ascii=False, indent=2))
        return
    if args.action == "correct":
        print(json.dumps(_append_correction(args.input, args.feedback, args.expected), ensure_ascii=False, indent=2))
        return
    if args.action == "version":
        print(json.dumps(_version_info(), ensure_ascii=False, indent=2))
        return
    if args.action == "analyze":
        hits = retrieve(args.input, args.top_k)
        categories = []
        for h in hits[:5]:
            if h.get("cluster") not in categories:
                categories.append(h["cluster"])
        result = {
            "input": args.input,
            "top_scene": hits[0]["scene"] if hits else "unknown",
            "slang_hits": _contains_slang(args.input, _load_lexicon()),
            "style_atoms": categories,
            "anchors": hits[:5],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    mode = {"chat": "chat", "rewrite": "rewrite", "vibe": "vibe", "mimic": "mimic"}[args.action]
    anchors = retrieve(args.input, max(3, min(args.top_k, 8)))
    rendered = _render(mode, args.input, anchors, session)
    print(json.dumps(rendered, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
