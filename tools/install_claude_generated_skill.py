#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from install_generated_skill_common import install_package


def main() -> None:
    parser = argparse.ArgumentParser(description="Install package into Claude skills dir")
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--skills-dir", default=str(Path.home() / ".claude" / "skills"))
    args = parser.parse_args()
    target = install_package(Path(args.package_dir), Path(args.skills_dir))
    print(str(target))


if __name__ == "__main__":
    main()
