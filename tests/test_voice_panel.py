"""Tests for the geniusbot voice dictation panel (CONCEPT:GB-GBOT.cockpit.voice-dictation-cockpit).

Qt runs offscreen (conftest's ``qapp`` fixture). Pure response-shaping logic
is tested without touching the audio backend at all; the panel's honest
states are exercised by feeding it synthetic gateway responses directly
(``_on_transcribed``/``_on_error``), never by driving a real
``QMediaRecorder`` capture -- this sandbox has no microphone hardware
(``QMediaDevices.audioInputs() == []``, confirmed independently), so a real
recording pass is neither meaningful nor safe to exercise here.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from PySide6.QtMultimedia import QMediaRecorder

from geniusbot.qt.voice_panel import (
    VoicePanel,
    extract_transcript,
    status_for_recorder_error,
)


def test_extract_transcript_returns_text_on_success() -> None:
    assert extract_transcript({"text": "hello world"}) == "hello world"


def test_extract_transcript_returns_none_on_error_never_fabricates() -> None:
    assert extract_transcript({"error": "boom"}) is None
    assert extract_transcript({"error": "boom", "text": "should not be used"}) is None


def test_extract_transcript_handles_malformed_response() -> None:
    assert extract_transcript({}) is None
    assert extract_transcript({"text": 42}) is None
    assert extract_transcript("not a dict") is None  # type: ignore[arg-type]


def test_status_for_recorder_error_is_distinct_per_error() -> None:
    messages = {
        status_for_recorder_error(err)
        for err in (
            QMediaRecorder.Error.ResourceError,
            QMediaRecorder.Error.FormatError,
            QMediaRecorder.Error.OutOfSpaceError,
            QMediaRecorder.Error.LocationNotWritable,
        )
    }
    assert len(messages) == 4  # every recorder error renders distinctly


def test_status_for_recorder_error_has_a_fallback_for_no_error() -> None:
    assert status_for_recorder_error(QMediaRecorder.Error.NoError)


def test_panel_shows_no_device_state_in_this_mic_less_sandbox(qapp) -> None:
    # This CI sandbox genuinely has no audio input device -- confirmed via
    # QMediaDevices.audioInputs() == [] -- so construction must land on the
    # honest no-device state, distinctly worded and with recording disabled.
    panel = VoicePanel(MagicMock())
    assert "No microphone device" in panel.status_lbl.text()
    assert panel.btn_record.isEnabled() is False


def test_panel_renders_backend_unavailable_distinctly(qapp) -> None:
    panel = VoicePanel(MagicMock())
    panel.btn_record.setEnabled(False)

    panel._on_transcribed({"error": "not enabled", "unavailable": True})

    assert "not enabled on this server" in panel.status_lbl.text()
    assert panel.btn_record.isEnabled() is True
    assert panel.transcript_box.toPlainText() == ""


def test_panel_renders_a_genuine_error_distinctly(qapp) -> None:
    panel = VoicePanel(MagicMock())

    panel._on_transcribed({"error": "sidecar unreachable"})

    assert "sidecar unreachable" in panel.status_lbl.text()
    assert "not enabled on this server" not in panel.status_lbl.text()
    assert panel.transcript_box.toPlainText() == ""


def test_panel_worker_error_path_renders_distinctly(qapp) -> None:
    panel = VoicePanel(MagicMock())

    panel._on_error("network exploded")

    assert "network exploded" in panel.status_lbl.text()
    assert panel.btn_record.isEnabled() is True


def test_panel_appends_successful_transcript(qapp) -> None:
    panel = VoicePanel(MagicMock())

    panel._on_transcribed({"text": "first clip"})
    assert panel.transcript_box.toPlainText() == "first clip"

    panel._on_transcribed({"text": "second clip"})
    assert panel.transcript_box.toPlainText() == "first clip\nsecond clip"


def test_panel_every_honest_state_message_is_distinct(qapp) -> None:
    panel = VoicePanel(MagicMock())
    messages = set()

    panel._on_transcribed({"error": "x", "unavailable": True})
    messages.add(panel.status_lbl.text())

    panel._on_transcribed({"error": "generic failure"})
    messages.add(panel.status_lbl.text())

    panel._on_error("network failure")
    messages.add(panel.status_lbl.text())

    panel._check_device()  # no-device state (this sandbox has no mic)
    messages.add(panel.status_lbl.text())

    assert len(messages) == 4
