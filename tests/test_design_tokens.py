"""The Qt palette is reproducible from the tracked design-token source."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
GENERATOR_PATH = ROOT / "design-system" / "gen_qss.py"
COLORS_PATH = ROOT / "geniusbot" / "qt" / "colors.py"


def _generator():
    spec = importlib.util.spec_from_file_location("gen_qss", GENERATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.spec("GENIUSBOT-CLIENT-R013")
def test_colors_match_generated_output() -> None:
    """The checked-in module must be byte-identical to generator output."""
    assert COLORS_PATH.read_text(encoding="utf-8") == _generator().render()


@pytest.mark.spec("GENIUSBOT-CLIENT-R013")
def test_hand_edited_color_constant_is_detected() -> None:
    """Changing a generated token makes the checked-in output stale."""
    current = COLORS_PATH.read_text(encoding="utf-8")
    edited = current.replace('BG_PRIMARY = "#121214"', 'BG_PRIMARY = "#000000"', 1)
    assert edited != _generator().render()
