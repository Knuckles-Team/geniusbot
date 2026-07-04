#!/usr/bin/env python3
"""CONCEPT:GB-GBOT.cockpit.federated-search-cockpit — Federated Search Cockpit.

Surfaces the epistemic-graph federated-search surface
(``/api/graph/federated-search``, backend KG-2.310) in the desktop cockpit: a
single natural-language / keyword query is fanned across every registered
external graph reference and the ranked results are rendered in a table. An
optional comma-separated ``references`` filter scopes the fan-out.

All gateway access goes through the shared SDK via the geniusbot facade
(ECO-4.37); network runs off the UI thread through the AgentBridgeWorker.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BORDER_COLOR
from geniusbot.services.gateway_client import GatewayClient


class FederatedSearchPanel(QWidget):
    """Search across every registered external graph in one query."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.gateway = GatewayClient()
        self.initialize_ui()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("🌐 Federated Search")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Fan one query across every registered external graph reference and "
            "rank the merged results (backend KG-2.310). Scope with an optional "
            "comma-separated list of reference ids."
        )
        subtitle.setStyleSheet("color: #8A8A93; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # --- Query row --------------------------------------------------- #
        input_row = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText(
            "e.g. payments service reliability incidents"
        )
        self.query_input.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
            "border-radius: 6px; padding: 10px; font-size: 12px;"
        )
        self.query_input.returnPressed.connect(self.run_search)
        input_row.addWidget(self.query_input, 1)

        self.top_k = QSpinBox()
        self.top_k.setRange(1, 100)
        self.top_k.setValue(10)
        self.top_k.setToolTip("Max results (top_k)")
        self.top_k.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 8px;"
        )
        input_row.addWidget(self.top_k)

        self.btn_search = QPushButton("Search")
        self.btn_search.setStyleSheet(
            "background-color: #7C4DFF; color: white; font-weight: bold; padding: 10px 16px; border-radius: 6px;"
        )
        self.btn_search.clicked.connect(self.run_search)
        input_row.addWidget(self.btn_search)
        layout.addLayout(input_row)

        self.refs_input = QLineEdit()
        self.refs_input.setPlaceholderText(
            "Optional: comma-separated external graph reference ids (empty ⇒ all)"
        )
        self.refs_input.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
            "border-radius: 6px; padding: 8px; font-size: 11px;"
        )
        layout.addWidget(self.refs_input)

        self.status_lbl = QLabel("Ready.")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        # --- Results table ----------------------------------------------- #
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Source", "Result", "Score"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # type: ignore[attr-defined]
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px;"
        )
        layout.addWidget(self.results_table, 1)

    # --- Data flow ------------------------------------------------------- #

    def run_search(self):
        query = self.query_input.text().strip()
        if not query:
            return
        self.btn_search.setEnabled(False)
        self.status_lbl.setText("Searching across registered graphs…")
        top_k = self.top_k.value()
        references = self.refs_input.text().strip()

        async def runner(progress_cb=None):
            return await self.gateway.federated_search(
                query, top_k=top_k, references=references
            )

        self.worker.run_agent_task(
            runner, on_finished=self._on_results, on_error=self._on_error
        )

    def _on_error(self, message: str):
        self.btn_search.setEnabled(True)
        self.status_lbl.setText(f"❌ Search failed: {message}")

    def _on_results(self, data: dict):
        self.btn_search.setEnabled(True)
        if data.get("error"):
            self._on_error(str(data["error"]))
            return
        results = self._extract_results(data)
        self.status_lbl.setText(f"{len(results)} result(s).")
        self.results_table.setRowCount(len(results))
        for r, item in enumerate(results):
            self.results_table.setItem(r, 0, QTableWidgetItem(str(item["source"])))
            self.results_table.setItem(r, 1, QTableWidgetItem(str(item["text"])))
            self.results_table.setItem(r, 2, QTableWidgetItem(str(item["score"])))

    @staticmethod
    def _extract_results(data: dict) -> list[dict]:
        """Normalize the federated-search envelope into row dicts."""
        payload = data.get("result", data)
        if isinstance(payload, dict):
            payload = payload.get("results", payload.get("hits", []))
        rows: list[dict] = []
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    rows.append(
                        {
                            "source": item.get("reference")
                            or item.get("source")
                            or item.get("graph")
                            or "",
                            "text": item.get("text")
                            or item.get("title")
                            or item.get("name")
                            or item.get("id")
                            or item,
                            "score": item.get("score", item.get("rank", "")),
                        }
                    )
                else:
                    rows.append({"source": "", "text": item, "score": ""})
        return rows
