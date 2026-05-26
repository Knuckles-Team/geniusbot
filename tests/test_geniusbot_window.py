from geniusbot.geniusbot import GeniusBot
from geniusbot.qt.terminal_widget import TerminalBridge, TerminalWidget
from geniusbot.qt.tool_guard import ToolGuardDialog
from geniusbot.qt.widget_mapper import AgentControlPanel
from geniusbot.utils.agent_bridge import AgentBridgeWorker


def test_genius_bot_window_instantiation(qapp):
    """Verify that the main GeniusBot cockpit window instantiates successfully."""
    bot = GeniusBot()
    assert bot is not None
    assert bot.windowTitle() == "GeniusBot Multi-Agent Cockpit"
    assert bot.width() == 1200
    assert bot.height() == 800
    bot.close()


def test_terminal_widget_instantiation(qapp):
    """Verify that our hybrid terminal emulator instantiates correctly."""
    term = TerminalWidget()
    assert term is not None
    assert isinstance(term.bridge, TerminalBridge)
    term.close()


def test_tool_guard_dialog_instantiation(qapp):
    """Verify that our secure execution guard modal instantiates with sample parameters."""
    dialog = ToolGuardDialog("test_tool", {"arg1": "val1", "arg2": 42})
    assert dialog is not None
    assert dialog.windowTitle() == "Action Authorization Required"
    assert (
        "test_tool" in dialog.args_viewer.toPlainText()
        or "arg1" in dialog.args_viewer.toPlainText()
    )
    dialog.close()


def test_agent_control_panel_instantiation(qapp):
    """Verify that a dynamic agent control card compiles correctly from specialist schemas."""
    worker = AgentBridgeWorker()
    agent_data = {
        "name": "Data Explorer",
        "description": "Scrapes and parses structured repositories.",
        "skills": ["scrape_web", "git_operations"],
        "type": "specialist",
    }
    panel = AgentControlPanel(agent_data, worker)
    assert panel is not None
    assert "scrape_web" in panel.inputs or "task_query" in panel.inputs
    panel.close()
