#!/usr/bin/env python3
"""CONCEPT:ECO-4.41 — Usage & Cost Cockpit.

Surfaces the agent-utilities observability plane (/api/observability/*) in the
desktop cockpit: usage/cost KPIs, cost-by-model, tool/skill/db-call metrics, a
day×hour activity heatmap, a top-sessions browser, and Langfuse trace links —
across every ingested agent + our own runtime telemetry. All gateway access
goes through the shared SDK via the geniusbot facade (ECO-4.37); network runs
off the UI thread through the AgentBridgeWorker.
"""

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BORDER_COLOR
from geniusbot.services.gateway_client import GatewayClient

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _fmt_usd(n) -> str:
    try:
        return f"${float(n or 0):.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def _fmt_num(n) -> str:
    n = int(n or 0)
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def _metric_card(title: str, value: str, color: str = "#7C4DFF") -> QWidget:
    """A compact KPI card (mirrors telemetry_dashboard.create_metric_card)."""
    card = QWidget()
    card.setStyleSheet(
        f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
        "border-radius: 8px;"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 10, 14, 10)
    val = QLabel(value)
    val.setObjectName("value")
    val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
    cap = QLabel(title)
    cap.setStyleSheet("color: #8A8A93; font-size: 11px;")
    lay.addWidget(val)
    lay.addWidget(cap)
    return card


class UsageCockpitPanel(QWidget):
    """Operator view of usage, cost, and call metrics across all agents."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.gateway = GatewayClient()
        self._cards: dict[str, QLabel] = {}
        self.initialize_ui()
        self.refresh()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("💰 Usage & Cost")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Token usage, cost, and tool/skill/database-call metrics across every "
            "agent and our own runtime — assimilated agentsview (ECO-4.41)."
        )
        subtitle.setStyleSheet("color: #8A8A93; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        header_row = QHBoxLayout()
        self.status_lbl = QLabel("Loading usage…")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        header_row.addWidget(self.status_lbl)
        header_row.addStretch()
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh)
        header_row.addWidget(self.btn_refresh)
        layout.addLayout(header_row)

        # --- KPI cards --------------------------------------------------- #
        kpi_row = QGridLayout()
        for col, (key, label) in enumerate(
            [("cost", "Total cost"), ("tokens", "Tokens (in/out)"),
             ("cache", "Cache hit"), ("sessions", "Sessions")]
        ):
            card = _metric_card(label, "—")
            self._cards[key] = card.findChild(QLabel, "value")
            kpi_row.addWidget(card, 0, col)
        layout.addLayout(kpi_row)

        # --- Cost by model ----------------------------------------------- #
        layout.addWidget(self._section("Cost by model"))
        self.model_table = self._make_table(["Model", "Sessions", "Tokens", "Cost"])
        layout.addWidget(self.model_table)

        # --- Tool / skill / db calls ------------------------------------- #
        layout.addWidget(self._section("Tool, skill & database calls"))
        self.tool_table = self._make_table(["Tool/Skill", "Category", "Calls", "Success"])
        layout.addWidget(self.tool_table)

        # --- Activity heatmap -------------------------------------------- #
        layout.addWidget(self._section("Activity (day × hour)"))
        self.heatmap = QLabel("")
        self.heatmap.setStyleSheet(
            "font-family: monospace; color: #B8B8C0; font-size: 12px;"
        )
        layout.addWidget(self.heatmap)

        # --- Top sessions ------------------------------------------------ #
        layout.addWidget(self._section("Top sessions by cost"))
        self.session_table = self._make_table(
            ["Project", "Agent", "Msgs", "Cost", "Grade"]
        )
        layout.addWidget(self.session_table)

        # --- Langfuse traces (shown only when enabled) ------------------- #
        self.traces_lbl = QLabel("")
        self.traces_lbl.setStyleSheet("color: #8A8A93; font-size: 11px;")
        self.traces_lbl.setWordWrap(True)
        layout.addWidget(self.traces_lbl)

    def _section(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #F5F5F7;")
        return lbl

    def _make_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # type: ignore[attr-defined]  # PySide6 QHeaderView.Stretch enum (incomplete stubs)
        table.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; "
            "border-radius: 6px;"
        )
        table.verticalHeader().setVisible(False)
        return table

    # --- Data flow ------------------------------------------------------- #

    def refresh(self):
        """Fetch all usage data off the UI thread, then repaint."""
        self.status_lbl.setText("Refreshing…")

        async def fetch():
            return {
                "summary": await self.gateway.fetch_usage_summary(),
                "by_model": await self.gateway.fetch_usage_by_model(),
                "tools": await self.gateway.fetch_usage_tools(),
                "activity": await self.gateway.fetch_usage_activity(),
                "sessions": await self.gateway.fetch_usage_sessions(limit=15),
                "traces": await self.gateway.fetch_usage_traces(),
            }

        self.worker.run_agent_task(
            fetch, on_finished=self._on_loaded, on_error=self._on_error
        )

    def _on_error(self, message: str):
        self.status_lbl.setText(f"❌ Gateway offline: {message}")

    def _on_loaded(self, data: dict):
        summary = data.get("summary") or {}
        totals = summary.get("totals", {})
        self._cards["cost"].setText(_fmt_usd(totals.get("cost_usd", 0)))
        self._cards["tokens"].setText(
            f"{_fmt_num(totals.get('input_tokens', 0))}/"
            f"{_fmt_num(totals.get('output_tokens', 0))}"
        )
        self._cards["cache"].setText(
            f"{round(summary.get('cache_hit_rate', 0) * 100)}%"
        )
        self._cards["sessions"].setText(_fmt_num(summary.get("session_count", 0)))

        self._fill_models(data.get("by_model") or [])
        self._fill_tools(data.get("tools") or [])
        self._fill_heatmap(data.get("activity") or [])
        self._fill_sessions(data.get("sessions") or [])
        self._fill_traces(data.get("traces") or {})
        self.status_lbl.setText(
            f"{summary.get('session_count', 0)} sessions · "
            f"{_fmt_usd(totals.get('cost_usd', 0))} total"
        )

    def _fill_models(self, rows: list):
        self.model_table.setRowCount(len(rows[:20]))
        for r, row in enumerate(rows[:20]):
            tok = (row.get("input_tokens", 0) or 0) + (row.get("output_tokens", 0) or 0)
            for c, val in enumerate(
                [row.get("key", "?"), str(row.get("session_count", 0)),
                 _fmt_num(tok), _fmt_usd(row.get("cost_usd", 0))]
            ):
                self.model_table.setItem(r, c, QTableWidgetItem(val))

    def _fill_tools(self, rows: list):
        self.tool_table.setRowCount(len(rows[:20]))
        for r, row in enumerate(rows[:20]):
            for c, val in enumerate(
                [row.get("name", "?"), row.get("category", "other"),
                 str(row.get("calls", 0)),
                 f"{round(row.get('success_rate', 0) * 100)}%"]
            ):
                self.tool_table.setItem(r, c, QTableWidgetItem(val))

    def _fill_heatmap(self, cells: list):
        blocks = " ▁▂▃▄▅▆▇█"
        grid = {(c.get("day_of_week"), c.get("hour")): c.get("sessions", 0) for c in cells}
        mx = max([v for v in grid.values()], default=1) or 1
        lines = []
        for di, day in enumerate(_DAYS):
            row = []
            for h in range(24):
                v = grid.get((di, h), 0)
                idx = 0 if not v else min(8, 1 + int(v / mx * 7))
                row.append(blocks[idx])
            lines.append(f"{day} {''.join(row)}")
        self.heatmap.setText("\n".join(lines))

    def _fill_sessions(self, rows: list):
        self.session_table.setRowCount(len(rows[:15]))
        for r, row in enumerate(rows[:15]):
            for c, val in enumerate(
                [(row.get("project") or "—")[:40], row.get("agent", "?"),
                 str(row.get("message_count", 0)), _fmt_usd(row.get("cost_usd", 0)),
                 row.get("health_grade") or ""]
            ):
                self.session_table.setItem(r, c, QTableWidgetItem(val))

    def _fill_traces(self, traces: dict):
        if not traces.get("enabled"):
            self.traces_lbl.setText("")
            return
        items = traces.get("traces", [])[:8]
        host = traces.get("host", "")
        lines = [f"Langfuse ({host}):"] + [
            f"  {t.get('session_id', '')[:16]} → {t.get('url', '')}" for t in items
        ]
        self.traces_lbl.setText("\n".join(lines))
