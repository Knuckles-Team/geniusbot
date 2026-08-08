#!/usr/bin/env python3
"""CONCEPT:GB-GBOT.cockpit.metrics-status-cockpit — Engine Metrics & Status Cockpit.

Surfaces the epistemic-graph engine observability + KV-cache surface in the
desktop cockpit:

  * **KV-cache stats** (``/api/graph/kvcache`` action=stats, backend KG-2.310) —
    occupancy + dedup counters of the shared content-addressed KV-cache, shown
    as KPI cards and refreshed on demand.
  * **PromQL** (``/api/graph/promql``, backend KG-2.310) — run an instant PromQL
    expression against the engine's metrics and render the result series.

All gateway access goes through the shared SDK via the geniusbot facade
(ECO-4.37); network runs off the UI thread through the AgentBridgeWorker.
"""

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BORDER_COLOR
from geniusbot.services.gateway_client import GatewayClient


def _metric_card(title: str) -> QWidget:
    """A compact KPI card exposing its value label as child ``value``."""
    card = QWidget()
    card.setStyleSheet(
        f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 8px;"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 10, 14, 10)
    val = QLabel("—")
    val.setObjectName("value")
    val.setStyleSheet("font-size: 22px; font-weight: bold; color: #00E5FF;")
    cap = QLabel(title)
    cap.setStyleSheet("color: #8A8A93; font-size: 11px;")
    lay.addWidget(val)
    lay.addWidget(cap)
    return card


class MetricsPanel(QWidget):
    """Operator view of engine metrics (PromQL) and shared KV-cache stats."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.gateway = GatewayClient()
        self._cards: dict[str, QLabel] = {}
        self.initialize_ui()
        self.refresh_stats()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("📊 Engine Metrics & Status")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Live engine observability: query the metrics with PromQL and watch "
            "the shared content-addressed KV-cache occupancy (backend KG-2.310)."
        )
        subtitle.setStyleSheet("color: #8A8A93; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # --- KV-cache KPI cards ------------------------------------------ #
        header_row = QHBoxLayout()
        self.status_lbl = QLabel("Loading KV-cache stats…")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        header_row.addWidget(self.status_lbl)
        header_row.addStretch()
        self.btn_refresh = QPushButton("🔄 Refresh Stats")
        self.btn_refresh.clicked.connect(self.refresh_stats)
        header_row.addWidget(self.btn_refresh)
        layout.addLayout(header_row)

        kpi_row = QGridLayout()
        for col, (key, label) in enumerate(
            [
                ("entries", "Cache entries"),
                ("bytes", "Bytes stored"),
                ("hits", "Hits"),
                ("dedup", "Dedup hits"),
            ]
        ):
            card = _metric_card(label)
            self._cards[key] = card.findChild(QLabel, "value")
            kpi_row.addWidget(card, 0, col)
        layout.addLayout(kpi_row)

        # --- PromQL query row -------------------------------------------- #
        promql_lbl = QLabel("PromQL query")
        promql_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #F5F5F7;")
        layout.addWidget(promql_lbl)

        input_row = QHBoxLayout()
        self.promql_input = QLineEdit()
        self.promql_input.setPlaceholderText("e.g. rate(graph_queries_total[5m])")
        self.promql_input.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
            "border-radius: 6px; padding: 10px; font-family: monospace; font-size: 12px;"
        )
        self.promql_input.returnPressed.connect(self.run_promql)
        input_row.addWidget(self.promql_input, 1)

        self.btn_run = QPushButton("Run")
        self.btn_run.setStyleSheet(
            "background-color: #7C4DFF; color: white; font-weight: bold; padding: 10px 16px; border-radius: 6px;"
        )
        self.btn_run.clicked.connect(self.run_promql)
        input_row.addWidget(self.btn_run)
        layout.addLayout(input_row)

        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Series", "Value"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # type: ignore[attr-defined]
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px;"
        )
        layout.addWidget(self.result_table, 1)

    # --- Data flow ------------------------------------------------------- #

    def refresh_stats(self):
        self.status_lbl.setText("Refreshing KV-cache stats…")

        async def runner(progress_cb=None):
            return await self.gateway.kvcache_stats()

        self.worker.run_agent_task(
            runner, on_finished=self._on_stats, on_error=self._on_error
        )

    def _on_error(self, message: str):
        self.status_lbl.setText(f"❌ Gateway offline: {message}")

    def _on_stats(self, data: dict):
        if data.get("error"):
            self._on_error(str(data["error"]))
            return
        # Envelope shape: {"surface":"kvcache","action":"stats","result": {...}}
        result = data.get("result")
        stats = result if isinstance(result, dict) else data
        self.status_lbl.setText("KV-cache stats updated.")
        self._cards["entries"].setText(
            str(stats.get("entries", stats.get("count", "—")))
        )
        self._cards["bytes"].setText(
            str(stats.get("bytes", stats.get("bytes_stored", "—")))
        )
        self._cards["hits"].setText(str(stats.get("hits", "—")))
        self._cards["dedup"].setText(
            str(stats.get("dedup_hits", stats.get("dedup", "—")))
        )

    def run_promql(self):
        query = self.promql_input.text().strip()
        if not query:
            return
        self.btn_run.setEnabled(False)
        self.status_lbl.setText("Evaluating PromQL…")

        async def runner(progress_cb=None):
            return await self.gateway.promql(query)

        self.worker.run_agent_task(
            runner, on_finished=self._on_promql, on_error=self._on_promql_error
        )

    def _on_promql_error(self, message: str):
        self.btn_run.setEnabled(True)
        self.status_lbl.setText(f"❌ PromQL failed: {message}")

    def _on_promql(self, data: dict):
        self.btn_run.setEnabled(True)
        if data.get("error"):
            self._on_promql_error(str(data["error"]))
            return
        self.status_lbl.setText("PromQL evaluated.")
        series = self._extract_series(data)
        self.result_table.setRowCount(len(series))
        for r, (label, value) in enumerate(series):
            self.result_table.setItem(r, 0, QTableWidgetItem(label))
            self.result_table.setItem(r, 1, QTableWidgetItem(value))

    @staticmethod
    def _extract_series(data: dict) -> list[tuple[str, str]]:
        """Flatten a Prometheus-style result into (series-label, value) rows."""
        result = data.get("result", data)
        # Prometheus wire: {"data": {"result": [{"metric": {...}, "value": [ts, v]}]}}
        payload = result
        if isinstance(result, dict):
            payload = result.get("data", result)
            if isinstance(payload, dict):
                payload = payload.get("result", payload)
        rows: list[tuple[str, str]] = []
        if isinstance(payload, list):
            for item in payload:
                if not isinstance(item, dict):
                    rows.append(("", str(item)))
                    continue
                metric = item.get("metric", {})
                label = ", ".join(f"{k}={v}" for k, v in metric.items()) or "value"
                value = item.get("value") or item.get("values") or ""
                if isinstance(value, list) and len(value) == 2:
                    value = value[1]
                rows.append((label, str(value)))
        elif payload not in (None, ""):
            rows.append(("result", str(payload)))
        return rows
