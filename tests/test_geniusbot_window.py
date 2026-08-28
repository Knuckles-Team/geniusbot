import pytest
from PySide6.QtWidgets import QLineEdit

from geniusbot.geniusbot import GeniusBot
from geniusbot.qt.terminal_widget import TerminalBridge, TerminalWidget
from geniusbot.qt.tool_guard import ToolGuardDialog
from geniusbot.qt.widget_mapper import AgentControlPanel
from geniusbot.utils.agent_bridge import AgentBridgeWorker


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_genius_bot_window_instantiation(qapp):
    """Verify that the main GeniusBot cockpit window instantiates successfully."""
    bot = GeniusBot()
    assert bot is not None
    assert bot.windowTitle() == "GeniusBot Multi-Agent Cockpit"
    assert bot.width() == 1200
    assert bot.height() == 800
    bot.close()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.2")
def test_terminal_widget_instantiation(qapp):
    """Verify that our hybrid terminal emulator instantiates correctly."""
    term = TerminalWidget()
    assert term is not None
    assert isinstance(term.bridge, TerminalBridge)
    term.close()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.3")
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


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.1")
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


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.1")
def test_agent_control_panel_builds_one_input_per_skill(qapp):
    """Characterize AgentControlPanel.__init__'s capability-form branch:
    a `skills` list produces exactly one QLineEdit per skill, keyed by
    skill name in `panel.inputs`."""
    worker = AgentBridgeWorker()
    agent_data = {
        "name": "Data Explorer",
        "skills": ["scrape_web", "git_operations", "summarize"],
    }
    panel = AgentControlPanel(agent_data, worker)
    assert set(panel.inputs.keys()) == {"scrape_web", "git_operations", "summarize"}
    for widget in panel.inputs.values():
        assert isinstance(widget, QLineEdit)
    panel.close()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.1")
def test_agent_control_panel_parses_comma_separated_capabilities_string(qapp):
    """Characterize the `capabilities` (str) fallback path used when
    `skills` is absent/empty: a comma-separated string is split and
    stripped into individual capability names."""
    worker = AgentBridgeWorker()
    agent_data = {
        "name": "Comma Agent",
        "capabilities": "alpha,  beta ,gamma",
    }
    panel = AgentControlPanel(agent_data, worker)
    assert set(panel.inputs.keys()) == {"alpha", "beta", "gamma"}
    panel.close()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.1")
def test_agent_control_panel_parses_list_capabilities(qapp):
    """Characterize the `capabilities` (list) fallback path."""
    worker = AgentBridgeWorker()
    agent_data = {"name": "List Agent", "capabilities": ["one", "two"]}
    panel = AgentControlPanel(agent_data, worker)
    assert set(panel.inputs.keys()) == {"one", "two"}
    panel.close()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.1")
def test_agent_control_panel_falls_back_to_task_query_when_no_capabilities(qapp):
    """Characterize the no-capabilities-at-all fallback: a single
    `task_query` free-text input."""
    worker = AgentBridgeWorker()
    agent_data = {"name": "Bare Agent"}
    panel = AgentControlPanel(agent_data, worker)
    assert set(panel.inputs.keys()) == {"task_query"}
    panel.close()


# Index -> (panel attribute name, sidebar button attribute name), mirroring
# switch_view's dispatch table so this characterization test can walk every
# lazily-loaded view without hand-listing panel classes twice.
_SWITCH_VIEW_PANEL_ATTRS = {
    3: "graph_panel",
    4: "telemetry_panel",
    5: "workflow_panel",
    6: "security_panel",
    7: "infra_panel",
    8: "finance_panel",
    9: "dashboard_panel",
    10: "fleet_panel",
    11: "usage_panel",
    12: "extraction_panel",
    13: "temporal_panel",
    14: "data_query_panel",
    15: "metrics_panel",
    16: "federated_panel",
    17: "voice_panel",
}

_SWITCH_VIEW_BUTTON_ATTRS = {
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


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_switch_view_lazily_loads_every_panel_and_styles_sidebar(qapp):
    """Characterize switch_view: for every index 0..17 except 8, the stack
    widget's current index tracks the switch, the correct panel attribute
    gets lazily instantiated exactly once (idempotent on repeat calls),
    only the active sidebar button loses the 'transparent' styling, and
    view 1 starts the embedded terminal shell exactly once.

    Index 8 (finance_panel / FinanceCockpitPanel) is deliberately excluded:
    instantiating it and then letting pytest-qt's autouse app.processEvents()
    run (as happens after every test) triggers a pre-existing native
    SIGSEGV inside libQt6Charts.so (AreaChartItem::fixEdgeSeriesDomain) when
    its charts get laid out under the offscreen QPA platform used in this
    environment -- unrelated to switch_view's own logic. See the BUGS FOUND
    section of the wD10-c-misc report. index 8's dispatch entry is
    structurally identical to every other entry in switch_view's dict
    table, so exercising 3-7 and 9-17 is sufficient to characterize the
    dispatch behavior switch_view itself is responsible for."""
    bot = GeniusBot()

    for index in [i for i in range(18) if i != 8]:
        bot.switch_view(index)
        assert bot.centralStackWidget.currentIndex() == index

        panel_attr = _SWITCH_VIEW_PANEL_ATTRS.get(index)
        if panel_attr is not None:
            panel = getattr(bot, panel_attr)
            assert panel is not None, f"panel for index {index} was not loaded"
            # Placeholder QWidget was swapped out for the real panel.
            assert bot.centralStackWidget.widget(index) is panel

        for btn_index, btn_attr in _SWITCH_VIEW_BUTTON_ATTRS.items():
            style = getattr(bot, btn_attr).styleSheet()
            if btn_index == index:
                assert style == ""
            else:
                assert "transparent" in style

    # Re-visiting an already-loaded view must not replace the panel instance.
    first_graph_panel = bot.graph_panel
    bot.switch_view(3)
    assert bot.graph_panel is first_graph_panel

    bot.close()
