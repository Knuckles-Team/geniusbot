#!/usr/bin/env python3

import inspect

from geniusbot.qt.finance_cockpit import FinanceCockpitPanel
from geniusbot.qt.graph_explorer import GraphExplorerPanel
from geniusbot.qt.infra_cockpit import InfrastructureCockpitPanel
from geniusbot.qt.security_policy import SecurityPolicyPanel
from geniusbot.qt.telemetry_dashboard import TelemetryDashboardPanel
from geniusbot.qt.workflow_builder import WorkflowBuilderPanel


def test_cockpit_panels_exist():
    """Verify that all cockpit panels are correctly defined and can be imported."""
    assert inspect.isclass(GraphExplorerPanel)
    assert inspect.isclass(TelemetryDashboardPanel)
    assert inspect.isclass(WorkflowBuilderPanel)
    assert inspect.isclass(SecurityPolicyPanel)
    assert inspect.isclass(InfrastructureCockpitPanel)
    assert inspect.isclass(FinanceCockpitPanel)


def test_panel_signatures():
    """Verify constructors have the expected signature with worker parameter."""
    for cls in [
        GraphExplorerPanel,
        TelemetryDashboardPanel,
        WorkflowBuilderPanel,
        SecurityPolicyPanel,
        InfrastructureCockpitPanel,
        FinanceCockpitPanel,
    ]:
        sig = inspect.signature(cls.__init__)
        assert "worker" in sig.parameters
