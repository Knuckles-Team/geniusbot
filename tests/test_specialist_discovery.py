"""Specialist discovery preserves structured results across the real worker signals."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QLabel, QWidget

from geniusbot.geniusbot import GeniusBot
from geniusbot.qt.widget_mapper import WidgetSchemaMapper
from geniusbot.utils.agent_bridge import AgentBridgeWorker


@pytest.mark.parametrize(
    "specialists",
    [[], [{"name": "Explorer", "skills": ["search"], "type": "specialist"}]],
)
def test_specialist_list_survives_worker_signal(qapp, monkeypatch, specialists):
    monkeypatch.setattr(QThreadPool, "start", lambda self, task: task.run())
    worker = AgentBridgeWorker()
    bot = SimpleNamespace(
        worker=worker,
        gateway=SimpleNamespace(fetch_specialists=AsyncMock(return_value=specialists)),
        lbl_status=QLabel(),
        discovered_specialists=[],
        populate_specialist_deck=Mock(),
    )

    GeniusBot.async_load_specialists(bot)

    assert bot.discovered_specialists == specialists
    assert bot.lbl_status.text() == f"{len(specialists)} specialists loaded."
    bot.populate_specialist_deck.assert_called_once_with()
    parent = QWidget()
    cards = WidgetSchemaMapper.build_deck(bot.discovered_specialists, worker, parent)
    assert len(cards) == len(specialists)
    for card, specialist in zip(cards, specialists, strict=True):
        assert card.agent_data == specialist
    parent.close()


def test_specialist_discovery_error_remains_offline(qapp, monkeypatch):
    monkeypatch.setattr(QThreadPool, "start", lambda self, task: task.run())
    bot = SimpleNamespace(
        worker=AgentBridgeWorker(),
        gateway=SimpleNamespace(fetch_specialists=AsyncMock(side_effect=RuntimeError)),
        lbl_status=QLabel(),
        discovered_specialists=[],
        populate_specialist_deck=Mock(),
    )

    GeniusBot.async_load_specialists(bot)

    assert bot.lbl_status.text() == "Graph offline."
    assert bot.discovered_specialists == []
    bot.populate_specialist_deck.assert_not_called()
