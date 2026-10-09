#!/usr/bin/env python3
import importlib
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
from geniusbot.qt.terminal_widget import TerminalWidget
from geniusbot.qt.widget_mapper import WidgetSchemaMapper
from geniusbot.services.gateway_client import GatewayClient
from geniusbot.services.operation_registry import load_installed_registry
from geniusbot.utils.agent_bridge import AgentBridgeWorker
from geniusbot.utils.daemon import GeniusBotDaemon

__version__ = "5.2.0"


# Resolve centralized log directory via the single backend seam
from geniusbot.services.backend_adapter import backend

geniusbot_log_dir = backend.resolve_log_dir()
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
    """
    CONCEPT:AU-GBOT.cockpit.through-gbot
    GeniusBot Cockpit Dashboard Window.
    """

    # index -> (panel attribute name, module path, class name). Every lazily
    # loaded view (3..17) follows the identical pattern: import on first
    # visit, instantiate with the shared worker, cache on the instance
    # attribute, and swap the placeholder widget in the stack.
    _PANEL_SPECS: dict[int, tuple[str, str, str]] = {
        3: ("graph_panel", "geniusbot.qt.graph_explorer", "GraphExplorerPanel"),
        4: (
            "telemetry_panel",
            "geniusbot.qt.telemetry_dashboard",
            "TelemetryDashboardPanel",
        ),
        5: ("workflow_panel", "geniusbot.qt.workflow_builder", "WorkflowBuilderPanel"),
        6: ("security_panel", "geniusbot.qt.security_policy", "SecurityPolicyPanel"),
        7: ("infra_panel", "geniusbot.qt.infra_cockpit", "InfrastructureCockpitPanel"),
        8: ("finance_panel", "geniusbot.qt.finance_cockpit", "FinanceCockpitPanel"),
        9: (
            "dashboard_panel",
            "geniusbot.qt.service_dashboard",
            "ServiceDashboardPanel",
        ),
        10: ("fleet_panel", "geniusbot.qt.fleet_cockpit", "FleetCockpitPanel"),
        11: ("usage_panel", "geniusbot.qt.usage_cockpit", "UsageCockpitPanel"),
        12: (
            "extraction_panel",
            "geniusbot.qt.extraction_cockpit",
            "ExtractionCockpitPanel",
        ),
        13: (
            "temporal_panel",
            "geniusbot.qt.temporal_graph_panel",
            "TemporalGraphPanel",
        ),
        14: ("data_query_panel", "geniusbot.qt.data_query_panel", "DataQueryPanel"),
        15: ("metrics_panel", "geniusbot.qt.metrics_panel", "MetricsPanel"),
        16: (
            "federated_panel",
            "geniusbot.qt.federated_search_panel",
            "FederatedSearchPanel",
        ),
        17: ("voice_panel", "geniusbot.qt.voice_panel", "VoicePanel"),
    }

    # index -> sidebar button attribute name, for the active-view styling
    # pass at the end of switch_view.
    _SIDEBAR_BUTTON_ATTRS: dict[int, str] = {
        0: "btn_deck",
        1: "btn_term",
        2: "btn_chat",
        3: "btn_graph",
        4: "btn_telemetry",
        5: "btn_workflow",
        6: "btn_security",
        7: "btn_infra",
        8: "btn_finance",
        9: "btn_dashboard",
        10: "btn_fleet",
        11: "btn_usage",
        12: "btn_extraction",
        13: "btn_temporal",
        14: "btn_ask_data",
        15: "btn_metrics",
        16: "btn_federated",
        17: "btn_voice",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        # R002.2: refuse to start the application if the installed generated
        # operation registry is missing or malformed.
        self.operation_registry = load_installed_registry()
        self.worker = AgentBridgeWorker()
        self.daemon = GeniusBotDaemon(self)
        self.gateway = GatewayClient()
        self.discovered_specialists = []
        self.active_agent_card = None

        self.initialize_user_interface()
        self.setup_tray_daemon()

        # Asynchronously load specialists from Knowledge Graph after application startup
        QTimer.singleShot(100, self.async_load_specialists)

    def initialize_user_interface(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Initialize the main user interface components.
        Refactored to orchestrate sub-components.
        """
        self.setWindowTitle("GeniusBot Multi-Agent Cockpit")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_COCKPIT_STYLE)

        self.centralSplitter = QSplitter(Qt.Horizontal)

        self._setup_sidebar()
        self._setup_central_pane()
        self._setup_detail_drawer()
        self._setup_console_wrapper()

    def _setup_sidebar(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Setup the left navigation sidebar.
        """
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

        self.btn_temporal = QPushButton("🕰️ Temporal Graph")
        self.btn_temporal.clicked.connect(lambda: self.switch_view(13))
        sidebar_layout.addWidget(self.btn_temporal)

        self.btn_extraction = QPushButton("🧬 KG Extraction")
        self.btn_extraction.clicked.connect(lambda: self.switch_view(12))
        sidebar_layout.addWidget(self.btn_extraction)

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

        self.btn_fleet = QPushButton("🛰️ Fleet Supervisor")
        self.btn_fleet.clicked.connect(lambda: self.switch_view(10))
        sidebar_layout.addWidget(self.btn_fleet)

        self.btn_usage = QPushButton("💰 Usage & Cost")
        self.btn_usage.clicked.connect(lambda: self.switch_view(11))
        sidebar_layout.addWidget(self.btn_usage)

        self.btn_ask_data = QPushButton("🔎 Ask Data")
        self.btn_ask_data.clicked.connect(lambda: self.switch_view(14))
        sidebar_layout.addWidget(self.btn_ask_data)

        self.btn_metrics = QPushButton("📊 Engine Metrics")
        self.btn_metrics.clicked.connect(lambda: self.switch_view(15))
        sidebar_layout.addWidget(self.btn_metrics)

        self.btn_federated = QPushButton("🌐 Federated Search")
        self.btn_federated.clicked.connect(lambda: self.switch_view(16))
        sidebar_layout.addWidget(self.btn_federated)

        self.btn_voice = QPushButton("🎙️ Voice Dictation")
        self.btn_voice.clicked.connect(lambda: self.switch_view(17))
        sidebar_layout.addWidget(self.btn_voice)

        sidebar_layout.addStretch()

        # Sidebar footer status
        self.lbl_status = QLabel("System Ready")
        self.lbl_status.setStyleSheet(
            "color: #8A8A93; font-size: 11px; padding-left: 10px;"
        )
        sidebar_layout.addWidget(self.lbl_status)
        self.centralSplitter.addWidget(self.sidebar)

    def _setup_central_pane(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Setup the main central content stacked widget.
        """
        self.centralStackWidget = QStackedWidget()

        # View 0: Agent Deck (Scroll Area)
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

        # View 1: xterm.js Terminal
        self.term_widget = TerminalWidget()
        self.centralStackWidget.addWidget(self.term_widget)

        # View 2: Copilot Chat
        self._setup_copilot_chat()

        # View 3-9: Lazy-loaded panel placeholders
        self.graph_panel = None
        self.telemetry_panel = None
        self.workflow_panel = None
        self.security_panel = None
        self.infra_panel = None
        self.finance_panel = None
        self.dashboard_panel = None
        self.fleet_panel = None
        self.usage_panel = None
        self.extraction_panel = None
        self.temporal_panel = None
        self.data_query_panel = None
        self.metrics_panel = None
        self.federated_panel = None
        self.voice_panel = None

        # Views 3-13 plus the epistemic-graph capability panels 14-17 —
        # lazy-loaded placeholders (indices 3..17 inclusive).
        for _ in range(15):
            self.centralStackWidget.addWidget(QWidget())

        self.centralSplitter.addWidget(self.centralStackWidget)

    def _setup_copilot_chat(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Setup the Copilot chat pane inside the central stack.
        """
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

    def _setup_detail_drawer(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Setup the right slide-out telemetry detail drawer.
        """
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

    def _setup_console_wrapper(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Setup the bottom global terminal logger.
        """
        # Splitter sizing ratio: 15% sidebar, 50% central view, 35% right drawer
        self.centralSplitter.setSizes([180, 600, 360])

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        self.console.setStyleSheet(
            "background-color: #0b0b0d; color: #8A8A93; border: none; font-family: monospace; font-size: 11px;"
        )

        self.stdout_wrapper = OutputWrapper(self, True)
        self.stdout_wrapper.outputWritten.connect(self.log_to_console)
        self.stderr_wrapper = OutputWrapper(self, False)
        self.stderr_wrapper.outputWritten.connect(self.log_to_console)

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

    def _ensure_panel_loaded(self, index: int) -> None:
        """Lazily import + instantiate the panel for `index`, if any, and
        swap it into the placeholder slot. No-op if already loaded."""
        spec = self._PANEL_SPECS.get(index)
        if spec is None:
            return
        attr_name, module_path, class_name = spec
        if getattr(self, attr_name) is not None:
            return
        module = importlib.import_module(module_path)
        panel_cls = getattr(module, class_name)
        panel = panel_cls(self.worker)
        setattr(self, attr_name, panel)
        self._swap_placeholder(index, panel)

    def _style_sidebar_buttons(self, active_index: int) -> None:
        """Clear styling on the active view's sidebar button; transparent
        the rest."""
        for idx, attr_name in self._SIDEBAR_BUTTON_ATTRS.items():
            btn = getattr(self, attr_name)
            btn.setStyleSheet(
                "background-color: transparent; border: none;"
                if active_index != idx
                else ""
            )

    def switch_view(self, index: int):
        self._ensure_panel_loaded(index)
        self.centralStackWidget.setCurrentIndex(index)
        self._style_sidebar_buttons(index)

        if index == 1 and not self.term_widget.fd:
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
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Asynchronously load all specialists from the Knowledge Graph via the Gateway.
        """
        self.lbl_status.setText("Connecting Graph...")

        async def fetch(progress_cb=None):
            return {"specialists": await self.gateway.fetch_specialists()}

        def on_finished(result):
            specs = result["specialists"]
            self.discovered_specialists = specs
            self.lbl_status.setText(f"{len(specs)} specialists loaded.")
            self.populate_specialist_deck()

        def on_error(err):
            logger.error("Specialist discovery failed")
            self.lbl_status.setText("Graph offline.")

        self.worker.run_agent_task(fetch, on_finished=on_finished, on_error=on_error)

    def populate_specialist_deck(self):
        """Add discovered specialists control widgets into the scrolling deck layout."""
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

    def on_agent_started(self, agent_name):
        self.lbl_status.setText(f"Running {agent_name}...")
        self.telemetry_log.append(f"⏱️ Spawning {agent_name} Specialist...")

    def on_agent_finished(self, agent_name, result):
        self.lbl_status.setText(f"{agent_name} Complete.")
        self.telemetry_log.append(f"✅ {agent_name} Completed execution.\n")
        result_text = result.get("result", str(result))
        self.telemetry_log.append(f"Output:\n{result_text}\n")
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
            return await self.gateway.run_health_check()

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
                return await self.gateway.fetch_autocomplete_suggestions(text)

            def on_finished(suggestions):
                if suggestions:
                    from PySide6.QtCore import QStringListModel

                    model = QStringListModel(suggestions, self.completer)
                    self.completer.setModel(model)
                    self.completer.complete()

            self.worker.run_agent_task(fetch_suggestions, on_finished=on_finished)

    def send_chat_message(self):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Execute master copilot query with prompt injection scan and secure guard confirmations.
        """
        query = self.chat_input.text().strip()
        if not query:
            return

        self.chat_input.clear()
        self.chat_log.append(f"\n👤 You: {query}")

        self._execute_copilot_request(query)

    def _execute_copilot_request(self, query: str):
        """
        CONCEPT:AU-GBOT.cockpit.through-gbot
        Internal async handler to route the copilot request to the gateway.
        """

        async def ask_copilot(progress_cb=None):
            if query.startswith("/"):
                return await self.gateway.execute_slash_command(query)
            return await self.gateway.stream_copilot_query(query, progress_cb)

        def on_done(res):
            ans = res.get("result", str(res))
            self.chat_log.append(f"🤖 Copilot: {ans}")
            if res.get("mermaid"):
                self.graph_display.setText(res.get("mermaid"))

            for action_dict in res.get("client_actions", []):
                if action_dict.get("action") == "clear_chat":
                    self.chat_log.clear()
                    self.chat_log.append("🧹 Chat log cleared via slash command.")

        def on_fail(err):
            self.chat_log.append(f"❌ Error: {err}")

        def on_progress(msg):
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
