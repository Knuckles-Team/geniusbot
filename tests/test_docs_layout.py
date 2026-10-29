from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    "architecture",
    "apps",
    "design-system",
    "deployment",
    "features",
    "start",
    "status",
    "agents",
]


@pytest.mark.spec("AXIL-CLIENT-R017")
def test_nav_lists_every_page():
    nav = (ROOT / "mkdocs.yml").read_text().split("nav:", 1)[1]
    for page in PAGES:
        assert (ROOT / "docs" / f"{page}.md").is_file(), page
        assert f"{page}.md" in nav, page
