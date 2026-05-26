"""Smoke test for application startup."""

from geniusbot.geniusbot import GeniusBot


def test_app_startup(qapp):
    """Verify that the GeniusBot instance can be created and closed cleanly."""
    bot = GeniusBot()
    assert bot is not None
    # Verify basics
    assert bot.windowTitle() == "GeniusBot Multi-Agent Cockpit"
    bot.close()
