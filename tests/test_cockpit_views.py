#!/usr/bin/env python3

import inspect

import pytest

from geniusbot.qt.data_query_panel import DataQueryPanel
from geniusbot.qt.federated_search_panel import FederatedSearchPanel
from geniusbot.qt.finance_cockpit import FinanceCockpitPanel
from geniusbot.qt.graph_explorer import GraphExplorerPanel
from geniusbot.qt.infra_cockpit import InfrastructureCockpitPanel
from geniusbot.qt.metrics_panel import MetricsPanel
from geniusbot.qt.security_policy import SecurityPolicyPanel
from geniusbot.qt.telemetry_dashboard import TelemetryDashboardPanel
from geniusbot.qt.temporal_graph_panel import TemporalGraphPanel
from geniusbot.qt.workflow_builder import WorkflowBuilderPanel


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_cockpit_panels_exist():
    """Verify that all cockpit panels are correctly defined and can be imported."""
    assert inspect.isclass(GraphExplorerPanel)
    assert inspect.isclass(TelemetryDashboardPanel)
    assert inspect.isclass(WorkflowBuilderPanel)
    assert inspect.isclass(SecurityPolicyPanel)
    assert inspect.isclass(InfrastructureCockpitPanel)
    assert inspect.isclass(FinanceCockpitPanel)
    assert inspect.isclass(TemporalGraphPanel)
    assert inspect.isclass(DataQueryPanel)
    assert inspect.isclass(MetricsPanel)
    assert inspect.isclass(FederatedSearchPanel)


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
@pytest.mark.parametrize(
    "cls",
    [
        GraphExplorerPanel,
        TelemetryDashboardPanel,
        WorkflowBuilderPanel,
        SecurityPolicyPanel,
        InfrastructureCockpitPanel,
        FinanceCockpitPanel,
        TemporalGraphPanel,
        DataQueryPanel,
        MetricsPanel,
        FederatedSearchPanel,
    ],
)
def test_panel_signatures(cls):
    """Verify constructors have the expected signature with worker parameter."""
    sig = inspect.signature(cls.__init__)
    assert "worker" in sig.parameters
