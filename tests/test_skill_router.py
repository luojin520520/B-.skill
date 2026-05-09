from __future__ import annotations

import unittest
from pathlib import Path


class SkillRouterTest(unittest.TestCase):
    def test_skill_md_is_thin_router(self) -> None:
        skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
        lines = skill_path.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lines), 120)
        self.assertLessEqual(len(lines), 180)
        text = "\n".join(lines)
        for command in ("/站味", "/改写", "/拆解", "/氛围", "/复刻"):
            self.assertIn(command, text)


if __name__ == "__main__":
    unittest.main()
