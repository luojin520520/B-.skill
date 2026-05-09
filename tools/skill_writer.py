#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import read_jsonl


def list_skill(project_root: Path) -> dict:
    anchors = read_jsonl(project_root / "assets" / "anchors.jsonl")
    return {
        "name": "B站文化 skill",
        "anchors": len(anchors),
        "commands": ["站味", "改写", "拆解", "氛围", "复刻", "检索", "词典", "校准", "评测", "纠偏", "版本"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill writer helper")
    parser.add_argument("--action", required=True, choices=["list"])
    parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    if args.action == "list":
        print(json.dumps(list_skill(Path(args.project_root)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
