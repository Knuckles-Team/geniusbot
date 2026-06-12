#!/usr/bin/env python3
"""CONCEPT:GBOT-6.6 — Fleet Supervisory Cockpit.

Surfaces the agent-utilities fleet autonomy control plane (OS-5.10 / OS-5.15 /
OS-5.24) in the desktop cockpit: worker/placement topology and the **ActionPolicy
approval inbox** — the human decision point for every autonomous mutating action.
All gateway access goes through the shared surface SDK via the geniusbot facade
(:class:`geniusbot.services.gateway_client.GatewayClient`, ECO-4.37); network calls
run off the UI thread through the :class:`AgentBridgeWorker`.
"""

from PySide6.QtWidgets import (
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


class FleetCockpitPanel(QWidget):
    """Operator view of fleet topology + pending ActionPolicy approvals."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker
        self.gateway = GatewayClient()
        self._approvals: list[dict] = []
        self.initialize_ui()
        self.refresh()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("🛰️ Fleet Supervisor")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Worker placement topology and the ActionPolicy approval inbox — "
            "grant or hold every autonomous mutating action (OS-5.24)."
        )
        subtitle.setStyleSheet("color: #8A8A93; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        header_row = QHBoxLayout()
        self.status_lbl = QLabel("Loading fleet state…")
        self.status_lbl.setStyleSheet("color: #8A8A93; font-size: 12px;")
        header_row.addWidget(self.status_lbl)
        header_row.addStretch()
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.clicked.connect(self.refresh)
        header_row.addWidget(self.btn_refresh)
        layout.addLayout(header_row)

        # --- Topology ---------------------------------------------------- #
        topo_lbl = QLabel("Topology")
        topo_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #F5F5F7;")
        layout.addWidget(topo_lbl)
        self.topo_table = QTableWidget(0, 2)
        self.topo_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.topo_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.topo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.topo_table.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px;"
        )
        layout.addWidget(self.topo_table)

        # --- Approval inbox ---------------------------------------------- #
        appr_lbl = QLabel("Pending approvals")
        appr_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #F5F5F7;")
        layout.addWidget(appr_lbl)
        self.appr_table = QTableWidget(0, 4)
        self.appr_table.setHorizontalHeaderLabels(
            ["ID", "Action", "Target", "Decision"]
        )
        self.appr_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.appr_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.appr_table.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px;"
        )
        layout.addWidget(self.appr_table)

    # --- Data flow ------------------------------------------------------- #

    def refresh(self):
        """Fetch topology + approvals off the UI thread, then repaint."""
        self.status_lbl.setText("Refreshing…")

        async def fetch():
            topology = await self.gateway.fetch_fleet_topology()
            approvals = await self.gateway.fetch_fleet_approvals()
            return {"topology": topology, "approvals": approvals}

        self.worker.run_agent_task(
            fetch, on_finished=self._on_loaded, on_error=self._on_error
        )

    def _on_error(self, message: str):
        self.status_lbl.setText(f"❌ Gateway offline: {message}")

    def _on_loaded(self, data: dict):
        topology = data.get("topology") or {}
        approvals = data.get("approvals") or []
        self._render_topology(topology)
        self._render_approvals(approvals)
        self.status_lbl.setText(
            f"{len(approvals)} pending approval(s) · topology: {len(topology)} field(s)"
        )

    def _render_topology(self, topology: dict):
        # Flatten one level so worker lists and scalar fields both render.
        rows = []
        for key, value in topology.items():
            if isinstance(value, list):
                rows.append((key, f"{len(value)} item(s)"))
                for i, item in enumerate(value):
                    rows.append((f"  {key}[{i}]", str(item)))
            else:
                rows.append((key, str(value)))
        self.topo_table.setRowCount(len(rows))
        for r, (k, v) in enumerate(rows):
            self.topo_table.setItem(r, 0, QTableWidgetItem(k))
            self.topo_table.setItem(r, 1, QTableWidgetItem(v))

    def _render_approvals(self, approvals: list):
        self._approvals = approvals
        self.appr_table.setRowCount(len(approvals))
        for r, appr in enumerate(approvals):
            approval_id = str(appr.get("id", appr.get("approval_id", r)))
            self.appr_table.setItem(r, 0, QTableWidgetItem(approval_id))
            self.appr_table.setItem(
                r, 1, QTableWidgetItem(str(appr.get("action", "—")))
            )
            self.appr_table.setItem(
                r, 2, QTableWidgetItem(str(appr.get("target", appr.get("subject", "—"))))
            )
            grant_btn = QPushButton("✅ Grant")
            grant_btn.clicked.connect(
                lambda _checked=False, aid=approval_id: self._grant(aid)
            )
            self.appr_table.setCellWidget(r, 3, grant_btn)

    def _grant(self, approval_id: str):
        self.status_lbl.setText(f"Granting {approval_id}…")

        async def do_grant():
            result = await self.gateway.grant_approval(approval_id)
            return {"granted": approval_id, "result": result}

        self.worker.run_agent_task(
            do_grant,
            on_finished=lambda _data: self.refresh(),
            on_error=self._on_error,
        )
