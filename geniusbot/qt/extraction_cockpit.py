#!/usr/bin/env python3
"""Document → knowledge-graph extraction cockpit (CONCEPT:AU-ECO.connector.git-task-resolver).

Paste text or a URL, watch facts stream live onto a native force-directed graph,
click an edge for its full fact card (confidence / evidence / tags / source),
and export JSONL — the knowledge-graph-extractor experience on the Qt cockpit,
backed by the real /api/enhanced/extract/* gateway (not mock data).
"""

from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.force_graph import ForceGraphWidget


class ExtractionCockpitPanel(QWidget):
    """Live document→KG extraction with a force-directed graph + edge cards."""

    def __init__(self, worker, gateway=None, parent=None):
        super().__init__(parent)
        self.worker = worker
        # the gateway facade (injectable for tests); lazy default
        self._gateway = gateway
        self._job_id: str | None = None
        self._kept = 0
        self._dupes = 0
        self.initialize_ui()

    @property
    def gateway(self):
        if self._gateway is None:
            from geniusbot.services.gateway_client import GatewayClient

            self._gateway = GatewayClient()
        return self._gateway

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("🧬 Knowledge Graph Extraction")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #7C4DFF;")
        layout.addWidget(title)

        # input row
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("Paste document text…")
        self.text_input.setMaximumHeight(90)
        layout.addWidget(self.text_input)

        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("…or a URL (readability)")
        url_row.addWidget(self.url_input)
        self.btn_extract = QPushButton("Extract")
        self.btn_extract.clicked.connect(self.run_extraction)
        url_row.addWidget(self.btn_extract)
        self.btn_export = QPushButton("JSONL")
        self.btn_export.clicked.connect(self.export_jsonl)
        self.btn_export.setEnabled(False)
        url_row.addWidget(self.btn_export)
        layout.addLayout(url_row)

        self.status_lbl = QLabel("idle")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        # graph + edge card
        splitter = QSplitter(Qt.Horizontal)
        self.graph = ForceGraphWidget()
        self.graph.edge_selected.connect(self.show_fact_card)
        splitter.addWidget(self.graph)

        self.card = QTextEdit()
        self.card.setReadOnly(True)
        self.card.setMaximumWidth(320)
        self.card.setHtml(
            "<p style='color:#8A8A93;'>Hover or click an edge to see its fact.</p>"
        )
        splitter.addWidget(self.card)
        splitter.setSizes([700, 320])
        layout.addWidget(splitter, 1)

    # ------------------------------------------------------------------ #
    # actions
    # ------------------------------------------------------------------ #

    def run_extraction(self):
        text = self.text_input.toPlainText().strip()
        url = self.url_input.text().strip()
        if not text and not url:
            self.status_lbl.setText("paste text or enter a URL first")
            return
        self.graph.clear_graph()
        self._kept = 0
        self._dupes = 0
        self.btn_extract.setEnabled(False)
        self.btn_extract.setText("Extracting…")
        self.status_lbl.setText("submitting…")

        async def runner(progress_cb=None):
            return await self.gateway.submit_and_stream_extraction(
                text=text, url=url, progress_cb=progress_cb
            )

        self.worker.run_agent_task(
            runner,
            on_finished=self._on_done,
            on_error=self._on_error,
            on_progress=self._on_event,
        )

    def _on_event(self, raw: str):
        """Render one streamed event live (runs on the UI thread via signal)."""
        try:
            ev = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return
        etype = ev.get("type")
        if etype == "fact":
            fact = ev.get("fact", {})
            if ev.get("is_duplicate"):
                self._dupes += 1
            else:
                self._kept += 1
                self.graph.add_fact(fact)
            self.status_lbl.setText(
                f"streaming… {self._kept} facts"
                + (f" (+{self._dupes} dup)" if self._dupes else "")
            )
        elif etype == "round_start":
            self.status_lbl.setText(f"round {ev.get('round')}…")
        elif etype == "job_done":
            self.status_lbl.setText("done")

    def _on_done(self, result: dict):
        self.btn_extract.setEnabled(True)
        self.btn_extract.setText("Extract")
        if isinstance(result, dict):
            self._job_id = result.get("job_id")
            self.btn_export.setEnabled(bool(self._job_id))
            if result.get("status") in ("unavailable", "error"):
                self.status_lbl.setText(
                    f"unavailable: {result.get('message', 'engine cold?')}"
                )
            else:
                self.status_lbl.setText(f"done — {self._kept} facts")

    def _on_error(self, err: str):
        self.btn_extract.setEnabled(True)
        self.btn_extract.setText("Extract")
        self.status_lbl.setText(f"failed: {err}")

    def show_fact_card(self, fact: dict):
        """Render the clicked edge's fact as a card."""
        tags = " ".join(
            f"<span style='color:#00E5FF;'>#{t}</span>"
            for t in (fact.get("tags") or [])
        )
        dup = (
            "<span style='color:#FF1744;'>[duplicate]</span>"
            if fact.get("is_duplicate")
            else ""
        )
        html = (
            f"<h3 style='color:#E4E4E7;'>{_esc(fact.get('title') or '')}</h3>"
            f"<p style='font-family:monospace;'>"
            f"<span style='color:#42A5F5;'>{_esc(fact.get('subject', ''))}</span> → "
            f"<span style='color:#AB47BC;'>{_esc(fact.get('predicate', ''))}</span> → "
            f"<span style='color:#66BB6A;'>{_esc(fact.get('object', ''))}</span></p>"
            f"<p style='color:#B0B0B8;'>{_esc(fact.get('description', ''))}</p>"
            f"<p>conf {fact.get('confidence', '–')}% {dup}</p>"
            f"<p>{tags}</p>"
        )
        if fact.get("evidence_span"):
            html += f"<blockquote style='color:#8A8A93;'>“{_esc(fact['evidence_span'])}”</blockquote>"
        if fact.get("source_file"):
            html += f"<p style='color:#8A8A93;'>📄 {_esc(fact['source_file'])}</p>"
        self.card.setHtml(html)

    def export_jsonl(self):
        if not self._job_id:
            return
        job_id = self._job_id

        async def runner(progress_cb=None):
            return await self.gateway.fetch_extraction_jsonl(job_id)

        def on_done(text):
            self.card.setHtml(
                f"<pre style='color:#E4E4E7; font-size:10px;'>{_esc((text or '').strip())}</pre>"
            )

        self.worker.run_agent_task(runner, on_finished=on_done, on_error=self._on_error)


def _esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
