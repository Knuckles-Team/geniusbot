"""R006: no local approval authority.

A governed or mutating action is never authorized by the desktop process itself;
the operator's explicit decision is always forwarded to Graph OS's server-side
approval endpoint, which performs the authoritative check.
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from geniusbot.qt.fleet_cockpit import FleetCockpitPanel


class _RecordingWorker:
    """Captures the dispatched async callable instead of running it, so the test
    can invoke it directly and inspect exactly what it awaits."""

    def __init__(self):
        self.last_task = None

    def run_agent_task(self, async_func, on_finished=None, on_error=None, **_):
        self.last_task = async_func


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.5")
def test_grant_forwards_to_gateway_approval_endpoint(qapp, monkeypatch):
    worker = _RecordingWorker()
    panel = FleetCockpitPanel(worker)
    mock_grant = AsyncMock(return_value={"status": "granted"})
    monkeypatch.setattr(panel.gateway, "grant_approval", mock_grant)

    panel._grant("approval-123")

    assert panel.worker.last_task is not None, "grant did not dispatch a task"
    result = asyncio.run(panel.worker.last_task())

    mock_grant.assert_awaited_once_with("approval-123")
    assert result == {"granted": "approval-123", "result": {"status": "granted"}}
    panel.close()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.5")
def test_grant_never_marks_authorized_without_the_round_trip(qapp, monkeypatch):
    worker = _RecordingWorker()
    panel = FleetCockpitPanel(worker)
    mock_grant = AsyncMock(side_effect=RuntimeError("gateway unreachable"))
    monkeypatch.setattr(panel.gateway, "grant_approval", mock_grant)

    panel._grant("approval-456")

    with pytest.raises(RuntimeError):
        asyncio.run(panel.worker.last_task())

    mock_grant.assert_awaited_once_with("approval-456")
    panel.close()
