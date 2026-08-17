#!/usr/bin/env python3
"""CONCEPT:GB-GBOT.cockpit.voice-dictation-cockpit — Voice Dictation Cockpit.

Desktop microphone dictation: capture via QtMultimedia
(``QMediaCaptureSession`` + ``QAudioInput`` + ``QMediaRecorder``), transcribe
the finished clip through the SAME governed backend the webui's dictation
control uses -- ``POST /api/enhanced/voice/transcribe``
(backend ``AU-ECO.mcp.webui-voice-transcription-delegation``, itself
delegating through the ``audio-transcriber-mcp`` sidecar) -- via the shared
gateway SDK facade (ECO-4.37). geniusbot talks to the agent-utilities
gateway (port 8000), not agent-webui's own backend process directly; the
route is reachable there too because ``build_agent_app`` mounts the WebUI's
whole backend at ``/``.

Honest states, same discipline the webui control uses: no microphone
device, a recorder/permission failure, backend unavailable, and a genuine
network/transcription error are each shown distinctly -- never collapsed
into one generic "failed" label. TTS/playback of synthesized speech is
explicitly NOT implemented here: no backend route exists to synthesize
speech yet (tracked separately, out of this panel's scope).

All gateway access goes through the shared SDK via the geniusbot facade;
network runs off the UI thread through the AgentBridgeWorker.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import (
    QAudioInput,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaFormat,
    QMediaRecorder,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BORDER_COLOR
from geniusbot.services.gateway_client import GatewayClient

#: QMediaRecorder.Error -> a status message distinct from every other honest
#: state this panel can be in (no-device / backend-unavailable / generic
#: network error). Desktop Qt has no dedicated "permission denied" enum
#: value; ResourceError is the cross-platform proxy -- the OS refusing the
#: audio device is what a denied mic permission usually surfaces as.
_RECORDER_ERROR_MESSAGES = {
    QMediaRecorder.Error.ResourceError: "Microphone access was denied or the device is busy.",
    QMediaRecorder.Error.FormatError: "This system cannot record in the required audio format.",
    QMediaRecorder.Error.OutOfSpaceError: "Not enough disk space to record.",
    QMediaRecorder.Error.LocationNotWritable: "Could not write the recording to a temporary file.",
}


def status_for_recorder_error(error: QMediaRecorder.Error) -> str:
    """Map a ``QMediaRecorder.Error`` to its distinct honest status message."""
    return _RECORDER_ERROR_MESSAGES.get(error, "Recording failed unexpectedly.")


def extract_transcript(response: dict[str, Any]) -> str | None:
    """Pull the transcript text out of the gateway's response envelope.

    Returns ``None`` (never an empty/fabricated string) when the response
    carries an ``"error"`` key -- the caller renders that as the
    genuine-error (or backend-unavailable) state instead of a blank
    transcript.
    """
    if not isinstance(response, dict) or response.get("error"):
        return None
    text = response.get("text")
    return text if isinstance(text, str) else None


class VoicePanel(QWidget):
    """Desktop mic-to-text dictation, mirroring the webui's honest-state
    dictation control against the same backend."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.gateway = GatewayClient()
        self._recording = False
        self._output_path: Path | None = None
        self._capture_session: QMediaCaptureSession | None = None
        self._audio_input: QAudioInput | None = None
        self._recorder: QMediaRecorder | None = None
        self.initialize_ui()
        self._check_device()

    def initialize_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("🎙️ Voice Dictation")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Record a clip and transcribe it through the SAME governed audio-transcriber "
            "sidecar the web dictation control uses. Speech synthesis / playback is not "
            "implemented here -- no backend route exists for it yet."
        )
        subtitle.setStyleSheet("color: #8A8A93; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        row = QHBoxLayout()
        self.status_lbl = QLabel("Checking microphone…")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        row.addWidget(self.status_lbl, 1)
        self.btn_record = QPushButton("🎙️ Start Recording")
        self.btn_record.clicked.connect(self._toggle_recording)
        row.addWidget(self.btn_record)
        layout.addLayout(row)

        self.transcript_box = QTextEdit()
        self.transcript_box.setReadOnly(True)
        self.transcript_box.setPlaceholderText(
            "Transcript appears here after you stop recording…"
        )
        self.transcript_box.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
            "border-radius: 6px; padding: 10px;"
        )
        layout.addWidget(self.transcript_box, 1)

    # --- Device / capture lifecycle -------------------------------------- #

    def _check_device(self) -> None:
        if not QMediaDevices.audioInputs():
            self.status_lbl.setText("❌ No microphone device found on this system.")
            self.btn_record.setEnabled(False)
            return
        self.status_lbl.setText("Ready to record.")

    def _toggle_recording(self) -> None:
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        if not QMediaDevices.audioInputs():
            self.status_lbl.setText("❌ No microphone device found on this system.")
            self.btn_record.setEnabled(False)
            return

        fd, path = tempfile.mkstemp(
            prefix="geniusbot-voice-", suffix=".wav", dir="/var/tmp"
        )
        os.close(fd)
        self._output_path = Path(path)

        self._audio_input = QAudioInput()
        self._capture_session = QMediaCaptureSession()
        self._capture_session.setAudioInput(self._audio_input)
        self._recorder = QMediaRecorder()
        media_format = QMediaFormat()
        media_format.setFileFormat(QMediaFormat.FileFormat.Wave)
        self._recorder.setMediaFormat(media_format)
        self._recorder.setOutputLocation(QUrl.fromLocalFile(str(self._output_path)))
        self._capture_session.setRecorder(self._recorder)
        self._recorder.errorOccurred.connect(self._on_recorder_error)

        self._recorder.record()
        self._recording = True
        self.btn_record.setText("⏹ Stop Recording")
        self.status_lbl.setText("● Recording…")

    def _on_recorder_error(
        self, error: QMediaRecorder.Error, error_string: str
    ) -> None:
        self._recording = False
        self.btn_record.setText("🎙️ Start Recording")
        self.status_lbl.setText(f"❌ {status_for_recorder_error(error)}")

    def _stop_recording(self) -> None:
        self._recording = False
        self.btn_record.setText("🎙️ Start Recording")
        self.status_lbl.setText("Transcribing…")
        self.btn_record.setEnabled(False)
        if self._recorder is not None:
            self._recorder.stop()
        self._transcribe_output()

    # --- Transcription ----------------------------------------------------#

    def _transcribe_output(self) -> None:
        path = self._output_path
        if path is None or not path.exists():
            self.status_lbl.setText("❌ Recording failed unexpectedly.")
            self.btn_record.setEnabled(True)
            return
        data = path.read_bytes()
        path.unlink(missing_ok=True)

        async def runner(progress_cb=None):
            return await self.gateway.transcribe_voice(data, content_type="audio/wav")

        self.worker.run_agent_task(
            runner, on_finished=self._on_transcribed, on_error=self._on_error
        )

    def _on_error(self, message: str) -> None:
        self.btn_record.setEnabled(True)
        self.status_lbl.setText(f"❌ Transcription failed: {message}")

    def _on_transcribed(self, data: dict[str, Any]) -> None:
        self.btn_record.setEnabled(True)
        if not isinstance(data, dict):
            self._on_error("unexpected response")
            return
        if data.get("unavailable"):
            self.status_lbl.setText(
                "❌ Voice transcription is not enabled on this server yet."
            )
            return
        transcript = extract_transcript(data)
        if transcript is None:
            self.status_lbl.setText(f"❌ {data.get('error', 'Transcription failed.')}")
            return
        self.status_lbl.setText("✅ Transcribed.")
        if transcript:
            existing = self.transcript_box.toPlainText()
            self.transcript_box.setPlainText(
                f"{existing}\n{transcript}".strip() if existing else transcript
            )
