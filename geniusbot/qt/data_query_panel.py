#!/usr/bin/env python3
"""CONCEPT:GBOT-6.8 — Ask-Data / NL→Query Cockpit.

Surfaces the epistemic-graph natural-language query surface in the desktop
cockpit: the user asks a data question in plain English and gets a synthesized
answer plus the auditable query the engine generated, the result rows, and
citations. Two modes map onto the two backend routes:

  * **Ask Data** (``/api/graph/ask-data``, backend KG-2.308) — a DB-GPT-style
    multi-step data-analysis agent that schema-links, generates a read-only
    query, executes it, self-corrects on error, and synthesizes an answer.
  * **NL → Query** (``/api/graph/nl-query``, backend KG-2.305) — a single-shot
    NL→UQL/Cypher/SQL/SPARQL translation, optionally preview-only.

All gateway access goes through the shared SDK via the geniusbot facade
(ECO-4.37); network runs off the UI thread through the AgentBridgeWorker.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BORDER_COLOR
from geniusbot.services.gateway_client import GatewayClient


class DataQueryPanel(QWidget):
    """Ask the Knowledge Graph a data question in natural language."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.gateway = GatewayClient()
        self.initialize_ui()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("🔎 Ask Data")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Ask the Knowledge Graph a question in plain English. The engine "
            "generates an auditable read-only query (UQL/Cypher/SQL/SPARQL), runs "
            "it, and synthesizes an answer with citations (backend KG-2.305/2.308)."
        )
        subtitle.setStyleSheet("color: #8A8A93; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # --- Query input row --------------------------------------------- #
        input_row = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItems(["Ask Data (multi-step)", "NL → Query (single-shot)"])
        self.mode.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 8px;"
        )
        input_row.addWidget(self.mode)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText(
            "e.g. Which agents executed the most tasks this week?"
        )
        self.question_input.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
            "border-radius: 6px; padding: 10px; font-size: 12px;"
        )
        self.question_input.returnPressed.connect(self.run_query)
        input_row.addWidget(self.question_input, 1)

        self.btn_ask = QPushButton("Ask")
        self.btn_ask.setStyleSheet(
            "background-color: #7C4DFF; color: white; font-weight: bold; padding: 10px 16px; border-radius: 6px;"
        )
        self.btn_ask.clicked.connect(self.run_query)
        input_row.addWidget(self.btn_ask)
        layout.addLayout(input_row)

        self.status_lbl = QLabel("Ready.")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        # --- Results splitter (answer/query above, rows below) ----------- #
        splitter = QSplitter(Qt.Vertical)  # type: ignore[attr-defined]
        layout.addWidget(splitter, 1)

        self.answer_view = QTextEdit()
        self.answer_view.setReadOnly(True)
        self.answer_view.setStyleSheet(
            "background-color: #0b0b0d; border: 1px solid #1E1E22; border-radius: 6px; padding: 12px; font-size: 12px;"
        )
        self.answer_view.setHtml(
            "<span style='color:#8A8A93;'>The synthesized answer, the generated "
            "query, and citations will appear here.</span>"
        )
        splitter.addWidget(self.answer_view)

        self.rows_table = QTableWidget(0, 0)
        self.rows_table.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px;"
        )
        self.rows_table.verticalHeader().setVisible(False)
        splitter.addWidget(self.rows_table)
        splitter.setSizes([260, 300])

    # --- Data flow ------------------------------------------------------- #

    def run_query(self):
        question = self.question_input.text().strip()
        if not question:
            return
        self.btn_ask.setEnabled(False)
        self.status_lbl.setText("Querying the Knowledge Graph…")
        single_shot = self.mode.currentIndex() == 1

        async def runner(progress_cb=None):
            if single_shot:
                return await self.gateway.nl_query(question)
            return await self.gateway.ask_data(question)

        self.worker.run_agent_task(
            runner, on_finished=self._on_answer, on_error=self._on_error
        )

    def _on_error(self, message: str):
        self.btn_ask.setEnabled(True)
        self.status_lbl.setText("❌ Query failed.")
        self.answer_view.setHtml(
            f"<span style='color:#FF1744;'>Query failed:<br>{message}</span>"
        )

    def _on_answer(self, data: dict):
        self.btn_ask.setEnabled(True)
        if data.get("error"):
            self._on_error(str(data["error"]))
            return
        self.status_lbl.setText("Done.")

        answer = data.get("answer") or data.get("result") or "(no answer synthesized)"
        query = data.get("query") or data.get("generated_query") or ""
        citations = data.get("citations") or []

        html = [f"<div style='color:#E4E4E7;'>{answer}</div>"]
        if query:
            html.append(
                "<br><b style='color:#00E5FF;'>Generated query</b>"
                f"<pre style='color:#00E676; white-space:pre-wrap;'>{query}</pre>"
            )
        if citations:
            cites = "<br>".join(f"• {c}" for c in citations)
            html.append(
                f"<br><b style='color:#FFAB40;'>Citations</b><br><span style='color:#8A8A93;'>{cites}</span>"
            )
        self.answer_view.setHtml("".join(html))

        rows = data.get("rows") or data.get("results") or []
        self._render_rows(rows)

    def _render_rows(self, rows: list):
        self.rows_table.clear()
        if not rows:
            self.rows_table.setRowCount(0)
            self.rows_table.setColumnCount(0)
            return
        # Rows may be list[dict] (column-keyed) or list[list] (positional).
        if isinstance(rows[0], dict):
            columns = list(rows[0].keys())
            self.rows_table.setColumnCount(len(columns))
            self.rows_table.setHorizontalHeaderLabels([str(c) for c in columns])
            self.rows_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, col in enumerate(columns):
                    self.rows_table.setItem(
                        r, c, QTableWidgetItem(str(row.get(col, "")))
                    )
        else:
            width = max(len(r) for r in rows)
            self.rows_table.setColumnCount(width)
            self.rows_table.setHorizontalHeaderLabels([f"col{i}" for i in range(width)])
            self.rows_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.rows_table.setItem(r, c, QTableWidgetItem(str(val)))
        self.rows_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore[attr-defined]
