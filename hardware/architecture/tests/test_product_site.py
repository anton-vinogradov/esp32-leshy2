import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


class ProductSiteTests(unittest.TestCase):
    PUBLIC_PAGES = (
        "README.md",
        "README.ru.md",
        "docs/hardware.md",
        "docs/hardware.ru.md",
        "docs/pinout.md",
        "docs/pinout.ru.md",
        "docs/safety.md",
        "docs/safety.ru.md",
    )

    def read(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_public_site_contains_only_product_pages(self):
        docs_markdown = {
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.glob("docs/**/*.md")
        }
        self.assertEqual(set(self.PUBLIC_PAGES[2:]), docs_markdown)

        for name in self.PUBLIC_PAGES:
            page = self.read(name)
            for forbidden in (
                "DEC-", "FND-", "REV-", "IMP-", "docs/review",
                "docs/status", "docs/stages", "проведено ревью",
            ):
                self.assertNotIn(forbidden, page, f"{name}: {forbidden}")

    def test_all_local_public_links_exist(self):
        for name in self.PUBLIC_PAGES:
            page_path = REPO_ROOT / name
            page = page_path.read_text(encoding="utf-8")
            for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", page):
                if target.startswith(("http://", "https://", "#")):
                    continue
                resolved = (page_path.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.exists(), f"{name}: missing {target}")

    def test_layout_is_product_facing(self):
        layout = self.read("docs/images/current-clamshell.svg")
        for token in (
            "Leshy2 — two-board clamshell layout",
            "HMX035CTFT-001",
            "M5Stack U214",
            "Keystone 1048P",
            "D-pad + OK",
            "STOP",
            "PTT",
            "RE-ARM",
        ):
            self.assertIn(token, layout)
        for process_token in ("G3-0001", "not G7", "not KiCad", "Working projection"):
            self.assertNotIn(process_token, layout)

    def test_project_history_is_archived_outside_public_docs(self):
        archive = REPO_ROOT / "drafts/project-history-2026-08-19"
        self.assertTrue((archive / "review/README.md").is_file())
        self.assertTrue((archive / "status/current-state.md").is_file())
        self.assertTrue((archive / "stages/03-target-product-design.md").is_file())
        self.assertTrue((archive / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
