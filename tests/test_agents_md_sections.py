from pathlib import Path

import pytest

AGENTS = Path(__file__).resolve().parent.parent / "AGENTS.md"
REQUIRED = [
    "What this repository owns",
    "Commands",
    "Quality gates",
    "Development rules",
    "Documentation",
    "Branching & isolation",
]


@pytest.mark.spec("AXIL-CLIENT-R018")
def test_required_headings_present():
    headings = [
        ln[3:].strip() for ln in AGENTS.read_text().splitlines() if ln.startswith("## ")
    ]
    missing = [h for h in REQUIRED if h not in headings]
    assert not missing
    assert [headings.index(h) for h in REQUIRED] == sorted(
        headings.index(h) for h in REQUIRED
    )
