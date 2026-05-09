from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from export_skill import export
from install_generated_skill_common import install_package


class ExportInstallTest(unittest.TestCase):
    def test_export_and_install(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = export(project_root, root / "dist", "站味")
            self.assertTrue((package / "manifest.json").exists())
            installed = install_package(package, root / "skills")
            self.assertTrue((installed / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
