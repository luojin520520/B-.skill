#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
QQ_RE = re.compile(r"\b[1-9][0-9]{4,10}\b")
WECHAT_RE = re.compile(r"\b[a-zA-Z][-_a-zA-Z0-9]{5,19}\b")
ADDR_RE = re.compile(r"(省|市|区|县|路|街|号)")
SYMBOL_ONLY_RE = re.compile(r"^[\W_]+$", re.UNICODE)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    path.write_text(body + ("\n" if body else ""), encoding="utf-8")


def hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sanitize_author(author: str) -> str:
    if not author:
        return "anon"
    return "u_" + hash_text(author)[:12]


def sanitize_content(text: str) -> str:
    text = text.strip()
    text = PHONE_RE.sub("[PHONE]", text)
    text = QQ_RE.sub("[QQ]", text)
    text = WECHAT_RE.sub(lambda m: "[WX]" if "微信" in text else m.group(0), text)
    if ADDR_RE.search(text) and len(text) > 12:
        text = text.replace("省", "[ADDR]").replace("市", "[ADDR]")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("。。。", "…").replace("..", "。")
    return text.strip()


def is_noise(text: str) -> bool:
    if not text or len(text) < 2:
        return True
    if SYMBOL_ONLY_RE.match(text):
        return True
    lowered = text.lower()
    return lowered in {"好看", "不错", "。。", "。", " ", "1", "顶"}


def tokenize(text: str) -> list[str]:
    # Lightweight tokenizer suitable for Chinese short texts.
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text.lower())
    parts = [p for p in normalized.split(" ") if p]
    if not parts:
        return list(text)
    return parts
