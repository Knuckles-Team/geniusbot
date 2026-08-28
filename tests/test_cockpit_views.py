#!/usr/bin/env python3

import inspect
from unittest.mock import MagicMock

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


def _make_data_query_panel(qapp) -> DataQueryPanel:
    return DataQueryPanel(MagicMock())


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_render_rows_dict_shaped(qapp) -> None:
    """dict rows (column-keyed): columns come from the first row's keys, in
    order, and each cell falls back to "" for a missing key."""
    panel = _make_data_query_panel(qapp)
    panel._render_rows([{"a": 1, "b": 2}, {"a": 3}])
    assert panel.rows_table.columnCount() == 2
    assert panel.rows_table.rowCount() == 2
    headers = [
        panel.rows_table.horizontalHeaderItem(c).text() for c in range(2)
    ]
    assert headers == ["a", "b"]
    assert panel.rows_table.item(0, 0).text() == "1"
    assert panel.rows_table.item(0, 1).text() == "2"
    assert panel.rows_table.item(1, 0).text() == "3"
    assert panel.rows_table.item(1, 1).text() == ""


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_render_rows_positional_shaped(qapp) -> None:
    """list rows (positional): column count is the WIDEST row; headers are
    synthesized as col0/col1/...."""
    panel = _make_data_query_panel(qapp)
    panel._render_rows([[1, 2, 3], [4, 5]])
    assert panel.rows_table.columnCount() == 3
    assert panel.rows_table.rowCount() == 2
    headers = [
        panel.rows_table.horizontalHeaderItem(c).text() for c in range(3)
    ]
    assert headers == ["col0", "col1", "col2"]
    assert panel.rows_table.item(0, 2).text() == "3"
    assert panel.rows_table.item(1, 0).text() == "4"
    assert panel.rows_table.item(1, 1).text() == "5"


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_render_rows_empty_clears_table(qapp) -> None:
    panel = _make_data_query_panel(qapp)
    panel._render_rows([{"a": 1}])
    assert panel.rows_table.rowCount() == 1
    panel._render_rows([])
    assert panel.rows_table.rowCount() == 0
    assert panel.rows_table.columnCount() == 0


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_on_answer_builds_html_with_query_and_citations(qapp) -> None:
    panel = _make_data_query_panel(qapp)
    panel._on_answer(
        {
            "answer": "42 agents.",
            "query": "MATCH (a:Agent) RETURN count(a)",
            "citations": ["doc-1", "doc-2"],
            "rows": [{"count": 42}],
        }
    )
    html = panel.answer_view.toHtml()
    assert "42 agents." in html
    assert "MATCH (a:Agent) RETURN count(a)" in html
    assert "doc-1" in html and "doc-2" in html
    assert panel.btn_ask.isEnabled()
    assert "Done." in panel.status_lbl.text()
    assert panel.rows_table.rowCount() == 1


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_on_answer_omits_query_and_citations_sections_when_absent(qapp) -> None:
    panel = _make_data_query_panel(qapp)
    panel._on_answer({"answer": "just an answer"})
    html = panel.answer_view.toHtml()
    assert "just an answer" in html
    assert "Generated query" not in html
    assert "Citations" not in html


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_on_answer_falls_back_to_result_when_no_answer_key(qapp) -> None:
    panel = _make_data_query_panel(qapp)
    panel._on_answer({"result": "fallback text"})
    assert "fallback text" in panel.answer_view.toHtml()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
def test_on_answer_routes_error_payload_to_on_error(qapp) -> None:
    panel = _make_data_query_panel(qapp)
    panel._on_answer({"error": "gateway is offline"})
    assert "gateway is offline" in panel.answer_view.toHtml()
    assert "❌" in panel.status_lbl.text()
    assert panel.btn_ask.isEnabled()


@pytest.mark.unit
@pytest.mark.concept("GBOT-6.0")
@pytest.mark.parametrize(
    "data,expected",
    [
        (
            {"result": [{"reference": "kg1", "text": "hit1", "score": 0.9}]},
            [{"source": "kg1", "text": "hit1", "score": 0.9}],
        ),
        (
            {"result": {"results": [{"source": "kg2", "title": "t", "rank": 3}]}},
            [{"source": "kg2", "text": "t", "score": 3}],
        ),
        (
            {"result": {"hits": [{"graph": "kg3", "name": "n", "score": 1}]}},
            [{"source": "kg3", "text": "n", "score": 1}],
        ),
        (
            {"result": [{"id": "only-id-no-text"}]},
            [{"source": "", "text": "only-id-no-text", "score": ""}],
        ),
        (
            {"result": ["plain string result"]},
            [{"source": "", "text": "plain string result", "score": ""}],
        ),
        ({"result": {"results": []}}, []),
        ({"result": {}}, []),
        ({"result": "scalar"}, []),
        ({"other": "no result key"}, []),
    ],
)
def test_federated_search_panel_extract_results(data, expected):
    """Characterize _extract_results's envelope-unwrap (data.result ->
    results/hits) and per-item field-precedence fallbacks (reference >
    source > graph for `source`; text > title > name > id > raw item for
    `text`; score > rank for `score`), plus the non-dict-item and
    non-list/empty-payload fallbacks."""
    assert FederatedSearchPanel._extract_results(data) == expected
