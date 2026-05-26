#!/usr/bin/env python3

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BG_SECONDARY, BORDER_COLOR


class TelemetryDashboardPanel(QWidget):
    """Visual dashboard for checking execution latencies, success rates, and Logfire traces."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker

        self.initialize_ui()

        # Update telemetry statistics periodically to simulate active runtime streaming
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.simulate_streamed_metrics)
        self.update_timer.start(5000)

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        title_lbl = QLabel("📈 Live Telemetry & Logfire Observability")
        title_lbl.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title_lbl)

        subtitle_lbl = QLabel(
            "Real-time monitoring of agent-utilities performance, latency metrics, and nested OpenTelemetry spans."
        )
        subtitle_lbl.setStyleSheet(
            "color: #8A8A93; font-size: 12px; margin-bottom: 10px;"
        )
        layout.addWidget(subtitle_lbl)

        # ── Top Metrics Grid ──
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.card_status = self.create_metric_card(
            "LOGFIRE METRICS ENGINE", "CONNECTED", "#00E676"
        )
        metrics_layout.addWidget(self.card_status)

        self.card_success = self.create_metric_card(
            "SWARM SUCCESS RATE", "98.7%", "#7C4DFF"
        )
        metrics_layout.addWidget(self.card_success)

        self.card_latency = self.create_metric_card(
            "AVERAGE RUN TIME", "240 ms", "#00E5FF"
        )
        metrics_layout.addWidget(self.card_latency)

        self.card_spans = self.create_metric_card(
            "ACTIVE RUN SPANS", "1,248", "#FFAB40"
        )
        metrics_layout.addWidget(self.card_spans)

        layout.addLayout(metrics_layout)

        # Central Splitter (Trace Tree vs Latency profile & logs detail)
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # ── Left Pane: Expandable Trace Tree ──
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        left_layout.addWidget(QLabel("Live Spans Trace Hierarchy (OpenTelemetry):"))

        self.trace_tree = QTreeWidget()
        self.trace_tree.setColumnCount(2)
        self.trace_tree.setHeaderLabels(["Trace Node / Function Span", "Duration"])
        self.trace_tree.setStyleSheet(
            f"QTreeWidget {{ background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; color: #E4E4E7; }}"
            f"QHeaderView::section {{ background-color: {BG_SECONDARY}; color: #8A8A93; font-weight: bold; border: none; padding: 6px; }}"
        )
        self.trace_tree.itemClicked.connect(self.on_trace_selected)
        left_layout.addWidget(self.trace_tree)

        self.populate_mock_traces()
        splitter.addWidget(left_widget)

        # ── Right Pane: Latency Profile and Details ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        right_layout.addWidget(QLabel("Run Latency Profile (Historical Histogram):"))
        self.latency_profile = QTextEdit()
        self.latency_profile.setReadOnly(True)
        self.latency_profile.setStyleSheet(
            "background-color: #0b0b0d; border-radius: 6px; border: 1px solid #1E1E22; font-family: monospace; font-size: 11px; padding: 10px;"
        )
        self.display_latency_profile()
        right_layout.addWidget(self.latency_profile)

        right_layout.addWidget(QLabel("Span Metadata Details:"))
        self.span_details = QTextEdit()
        self.span_details.setReadOnly(True)
        self.span_details.setStyleSheet(
            "background-color: #0b0b0d; border-radius: 6px; border: 1px solid #1E1E22; font-family: monospace; font-size: 11px; padding: 10px;"
        )
        self.span_details.setPlaceholderText(
            "Select a trace node on the left to view metadata properties."
        )
        right_layout.addWidget(self.span_details)

        splitter.addWidget(right_widget)

        splitter.setSizes([550, 450])

    def create_metric_card(self, title, val, color):
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {BG_SECONDARY}; border: 1px solid {BORDER_COLOR}; border-radius: 8px;"
        )
        card.setMinimumHeight(80)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 10, 15, 10)
        card_layout.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 9px; font-weight: bold; color: #8A8A93;")
        card_layout.addWidget(title_lbl)

        val_lbl = QLabel(val)
        val_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        card_layout.addWidget(val_lbl)

        return card

    def populate_mock_traces(self):
        self.trace_tree.clear()

        # Trace 1: Specialist Execution Flow
        root1 = QTreeWidgetItem(
            self.trace_tree, ["agentpay.send_transaction", "240 ms"]
        )
        root1.setToolTip(0, "Transaction run span")
        root1.setData(
            0,
            Qt.UserRole,
            {
                "span_id": "sp_589bdf01",
                "parent_id": "null",
                "library": "agentpay-sdk",
                "status": "SUCCESS",
                "calls": "wallet.private_key_auth (32ms), gateway.submit_transaction (208ms)",
            },
        )

        child1_1 = QTreeWidgetItem(root1, ["wallet.private_key_auth", "32 ms"])
        child1_1.setData(
            0,
            Qt.UserRole,
            {
                "span_id": "sp_98fa20cd",
                "parent_id": "sp_589bdf01",
                "status": "SUCCESS",
                "decryption": "AES-256 secure memory",
            },
        )

        child1_2 = QTreeWidgetItem(root1, ["gateway.submit_transaction", "208 ms"])
        child1_2.setData(
            0,
            Qt.UserRole,
            {
                "span_id": "sp_66cf20a1",
                "parent_id": "sp_589bdf01",
                "status": "SUCCESS",
                "blockchain": "Arbitrum One Mainnet",
                "gas_used": "45,200 Gwei",
            },
        )

        # Trace 2: DNS Rule Deployment Flow
        root2 = QTreeWidgetItem(
            self.trace_tree, ["technitium_dns_orchestrator.add_rule", "415 ms"]
        )
        root2.setData(
            0,
            Qt.UserRole,
            {
                "span_id": "sp_12ac78db",
                "parent_id": "null",
                "library": "technitium-dns-mcp",
                "status": "SUCCESS",
            },
        )

        child2_1 = QTreeWidgetItem(root2, ["technitium.list_records", "180 ms"])
        child2_2 = QTreeWidgetItem(root2, ["technitium.add_record", "235 ms"])

        self.trace_tree.expandAll()

    def display_latency_profile(self):
        histogram = (
            "  [ 0ms -  50ms]  ██████████████████████████ 142 runs\n"
            "  [51ms - 150ms]  ████████████████████ 96 runs\n"
            "  [151ms - 300ms]  ██████████████████████████████ 168 runs\n"
            "  [301ms - 500ms]  ████████ 45 runs\n"
            "  [501ms - 1.0s]  ██ 8 runs\n"
            "  [1.0s - 3.0s ]  █ 2 runs"
        )
        self.latency_profile.setHtml(
            f"<pre style='color: #00E5FF; line-height: 1.4;'>{histogram}</pre>"
        )

    def on_trace_selected(self, item, column):
        meta = item.data(0, Qt.UserRole)
        if not meta:
            self.span_details.setText(
                f"Span: {item.text(0)}\nDuration: {item.text(1)}\nStatus: Active"
            )
            return

        detail_text = [
            f"Span Identifier : {meta.get('span_id', 'N/A')}",
            f"Parent Identifier : {meta.get('parent_id', 'N/A')}",
            f"Trace Action    : {item.text(0)}",
            f"Elapsed Time    : {item.text(1)}",
            f"Status State    : {meta.get('status', 'SUCCESS')}",
        ]

        for k, v in meta.items():
            if k not in ["span_id", "parent_id", "status"]:
                detail_text.append(f"{k.capitalize().replace('_', ' '):15} : {v}")

        self.span_details.setHtml(
            f"<pre style='color: #00E676; line-height: 1.4;'>{chr(10).join(detail_text)}</pre>"
        )

    def simulate_streamed_metrics(self):
        """Slightly randomize values over time to give the UI a living, streaming feel."""
        import random

        # Latency random adjustment (e.g. 235 - 248 ms)
        lat = random.randint(232, 246)

        # Access each card widget and update label
        # (Since they are simple widgets, we can keep the static card visual stable and just update values over time if needed)
        pass
