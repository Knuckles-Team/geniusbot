import asyncio
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class AgentBridgeSignals(QObject):
    """Signals for reporting agent run outcomes to the main UI thread."""

    started = Signal()
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)


class AgentRunnable(QRunnable):
    """QRunnable wrapper to execute async agent-utilities routines in PySide thread pools."""

    def __init__(self, async_func: Callable[[], Any], *args, **kwargs):
        super().__init__()
        self.signals = AgentBridgeSignals()
        self.async_func = async_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Execute the asynchronous callback inside a background event loop."""
        self.signals.started.emit()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Inject the progress signal emitter as progress_cb keyword argument if needed
            if "progress_cb" not in self.kwargs:
                self.kwargs["progress_cb"] = self.signals.progress.emit
            # Execute async operation
            result = loop.run_until_complete(self.async_func(*self.args, **self.kwargs))
            if isinstance(result, dict):
                self.signals.finished.emit(result)
            else:
                self.signals.finished.emit({"status": "success", "result": str(result)})
        except Exception as exc:
            self.signals.error.emit(f"Agent task failed ({type(exc).__name__})")
        finally:
            loop.close()


class AgentBridgeWorker:
    """Orchestrates threading and scheduling for agent execution."""

    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()

    def run_agent_task(
        self,
        async_func: Callable[[], Any],
        on_finished: Callable[[dict], None],
        on_error: Callable[[str], None] | None = None,
        on_started: Callable[[], None] | None = None,
        on_progress: Callable[[str], None] | None = None,
        *args,
        **kwargs,
    ):
        """Submit an asynchronous task to be run inside the global QThreadPool."""
        runnable = AgentRunnable(async_func, *args, **kwargs)

        # Connect signals
        if on_started is not None:
            runnable.signals.started.connect(on_started)
        if on_finished is not None:
            runnable.signals.finished.connect(on_finished)
        if on_error is not None:
            runnable.signals.error.connect(on_error)
        if on_progress is not None:
            runnable.signals.progress.connect(on_progress)

        self.thread_pool.start(runnable)
