#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def backup(skill_dir: Path, version: str) -> Path:
    versions = skill_dir / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    target = versions / version
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for item in ("SKILL.md", "assets"):
        src = skill_dir / item
        if src.is_dir():
            shutil.copytree(src, target / item)
        elif src.exists():
            shutil.copy2(src, target / item)
    return target


def rollback(skill_dir: Path, version: str) -> None:
    src = skill_dir / "versions" / version
    if not src.exists():
        raise FileNotFoundError(version)
    for item in ("SKILL.md", "assets"):
        dst = skill_dir / item
        s = src / item
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        if s.is_dir():
            shutil.copytree(s, dst)
        elif s.exists():
            shutil.copy2(s, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple version manager")
    parser.add_argument("--action", required=True, choices=["backup", "rollback"])
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    if args.action == "backup":
        p = backup(skill_dir, args.version)
        print(str(p))
    else:
        rollback(skill_dir, args.version)
        print("ok")


if __name__ == "__main__":
    main()
