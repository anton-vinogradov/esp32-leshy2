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
        "docs/schematics.md",
        "docs/schematics.ru.md",
        "docs/interconnect.md",
        "docs/interconnect.ru.md",
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
            "Leshy2 — dimensioned external layout",
            "HMX035CTFT-001",
            "M5Stack U214",
            "Keystone 1048P",
            "single D-pad cap",
            "STOP",
            "PTT",
            "RE-ARM",
            "physical actual-TX evidence for each transmitting path",
            "M2.5 hole/head keep-outs",
            "GCT RFPC-SMA31-FN-175-A",
            "GCT RFPC-SMA32-FN-175-A",
        ):
            self.assertIn(token, layout)
        for process_token in ("G3-0001", "not G7", "not KiCad", "Working projection"):
            self.assertNotIn(process_token, layout)

    def test_internal_layout_is_dimensioned_and_separates_devices(self):
        layout = self.read("docs/images/internal-board-layout.svg")
        for token in (
            "Leshy2 — dimensioned inner-board placement",
            "Every solid rectangle is one device",
            "Numbered physical devices",
            "UI/control PCB",
            "RF/power PCB",
            "outward direction arrow",
            "M2.5 hole/head keep-out",
            "FX8C-80P-SV1(92)",
            "FX8C-80S-SV5(92)",
            "AS02404PO",
            "CMEJ-0413-42-SMT-TR",
            "JS102011SCQN",
            "SKQGADE010",
            "FTSH-105-01-L-DV-K-P-TR",
        ):
            self.assertIn(token, layout)

    def test_sandwich_section_uses_registered_component_depths(self):
        layout = self.read("docs/images/sandwich-section.svg")
        for token in (
            "Leshy2 — dimensioned front-to-rear sandwich",
            "HMX035CTFT-001",
            "FX8C M1 · 11-mm board-to-board",
            "AS02404PO",
            "Keystone Electronics 1048P",
            "M5Stack U214",
            "Dimensioned architecture projection",
        ):
            self.assertIn(token, layout)

    def test_principle_component_diagrams_are_public_and_discoverable(self):
        for hardware, schematics in (
            ("docs/hardware.md", "docs/schematics.md"),
            ("docs/hardware.ru.md", "docs/schematics.ru.md"),
        ):
            landing = self.read(hardware)
            diagrams = self.read(schematics)
            self.assertIn(f"]({Path(schematics).name})", landing)
            self.assertGreaterEqual(diagrams.count("```mermaid"), 10)
            for token in (
                "HMX035CTFT-001",
                "CMEJ-0413-42-SMT-TR",
                "AS02404PO",
                "SKQGADE010",
                "FTSH-105-01-L-DV-K-P-TR",
                "USB4105-GF-A",
                "AEQ10410",
                "JS102011SCQN",
            ):
                self.assertIn(token, diagrams)

    def test_project_history_is_archived_outside_public_docs(self):
        archive = REPO_ROOT / "drafts/project-history-2026-08-19"
        self.assertTrue((archive / "review/README.md").is_file())
        self.assertTrue((archive / "status/current-state.md").is_file())
        self.assertTrue((archive / "stages/03-target-product-design.md").is_file())
        self.assertTrue((archive / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
