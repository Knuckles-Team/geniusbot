"""R004: off-thread, non-blocking dispatch.

Direct unit coverage of :class:`AgentBridgeWorker`'s started/finished/error/progress
signal contract — every Arbora or backend call reports back to the caller only
through these typed signals, never a blocking return value on the Qt event-loop
thread.
"""

import pytest

from geniusbot.utils.agent_bridge import AgentBridgeWorker


@pytest.mark.spec("AXIL-CLIENT-R004.2")
@pytest.mark.unit
@pytest.mark.concept("GBOT-6.4")
def test_agent_bridge_worker_reports_success_only_through_signals(qapp, qtbot):
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

    qtbot.waitUntil(lambda: any(e[0] == "finished" for e in events), timeout=5000)

    kinds = [e[0] for e in events]
    assert "started" in kinds
    assert "progress" in kinds
    assert ("finished", {"status": "success", "result": "done"}) in events
    assert "error" not in kinds


@pytest.mark.spec("AXIL-CLIENT-R004.2")
@pytest.mark.unit
@pytest.mark.concept("GBOT-6.4")
def test_agent_bridge_worker_reports_failure_only_through_error_signal(qapp, qtbot):
    worker = AgentBridgeWorker()
    events = []

    async def failing_task(progress_cb=None):
        raise RuntimeError("boom")

    worker.run_agent_task(
        failing_task,
        on_finished=lambda data: events.append(("finished", data)),
        on_error=lambda msg: events.append(("error", msg)),
    )

    qtbot.waitUntil(lambda: any(e[0] == "error" for e in events), timeout=5000)

    kinds = [e[0] for e in events]
    assert "error" in kinds
    assert "finished" not in kinds
