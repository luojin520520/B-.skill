#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from eval_style import gate


def build_manifest(command_name: str) -> dict:
    return {
        "manifest_version": "1",
        "id": "culture.bilibili",
        "entrypoint": "SKILL.md",
        "command_name": command_name,
        "compatible_runtimes": ["claude-code", "openclaw", "codex"],
        "artifacts": [
            "SKILL.md",
            "assets/profile.json",
            "assets/anchors.jsonl",
            "assets/tag_dictionary.json",
            "assets/slang_lexicon.json",
            "assets/evalset.jsonl",
            "assets/corrections.jsonl"
        ]
    }


def export(project_root: Path, out_dir: Path, command_name: str) -> Path:
    gate_result = gate(project_root / "assets")
    if not gate_result["pass"]:
        raise RuntimeError(f"style gate failed: {gate_result}")
    package_dir = out_dir / command_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    for rel in ("SKILL.md", "assets", "tools"):
        src = project_root / rel
        dst = package_dir / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    manifest = build_manifest(command_name)
    (package_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return package_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Export runtime package")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("export")
    p.add_argument("--project-root", default=str(ROOT))
    p.add_argument("--out-dir", default=str(ROOT / "dist"))
    p.add_argument("--command-name", default="站味")
    p.add_argument("--target-runtime", default="all")
    args = parser.parse_args()

    package = export(Path(args.project_root), Path(args.out_dir), args.command_name)
    print(str(package))


if __name__ == "__main__":
    main()
