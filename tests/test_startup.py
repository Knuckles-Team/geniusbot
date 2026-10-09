"""Smoke test for application startup."""

import pytest

from geniusbot.geniusbot import GeniusBot
from geniusbot.services.operation_registry import OperationRegistryError


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_app_startup(qapp):
    """Verify that the GeniusBot instance can be created and closed cleanly."""
    bot = GeniusBot()
    assert bot is not None
    # Verify basics
    assert bot.windowTitle() == "GeniusBot Multi-Agent Cockpit"
    assert bot.operation_registry is not None
    bot.close()


@pytest.mark.unit
@pytest.mark.concept("GENIUSBOT-CLIENT-R002.2")
def test_app_startup_refuses_malformed_operation_registry(qapp, tmp_path, monkeypatch):
    """A malformed installed operation registry refuses startup through the real entry point."""
    malformed = tmp_path / "operation_registry.json"
    malformed.write_text("not valid json")
    monkeypatch.setenv("GENIUSBOT_OPERATION_REGISTRY_PATH", str(malformed))

    with pytest.raises(OperationRegistryError):
        GeniusBot()


@pytest.mark.unit
@pytest.mark.concept("GENIUSBOT-CLIENT-R002.2")
def test_app_startup_refuses_missing_operation_registry(qapp, tmp_path, monkeypatch):
    """A missing installed operation registry file refuses startup through the real entry point."""
    monkeypatch.setenv(
        "GENIUSBOT_OPERATION_REGISTRY_PATH", str(tmp_path / "does-not-exist.json")
    )

    with pytest.raises(OperationRegistryError):
        GeniusBot()
