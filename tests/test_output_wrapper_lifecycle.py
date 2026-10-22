"""Qt-owned stream wrappers must not outlive their signal objects."""

import io
import sys

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QObject

from geniusbot.geniusbot import GeniusBot, OutputWrapper


@pytest.mark.spec("GENIUSBOT-CLIENT-R010.2")
def test_destroyed_wrapper_restores_stream_and_nested_writer_stays_safe(
    qapp, monkeypatch
):
    original = io.StringIO()
    monkeypatch.setattr(sys, "stderr", original)
    parent = QObject()
    first = OutputWrapper(parent, stdout=False)
    second_parent = QObject()
    second = OutputWrapper(second_parent, stdout=False)
    parent.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert not first._active
    assert sys.stderr is second
    sys.stderr.write("after first destruction")
    second_parent.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert sys.stderr is original
    sys.stderr.write(" and second destruction")
    assert original.getvalue() == "after first destruction and second destruction"


@pytest.mark.spec("GENIUSBOT-CLIENT-R010.2")
def test_real_window_close_restores_streams_before_reopening(qapp, monkeypatch):
    stdout, stderr = sys.stdout, sys.stderr
    for _ in range(2):
        bot = GeniusBot()
        monkeypatch.setattr(bot.daemon.tray_icon, "isVisible", lambda: False)
        bot.log_to_console("before close")
        assert "before close" in bot.console.toPlainText()
        bot.close()
        assert sys.stdout is stdout
        assert sys.stderr is stderr
        sys.stderr.write("window closed safely\n")
        bot.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


@pytest.mark.spec("GENIUSBOT-CLIENT-R010.2")
def test_stream_slot_error_is_reported_once_without_recursive_emission(
    qapp, qtbot, monkeypatch
):
    original = io.StringIO()
    monkeypatch.setattr(sys, "stderr", original)
    parent = QObject()
    wrapper = OutputWrapper(parent, stdout=False)

    def broken_slot(text, is_stdout):
        raise RuntimeError("console slot failed")

    wrapper.outputWritten.connect(broken_slot)
    try:
        with qtbot.captureExceptions() as errors:
            wrapper.write("original output")
        assert len(errors) == 1
        assert errors[0][0] is RuntimeError
        assert "original output" in original.getvalue()
    finally:
        wrapper.restore()
