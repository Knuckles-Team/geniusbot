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


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {
                "result": [
                    {
                        "metric": {"job": "x", "instance": "y"},
                        "value": [12345, "3.5"],
                    }
                ]
            },
            [("job=x, instance=y", "3.5")],
        ),
        ({"result": [{"metric": {}, "value": [1, "v"]}]}, [("value", "v")]),
        (
            {
                "result": [
                    {"metric": {"a": "b"}, "values": [[1, "1"], [2, "2"]]}
                ]
            },
            [("a=b", "[2, '2']")],
        ),
        ({"result": ["plain-string-item"]}, [("", "plain-string-item")]),
        (
            {
                "result": {
                    "data": {
                        "result": [{"metric": {"z": "w"}, "value": [1, "9"]}]
                    }
                }
            },
            [("z=w", "9")],
        ),
        ({"result": {"data": {}}}, [("result", "{}")]),
        ({"result": None}, []),
        ({"result": ""}, []),
        ({"result": "scalar-value"}, [("result", "scalar-value")]),
        ({"other": "no result key"}, [("result", "{'other': 'no result key'}")]),
    ],
)
def test_metrics_panel_extract_series(data, expected):
    """Characterize _extract_series's Prometheus-shaped-payload flattening:
    nested data.result unwrapping, bare-list results, non-dict items,
    2-element `value` unwrapping vs. multi-point `values` left as a repr,
    and the None/empty/scalar/no-result-key fallbacks."""
    assert MetricsPanel._extract_series(data) == expected
