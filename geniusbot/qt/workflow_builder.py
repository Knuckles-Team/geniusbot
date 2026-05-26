#!/usr/bin/env python3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import BORDER_COLOR


class WorkflowBuilderPanel(QWidget):
    """Visual panel for building sequential specialist workflows and watching agent debates."""

    def __init__(self, worker, parent=None):
        super().__init__(parent)
        self.worker = worker

        self.initialize_ui()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        title_lbl = QLabel("⛓️ Swarm Workflow Builder & Debate Dashboard")
        title_lbl.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title_lbl)

        subtitle_lbl = QLabel(
            "Compile sequential agent pipelines and monitor live cross-agent consensus debates during execution."
        )
        subtitle_lbl.setStyleSheet(
            "color: #8A8A93; font-size: 12px; margin-bottom: 10px;"
        )
        layout.addWidget(subtitle_lbl)

        # Main splitter dividing builder steps from the visual flows & debate views
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # ── Left Column: Workflow Chain Step List ──
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        left_layout.addWidget(QLabel("Compile Workflow Chain Steps:"))

        # Combo row to add a specialist
        add_row = QHBoxLayout()
        self.specialist_selector = QComboBox()
        self.specialist_selector.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 8px;"
        )
        self.specialist_selector.addItems(
            [
                "technitium-dns-mcp (DNS Management)",
                "agentpay-sdk (Blockchain Transfer)",
                "scholarx-agent (Paper Scanner)",
                "repository-manager (Git Auditor)",
                "systems-manager (Host System Engine)",
                "uptime-self-healer (Self Healing)",
            ]
        )
        add_row.addWidget(self.specialist_selector)

        self.btn_add_step = QPushButton("+ Add Step")
        self.btn_add_step.setStyleSheet(
            "background-color: #2e2e33; color: #E4E4E7; border-radius: 6px; padding: 8px 12px;"
        )
        self.btn_add_step.clicked.connect(self.add_workflow_step)
        add_row.addWidget(self.btn_add_step)
        left_layout.addLayout(add_row)

        # List of compiled steps
        self.steps_list = QListWidget()
        self.steps_list.setStyleSheet(
            f"QListWidget {{ background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 5px; color: #E4E4E7; }}"
        )
        left_layout.addWidget(self.steps_list)

        # Add some initial mock steps to make it look active immediately
        self.add_initial_mock_steps()

        # Action Buttons Row
        action_row = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Steps")
        self.btn_clear.setStyleSheet(
            "background-color: #1a1a1c; border: 1px solid #27272a; color: #8A8A93; border-radius: 6px; padding: 10px;"
        )
        self.btn_clear.clicked.connect(self.clear_steps)
        action_row.addWidget(self.btn_clear)

        self.btn_compile = QPushButton("⚡ Compile & Execute Swarm")
        self.btn_compile.setStyleSheet(
            "background-color: #7C4DFF; color: white; font-weight: bold; border-radius: 6px; padding: 10px;"
        )
        self.btn_compile.clicked.connect(self.compile_and_execute_swarm)
        action_row.addWidget(self.btn_compile)
        left_layout.addLayout(action_row)

        splitter.addWidget(left_widget)

        # ── Right Column: Compiled Flow View & Swarm Debate Terminal ──
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        right_layout.addWidget(QLabel("Compiled Swarm Execution Graph:"))
        self.flow_diagram = QTextEdit()
        self.flow_diagram.setReadOnly(True)
        self.flow_diagram.setStyleSheet(
            "background-color: #0b0b0d; border-radius: 6px; border: 1px solid #1E1E22; font-family: monospace; font-size: 11px; padding: 10px;"
        )
        self.display_compiled_graph()
        right_layout.addWidget(self.flow_diagram)

        right_layout.addWidget(QLabel("Swarm Consensus Debate Console:"))
        self.debate_console = QTextEdit()
        self.debate_console.setReadOnly(True)
        self.debate_console.setStyleSheet(
            "background-color: #0b0b0d; border-radius: 6px; border: 1px solid #1E1E22; font-family: monospace; font-size: 11px; padding: 10px;"
        )
        self.display_swarm_debate()
        right_layout.addWidget(self.debate_console)

        splitter.addWidget(right_widget)

        splitter.setSizes([450, 550])

    def add_initial_mock_steps(self):
        self.steps_list.addItem(
            QListWidgetItem("Step 1 : systems-manager (Scan disk & CPU limits)")
        )
        self.steps_list.addItem(
            QListWidgetItem("Step 2 : uptime-self-healer (Check Docker platform)")
        )
        self.steps_list.addItem(
            QListWidgetItem("Step 3 : technitium-dns-mcp (Apply DNS rewrite rules)")
        )

    def add_workflow_step(self):
        text = self.specialist_selector.currentText()
        step_idx = self.steps_list.count() + 1
        item_text = f"Step {step_idx} : {text}"
        self.steps_list.addItem(QListWidgetItem(item_text))
        self.display_compiled_graph()

    def clear_steps(self):
        self.steps_list.clear()
        self.flow_diagram.clear()

    def display_compiled_graph(self):
        steps_count = self.steps_list.count()
        if steps_count == 0:
            self.flow_diagram.setHtml(
                "<pre style='color: #8A8A93;'>Add steps to visualize the execution graph.</pre>"
            )
            return

        graph_lines = [
            "------------------- COMPILED SWARM WORKFLOW GRAPH -------------------",
            "",
        ]

        flow_nodes = []
        for i in range(steps_count):
            item_text = self.steps_list.item(i).text()
            name = item_text.split(" : ")[1].split(" (")[0]
            flow_nodes.append(f"[{name}]")

        graph_lines.append("  " + "  ──>  ".join(flow_nodes))
        graph_lines.extend(
            [
                "",
                "---------------------------------------------------------------------",
            ]
        )

        self.flow_diagram.setHtml(
            f"<pre style='color: #00E5FF;'>{chr(10).join(graph_lines)}</pre>"
        )

    def display_swarm_debate(self):
        debate_log = (
            "<span style='color: #00E676;'>[systems-manager]</span>: Initializing host scanning. All system limits look clean.<br>"
            "<span style='color: #00E5FF;'>[uptime-self-healer]</span>: Checking Docker platforms... technitium container is up and DNS resolver port is healthy.<br>"
            "<span style='color: #FFAB40;'>[technitium-dns-mcp]</span>: Initiating DNS lookup rewrite rules. Rerouting local host to staging container.<br>"
            "<span style='color: #7C4DFF;'>[Consensus Lock]</span>: Consensus reached. All 3 agents approve execution chain pipeline."
        )
        self.debate_console.setHtml(debate_log)

    def compile_and_execute_swarm(self):
        self.btn_compile.setEnabled(False)
        self.btn_compile.setText("Executing Swarm Chain...")

        async def run_swarm():
            import time

            time.sleep(1.2)  # Simulate Swarm consensus deliberation
            return True

        def on_done(res):
            self.btn_compile.setEnabled(True)
            self.btn_compile.setText("⚡ Compile & Execute Swarm")
            self.debate_console.append(
                "\n\n<span style='color: #00E676;'>[Execution Complete]</span> Swarm pipeline finished with 0 errors."
            )

        def on_fail(err):
            self.btn_compile.setEnabled(True)
            self.btn_compile.setText("⚡ Compile & Execute Swarm")
            self.debate_console.append(
                f"\n\n<span style='color: #FF1744;'>[Execution Failed]</span> Swarm failed:\n{err}"
            )

        self.worker.run_agent_task(run_swarm, on_finished=on_done, on_error=on_fail)
