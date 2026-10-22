"""Dashboard refreshes stay off-thread and clear stale data on refusal."""

import asyncio
import subprocess
import sys
import textwrap
import threading

import pytest
from PySide6.QtCore import QThread

from geniusbot.qt.service_dashboard import ServiceDashboardPanel
from geniusbot.services.backend_adapter import backend


@pytest.mark.spec("GENIUSBOT-CLIENT-R001.3")
def test_dashboard_is_nonblocking_cancellable_and_ignores_late_results(
    qtbot, monkeypatch
):
    entered = threading.Event()
    cancelled = threading.Event()
    threads = []

    async def snapshot():
        threads.append(QThread.currentThread())
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    monkeypatch.setattr(backend, "service_dashboard_snapshot", snapshot)
    panel = ServiceDashboardPanel()
    qtbot.addWidget(panel)
    qtbot.waitUntil(entered.is_set)
    worker = panel._fetch_worker
    assert threads[0] != panel.thread()
    panel._refresh_data()
    assert panel._fetch_worker is worker
    panel.close()
    qtbot.waitUntil(cancelled.is_set)
    qtbot.waitUntil(lambda: panel._fetch_worker is None)
    panel._on_snapshot_ready({"layout": {"groups": []}, "data": {}})
    assert not panel._cards
    assert panel.stats_label.text() == "Loading..."


@pytest.mark.spec("GENIUSBOT-CLIENT-R001.3")
def test_dashboard_renders_then_clears_on_refusal_and_can_retry(qtbot, monkeypatch):
    responses = [
        {
            "layout": {
                "groups": [
                    {
                        "name": "Services",
                        "services": [
                            {"id": "svc", "name": "Service", "url": "", "visible": True}
                        ],
                    }
                ]
            },
            "data": {
                "svc": {"status": "ok", "fields": [{"label": "jobs", "value": "4"}]}
            },
        },
        RuntimeError("denied"),
        {"layout": {"groups": []}, "data": {}},
    ]

    async def snapshot():
        result = responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(backend, "service_dashboard_snapshot", snapshot)
    panel = ServiceDashboardPanel()
    qtbot.addWidget(panel)
    try:
        qtbot.waitUntil(lambda: panel._fetch_worker is None)
        assert list(panel._cards) == ["svc"]
        assert "1 healthy" in panel.stats_label.text()
        panel._refresh_data()
        qtbot.waitUntil(lambda: panel._fetch_worker is None)
        assert not panel._cards
        assert "Fetch error" in panel.stats_label.text()
        panel._refresh_data()
        qtbot.waitUntil(lambda: panel._fetch_worker is None)
        assert not panel._cards
        assert "0 services" in panel.stats_label.text()
    finally:
        panel.cleanup()


@pytest.mark.spec("GENIUSBOT-CLIENT-R001.3")
@pytest.mark.parametrize("stalled_cleanup", [False, True])
def test_application_quit_bounds_fetch_cancellation(stalled_cleanup):
    script = textwrap.dedent("""
        import asyncio
        import sys
        import threading
        import time
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from geniusbot.qt.service_dashboard import ServiceDashboardPanel
        from geniusbot.services.backend_adapter import backend

        entered = threading.Event()
        cleaned = threading.Event()
        async def snapshot():
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                if sys.argv[1] == "stalled":
                    await asyncio.Event().wait()
                await asyncio.sleep(0.05)
                cleaned.set()
        backend.service_dashboard_snapshot = snapshot
        app = QApplication([])
        panel = ServiceDashboardPanel()
        timer = QTimer()
        timer.timeout.connect(lambda: app.quit() if entered.is_set() else None)
        timer.start(5)
        started = time.monotonic()
        app.exec()
        assert time.monotonic() - started < 2.0
        if sys.argv[1] != "stalled":
            assert cleaned.is_set(), "quit abandoned cooperative HTTP cleanup"
        assert panel._fetch_worker._done.is_set()
    """)
    result = subprocess.run(
        [sys.executable, "-c", script, "stalled" if stalled_cleanup else "delayed"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
