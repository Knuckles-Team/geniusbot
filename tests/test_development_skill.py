from pathlib import Path

import pytest

SKILL = (
    Path(__file__).resolve().parent.parent
    / "geniusbot/skills/geniusbot-development/SKILL.md"
)


@pytest.mark.spec("GENIUSBOT-CLIENT-R015")
def test_skill_packaged_and_valid():
    text = SKILL.read_text()
    assert text.startswith("---\n")
    front = text.split("---", 2)[1]
    assert "name: geniusbot-development" in front
    assert "description:" in front
    assert "## Rapid delivery: the 5-minute contract" in text
