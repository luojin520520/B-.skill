#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


def install_package(package_dir: Path, skills_dir: Path, force: bool = True) -> Path:
    target = skills_dir / package_dir.name
    if target.exists() and force:
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_dir, target)
    return target
