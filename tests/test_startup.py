"""Smoke test for application startup."""

import pytest

from geniusbot.geniusbot import GeniusBot


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_app_startup(qapp):
    """Verify that the GeniusBot instance can be created and closed cleanly."""
    bot = GeniusBot()
    assert bot is not None
    # Verify basics
    assert bot.windowTitle() == "GeniusBot Multi-Agent Cockpit"
    bot.close()
