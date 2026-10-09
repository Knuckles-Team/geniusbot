"""R004: off-thread, non-blocking dispatch.

Direct unit coverage of :class:`AgentBridgeWorker`'s started/finished/error/progress
signal contract — every Graph OS or backend call reports back to the caller only
through these typed signals, never a blocking return value on the Qt event-loop
thread.
"""

import pytest
from PySide6.QtCore import QCoreApplication

from geniusbot.utils.agent_bridge import AgentBridgeWorker


def _pump_until(predicate, attempts=200):
    for _ in range(attempts):
        QCoreApplication.processEvents()
        if predicate():
            return True
    return False


@pytest.mark.spec("GENIUSBOT-CLIENT-R004")
@pytest.mark.unit
@pytest.mark.concept("GBOT-6.4")
def test_agent_bridge_worker_reports_success_only_through_signals(qapp):
    worker = AgentBridgeWorker()
    events = []

    async def ok_task(progress_cb=None):
        progress_cb("working")
        return {"status": "success", "result": "done"}

    worker.run_agent_task(
        ok_task,
        on_finished=lambda data: events.append(("finished", data)),
        on_error=lambda msg: events.append(("error", msg)),
        on_started=lambda: events.append(("started", None)),
        on_progress=lambda msg: events.append(("progress", msg)),
    )

    assert _pump_until(
        lambda: any(e[0] == "finished" for e in events)
    ), "agent task did not report a finished signal"

    kinds = [e[0] for e in events]
    assert "started" in kinds
    assert "progress" in kinds
    assert ("finished", {"status": "success", "result": "done"}) in events
    assert "error" not in kinds


@pytest.mark.spec("GENIUSBOT-CLIENT-R004")
@pytest.mark.unit
@pytest.mark.concept("GBOT-6.4")
def test_agent_bridge_worker_reports_failure_only_through_error_signal(qapp):
    worker = AgentBridgeWorker()
    events = []

    async def failing_task(progress_cb=None):
        raise RuntimeError("boom")

    worker.run_agent_task(
        failing_task,
        on_finished=lambda data: events.append(("finished", data)),
        on_error=lambda msg: events.append(("error", msg)),
    )

    assert _pump_until(
        lambda: any(e[0] == "error" for e in events)
    ), "failing agent task did not report an error signal"

    kinds = [e[0] for e in events]
    assert "error" in kinds
    assert "finished" not in kinds
