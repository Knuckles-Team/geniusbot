from pathlib import Path

import pytest

CONFIG = Path(__file__).resolve().parent.parent / ".pre-commit-config.yaml"
PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
REQUIRED = ["public-surface", "ste-staged", "ste-staleness-staged", "spec-standard"]


@pytest.mark.spec("GENIUSBOT-CLIENT-R016")
def test_required_pipelines_hook_ids_present():
    text = CONFIG.read_text()
    for hook in REQUIRED:
        assert f"- id: {hook}\n" in text, hook
    py = PYPROJECT.read_text()
    assert "[tool.pipelines_hooks.public_surface]" in py
    assert "[tool.pipelines_hooks.ste]" in py
