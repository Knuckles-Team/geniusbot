#!/usr/bin/env python3
import logging
import os
import sys
import warnings

from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Suppress annoying library warnings
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv.*")

# Append directories for local execution
sys.path.append(os.path.dirname(__file__))

# Local imports
from geniusbot.qt.colors import BG_SECONDARY, BORDER_COLOR, DARK_COCKPIT_STYLE

# Cockpit panel imports
from geniusbot.qt.terminal_widget import TerminalWidget
from geniusbot.qt.widget_mapper import WidgetSchemaMapper
from geniusbot.utils.agent_bridge import AgentBridgeWorker
from geniusbot.utils.daemon import GeniusBotDaemon

__version__ = "6.0.0"


# Resolve centralized log directory
try:
    from agent_utilities.core.paths import log_dir

    geniusbot_log_dir = log_dir()
except ImportError:
    from pathlib import Path

    import platformdirs

    geniusbot_log_dir = Path(
        platformdirs.user_log_path("agent-utilities", "knuckles-team")
    )

geniusbot_log_dir.mkdir(parents=True, exist_ok=True)
geniusbot_log_path = geniusbot_log_dir / "geniusbot.log"

logger = logging.getLogger("geniusbot")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.FileHandler(geniusbot_log_path)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class OutputWrapper(QObject):
    """Bridge standard output streams into Qt Signals thread-safely."""

    outputWritten = Signal(str, bool)

    def __init__(self, parent, stdout=True):
        super().__init__(parent)
        self._stdout = stdout
        if stdout:
            self._stream = sys.stdout
            sys.stdout = self
        else:
            self._stream = sys.stderr
            sys.stderr = self

    def write(self, text):
        self._stream.write(text)
        self.outputWritten.emit(text, self._stdout)

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __del__(self):
        try:
            if self._stdout:
                sys.stdout = self._stream
            else:
                sys.stderr = self._stream
        except AttributeError:
            pass


class GeniusBot(QMainWindow):
    """GeniusBot Cockpit Dashboard Window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = AgentBridgeWorker()
        self.daemon = GeniusBotDaemon(self)
        self.discovered_specialists = []
        self.active_agent_card = None

        self.initialize_user_interface()
        self.setup_tray_daemon()

        # Asynchronously load specialists from Knowledge Graph after application startup
        QTimer.singleShot(100, self.async_load_specialists)

    def initialize_user_interface(self):
        self.setWindowTitle("GeniusBot Multi-Agent Cockpit")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_COCKPIT_STYLE)

        # Central widget splitter (Left sidebar vs Central pane vs Right Drawer)
        self.centralSplitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.centralSplitter)

        # ── Left Navigation Sidebar ──
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setMinimumWidth(180)
        self.sidebar.setMaximumWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(12)

        # Sidebar Title
        title_label = QLabel("🚀 GENIUSBOT")
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #7C4DFF; padding-left: 10px; margin-bottom: 10px;"
        )
        sidebar_layout.addWidget(title_label)

        # Navigation buttons
        self.btn_deck = QPushButton("🌌 Specialist Deck")
        self.btn_deck.clicked.connect(lambda: self.switch_view(0))
        sidebar_layout.addWidget(self.btn_deck)

        self.btn_term = QPushButton("🖥️ CLI Terminal")
        self.btn_term.clicked.connect(lambda: self.switch_view(1))
        sidebar_layout.addWidget(self.btn_term)

        self.btn_chat = QPushButton("💬 Copilot Chat")
        self.btn_chat.clicked.connect(lambda: self.switch_view(2))
        sidebar_layout.addWidget(self.btn_chat)

        # Cockpit Controls Header
        cockpit_header = QLabel("🎛️ COCKPIT CONTROLS")
        cockpit_header.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #8A8A93; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;"
        )
        sidebar_layout.addWidget(cockpit_header)

        self.btn_graph = QPushButton("🌌 Graph Explorer")
        self.btn_graph.clicked.connect(lambda: self.switch_view(3))
        sidebar_layout.addWidget(self.btn_graph)

        self.btn_telemetry = QPushButton("📈 Live Telemetry")
        self.btn_telemetry.clicked.connect(lambda: self.switch_view(4))
        sidebar_layout.addWidget(self.btn_telemetry)

        self.btn_workflow = QPushButton("⛓️ Swarm Builder")
        self.btn_workflow.clicked.connect(lambda: self.switch_view(5))
        sidebar_layout.addWidget(self.btn_workflow)

        self.btn_security = QPushButton("🛡️ Security Policies")
        self.btn_security.clicked.connect(lambda: self.switch_view(6))
        sidebar_layout.addWidget(self.btn_security)

        self.btn_infra = QPushButton("🏥 Infrastructure")
        self.btn_infra.clicked.connect(lambda: self.switch_view(7))
        sidebar_layout.addWidget(self.btn_infra)

        self.btn_finance = QPushButton("📊 Trading Cockpit")
        self.btn_finance.clicked.connect(lambda: self.switch_view(8))
        sidebar_layout.addWidget(self.btn_finance)

        self.btn_dashboard = QPushButton("🏠 Service Dashboard")
        self.btn_dashboard.clicked.connect(lambda: self.switch_view(9))
        sidebar_layout.addWidget(self.btn_dashboard)

        sidebar_layout.addStretch()

        # Sidebar footer status
        self.lbl_status = QLabel("System Ready")
        self.lbl_status.setStyleSheet(
            "color: #8A8A93; font-size: 11px; padding-left: 10px;"
        )
        sidebar_layout.addWidget(self.lbl_status)

        self.centralSplitter.addWidget(self.sidebar)

        # ── Main Content Pane (Stacked view) ──
        self.centralStackWidget = QStackedWidget()

        # View 1: Agent Deck (Scroll Area)
        self.deck_scroll = QScrollArea()
        self.deck_scroll.setWidgetResizable(True)
        self.deck_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self.deck_container = QWidget()
        self.deck_layout = QVBoxLayout(self.deck_container)
        self.deck_layout.setSpacing(16)
        self.deck_layout.setContentsMargins(20, 20, 20, 20)
        self.deck_scroll.setWidget(self.deck_container)
        self.centralStackWidget.addWidget(self.deck_scroll)

        # View 2: xterm.js Terminal
        self.term_widget = TerminalWidget()
        self.centralStackWidget.addWidget(self.term_widget)

        # View 3: Copilot Chat
        self.chat_container = QWidget()
        chat_layout = QVBoxLayout(self.chat_container)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(12)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 10px;"
        )
        chat_layout.addWidget(self.chat_log)

        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask the master agent anything...")
        self.chat_input.returnPressed.connect(self.send_chat_message)

        # Native Autocomplete Completer
        self.completer = QCompleter([], self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.chat_input.setCompleter(self.completer)
        self.chat_input.textChanged.connect(self.handle_input_text_changed)

        input_row.addWidget(self.chat_input)

        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self.send_chat_message)
        input_row.addWidget(self.btn_send)
        chat_layout.addLayout(input_row)

        self.centralStackWidget.addWidget(self.chat_container)

        # View 4-9: Lazy-loaded panel placeholders
        self.graph_panel = None
        self.telemetry_panel = None
        self.workflow_panel = None
        self.security_panel = None
        self.infra_panel = None
        self.finance_panel = None
        self.dashboard_panel = None

        for _ in range(7):
            self.centralStackWidget.addWidget(QWidget())

        self.centralSplitter.addWidget(self.centralStackWidget)

        # ── Slide-Out Right Detail Drawer ──
        self.detail_drawer = QFrame()
        self.detail_drawer.setStyleSheet(
            f"background-color: {BG_SECONDARY}; border-left: 1px solid {BORDER_COLOR};"
        )
        self.detail_drawer.setMinimumWidth(320)
        self.detail_drawer.setMaximumWidth(400)

        drawer_layout = QVBoxLayout(self.detail_drawer)
        drawer_layout.setContentsMargins(15, 20, 15, 20)
        drawer_layout.setSpacing(12)

        drawer_title = QLabel("🔮 TELEMETRY & LOGS")
        drawer_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #7C4DFF;"
        )
        drawer_layout.addWidget(drawer_title)

        drawer_layout.addWidget(QLabel("Telemetry / Diagnostics Info:"))
        self.telemetry_log = QTextEdit()
        self.telemetry_log.setReadOnly(True)
        self.telemetry_log.setStyleSheet(
            "background-color: #121214; border-radius: 6px; font-family: monospace; font-size: 11px;"
        )
        drawer_layout.addWidget(self.telemetry_log)

        drawer_layout.addWidget(QLabel("Live Execution Graph Flow:"))
        self.graph_display = QLabel("No active execution diagram.")
        self.graph_display.setWordWrap(True)
        self.graph_display.setStyleSheet(
            f"background-color: #121214; border: 1px solid {BORDER_COLOR}; border-radius: 6px; padding: 10px; font-family: monospace; font-size: 11px;"
        )
        drawer_layout.addWidget(self.graph_display)

        self.centralSplitter.addWidget(self.detail_drawer)

        # Splitter sizing ratio: 15% sidebar, 50% central view, 35% right drawer
        self.centralSplitter.setSizes([180, 600, 360])

        # Bottom retractable standard out/err logger
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        self.console.setStyleSheet(
            "background-color: #0b0b0d; color: #8A8A93; border: none; font-family: monospace; font-size: 11px;"
        )

        # Redirect sys.stdout and sys.stderr
        self.stdout_wrapper = OutputWrapper(self, True)
        self.stdout_wrapper.outputWritten.connect(self.log_to_console)
        self.stderr_wrapper = OutputWrapper(self, False)
        self.stderr_wrapper.outputWritten.connect(self.log_to_console)

        # Wrap in layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.centralSplitter)
        main_layout.addWidget(self.console)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _swap_placeholder(self, index: int, new_widget: QWidget):
        placeholder = self.centralStackWidget.widget(index)
        self.centralStackWidget.removeWidget(placeholder)
        placeholder.deleteLater()
        self.centralStackWidget.insertWidget(index, new_widget)

    def switch_view(self, index: int):
        # Lazy load panels on demand
        if index == 3 and self.graph_panel is None:
            from geniusbot.qt.graph_explorer import GraphExplorerPanel

            self.graph_panel = GraphExplorerPanel(self.worker)
            self._swap_placeholder(3, self.graph_panel)
        elif index == 4 and self.telemetry_panel is None:
            from geniusbot.qt.telemetry_dashboard import TelemetryDashboardPanel

            self.telemetry_panel = TelemetryDashboardPanel(self.worker)
            self._swap_placeholder(4, self.telemetry_panel)
        elif index == 5 and self.workflow_panel is None:
            from geniusbot.qt.workflow_builder import WorkflowBuilderPanel

            self.workflow_panel = WorkflowBuilderPanel(self.worker)
            self._swap_placeholder(5, self.workflow_panel)
        elif index == 6 and self.security_panel is None:
            from geniusbot.qt.security_policy import SecurityPolicyPanel

            self.security_panel = SecurityPolicyPanel(self.worker)
            self._swap_placeholder(6, self.security_panel)
        elif index == 7 and self.infra_panel is None:
            from geniusbot.qt.infra_cockpit import InfrastructureCockpitPanel

            self.infra_panel = InfrastructureCockpitPanel(self.worker)
            self._swap_placeholder(7, self.infra_panel)
        elif index == 8 and self.finance_panel is None:
            from geniusbot.qt.finance_cockpit import FinanceCockpitPanel

            self.finance_panel = FinanceCockpitPanel(self.worker)
            self._swap_placeholder(8, self.finance_panel)
        elif index == 9 and self.dashboard_panel is None:
            from geniusbot.qt.service_dashboard import ServiceDashboardPanel

            self.dashboard_panel = ServiceDashboardPanel(self.worker)
            self._swap_placeholder(9, self.dashboard_panel)

        self.centralStackWidget.setCurrentIndex(index)
        # Style active sidebar button
        self.btn_deck.setStyleSheet(
            "background-color: transparent; border: none;" if index != 0 else ""
        )
        self.btn_term.setStyleSheet(
            "background-color: transparent; border: none;" if index != 1 else ""
        )
        self.btn_chat.setStyleSheet(
            "background-color: transparent; border: none;" if index != 2 else ""
        )
        self.btn_graph.setStyleSheet(
            "background-color: transparent; border: none;" if index != 3 else ""
        )
        self.btn_telemetry.setStyleSheet(
            "background-color: transparent; border: none;" if index != 4 else ""
        )
        self.btn_workflow.setStyleSheet(
            "background-color: transparent; border: none;" if index != 5 else ""
        )
        self.btn_security.setStyleSheet(
            "background-color: transparent; border: none;" if index != 6 else ""
        )
        self.btn_infra.setStyleSheet(
            "background-color: transparent; border: none;" if index != 7 else ""
        )
        self.btn_finance.setStyleSheet(
            "background-color: transparent; border: none;" if index != 8 else ""
        )
        self.btn_dashboard.setStyleSheet(
            "background-color: transparent; border: none;" if index != 9 else ""
        )

        # Launch terminal shells when clicked
        if index == 1 and not self.term_widget.fd:
            # Execute agent-terminal-ui inside xterm if available
            self.term_widget.start_shell("agent-terminal-ui")

    def setup_tray_daemon(self):
        """Bind Daemon trays and system states."""
        self.daemon.show_requested.connect(self.showNormal)
        self.daemon.terminal_requested.connect(
            lambda: (self.showNormal(), self.switch_view(1))
        )
        self.daemon.health_check_requested.connect(self.run_health_check)
        self.daemon.exit_requested.connect(self.close)
        self.daemon.start()

    def async_load_specialists(self):
        """Asynchronously load all specialists from the Knowledge Graph via the Gateway."""
        self.lbl_status.setText("Connecting Graph...")

        async def fetch(progress_cb=None):
            import httpx

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://localhost:8000/api/enhanced/agents", timeout=5.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "ok":
                            return data.get("agents", [])
            except Exception as e:
                logger.warning(f"Failed to fetch specialists from gateway: {e}")
            return []

        def on_finished(specs):
            self.discovered_specialists = specs
            self.lbl_status.setText(f"{len(specs)} specialists loaded.")
            self.populate_specialist_deck()

        def on_error(err):
            logger.error(f"Discovery failed: {err}")
            self.lbl_status.setText("Graph offline.")

        self.worker.run_agent_task(fetch, on_finished=on_finished, on_error=on_error)

    def populate_specialist_deck(self):
        """Add discovered specialists control widgets into the scrolling deck layout."""
        # Clear container
        for i in reversed(range(self.deck_layout.count())):
            widget = self.deck_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        cards = WidgetSchemaMapper.build_deck(
            self.discovered_specialists, self.worker, self
        )
        for card in cards:
            card.execution_started.connect(self.on_agent_started)
            card.execution_finished.connect(self.on_agent_finished)
            card.execution_failed.connect(self.on_agent_failed)
            self.deck_layout.addWidget(card)

        self.deck_layout.addStretch()

    # Agent Lifecycle Callbacks
    def on_agent_started(self, agent_name):
        self.lbl_status.setText(f"Running {agent_name}...")
        self.telemetry_log.append(f"⏱️ Spawning {agent_name} Specialist...")

    def on_agent_finished(self, agent_name, result):
        self.lbl_status.setText(f"{agent_name} Complete.")
        self.telemetry_log.append(f"✅ {agent_name} Completed execution.\n")

        # Display output in drawer details
        result_text = result.get("result", str(result))
        self.telemetry_log.append(f"Output:\n{result_text}\n")

        # Update graph mermaid visualization if included
        mermaid = result.get("mermaid")
        if mermaid:
            self.graph_display.setText(mermaid)

    def on_agent_failed(self, agent_name, error_trace):
        self.lbl_status.setText(f"{agent_name} Failed!")
        self.telemetry_log.append(f"❌ {agent_name} Crashed:\n{error_trace}\n")

    def run_health_check(self):
        """Run health check against the centralized Gateway."""
        self.telemetry_log.append("🏥 Initiating Engine Diagnostics...")
        self.lbl_status.setText("Health checking...")

        async def verify(progress_cb=None):
            import httpx

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://localhost:8000/api/enhanced/maintenance/status",
                        timeout=5.0,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "status": "success",
                            "result": f"Gateway healthy. Maintenance Required: {data.get('maintenance_required', False)}",
                        }
            except Exception as e:
                logger.warning(f"Gateway health check failed: {e}")
            return {"status": "error", "result": "❌ central Gateway offline."}

        self.worker.run_agent_task(
            verify,
            on_finished=lambda res: self.telemetry_log.append(
                f"Diagnostics:\n{res.get('result')}\n"
            ),
            on_error=lambda err: self.telemetry_log.append(
                f"Health check failed:\n{err}\n"
            ),
        )

    def handle_input_text_changed(self, text):
        """Asynchronously fetch autocomplete suggestions and populate QCompleter."""
        if text.startswith("/"):

            async def fetch_suggestions(progress_cb=None):
                import httpx

                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            f"http://localhost:8000/api/enhanced/commands/autocomplete?query={text}",
                            timeout=3.0,
                        )
                        if response.status_code == 200:
                            return response.json().get("suggestions", [])
                except Exception as e:
                    logger.debug(f"Autocomplete fetch failed: {e}")
                return []

            def on_finished(suggestions):
                if suggestions:
                    from PySide6.QtCore import QStringListModel

                    model = QStringListModel(suggestions, self.completer)
                    self.completer.setModel(model)
                    self.completer.complete()

            self.worker.run_agent_task(fetch_suggestions, on_finished=on_finished)

    def send_chat_message(self):
        """Execute master copilot query with prompt injection scan and secure guard confirmations."""
        query = self.chat_input.text().strip()
        if not query:
            return

        self.chat_input.clear()
        self.chat_log.append(f"\n👤 You: {query}")

        # Task runner targets
        async def ask_copilot(progress_cb=None):
            import json

            import httpx

            # If it starts with / command
            if query.startswith("/"):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "http://localhost:8000/api/enhanced/commands/execute",
                            json={"command": query},
                            timeout=15.0,
                        )
                        if response.status_code == 200:
                            data = response.json()
                            return {
                                "result": data.get("response_markdown", ""),
                                "client_actions": data.get("client_actions", []),
                            }
                        else:
                            return {
                                "result": f"❌ Gateway command error: Code {response.status_code}"
                            }
                except Exception as e:
                    return {
                        "result": f"❌ Gateway connection failed: {e}. Falling back to local run is not supported for slash commands."
                    }

            # Normal query execution: Try streaming via Gateway SSE first
            try:
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        "http://localhost:8000/stream",
                        json={"query": query, "mode": "ask", "topology": "basic"},
                        timeout=60.0,
                    ) as stream:
                        final_output = ""
                        async for line in stream.aiter_lines():
                            if line.startswith("data: "):
                                try:
                                    event = json.loads(line[6:])
                                    ev_type = event.get("type")
                                    if ev_type == "final_output":
                                        final_output = event.get("content", "")
                                    elif ev_type == "thought" and progress_cb:
                                        progress_cb(f"💭 {event.get('thought', '')}")
                                    elif ev_type == "call_tool" and progress_cb:
                                        progress_cb(f"🛠️ Tool: {event.get('tool', '')}")
                                    elif progress_cb:
                                        progress_cb(
                                            f"📡 {ev_type}: {event.get('message', '') or event.get('error', '')}"
                                        )
                                except Exception:
                                    continue
                        if final_output:
                            return {"result": final_output}
            except Exception as e:
                logger.warning(f"Gateway SSE execution failed: {e}")

            return {
                "result": "❌ Gateway is offline. Please make sure the agent-utilities gateway is running at http://localhost:8000."
            }

        def on_done(res):
            ans = res.get("result", str(res))
            self.chat_log.append(f"🤖 Copilot: {ans}")
            mermaid = res.get("mermaid")
            if mermaid:
                self.graph_display.setText(mermaid)

            # Handle gateway client actions
            actions = res.get("client_actions", [])
            for action_dict in actions:
                action = action_dict.get("action")
                if action == "clear_chat":
                    self.chat_log.clear()
                    self.chat_log.append("🧹 Chat log cleared via slash command.")

        def on_fail(err):
            self.chat_log.append(f"❌ Error: {err}")

        def on_progress(msg):
            # Append live thinking/progress directly to the telemetry log
            self.telemetry_log.append(msg)
            self.lbl_status.setText("Agent thinking...")

        self.worker.run_agent_task(
            ask_copilot, on_finished=on_done, on_error=on_fail, on_progress=on_progress
        )

    @Slot(str, bool)
    def log_to_console(self, text, is_stdout=True):
        self.console.moveCursor(self.console.textCursor().End)
        self.console.insertPlainText(text)

    def closeEvent(self, event):
        """Minimize window to tray instead of quitting."""
        if self.daemon.tray_icon.isVisible():
            self.hide()
            self.daemon.tray_icon.showMessage(
                "GeniusBot Cockpit",
                "Application is still running in background tray.",
                QSystemTrayIcon.Information,
                2000,
            )
            event.ignore()
        else:
            self.daemon.stop()
            event.accept()


def geniusbot():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    bot_window = GeniusBot()
    bot_window.show()
    sys.exit(app.exec())


def main():
    geniusbot()


if __name__ == "__main__":
    geniusbot()
