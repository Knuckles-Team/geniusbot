"""Tests for the geniusbot KG extraction cockpit (CONCEPT:AU-ECO.connector.git-task-resolver).

Qt runs offscreen (conftest). The pure layout math is tested without a display;
the panel is exercised by feeding it streamed events directly.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from geniusbot.qt.force_graph import ForceGraphWidget, normalize_key, relax_layout


def test_normalize_key_merges_variants() -> None:
    assert normalize_key("The Jina AI ") == "the jina ai"
    assert normalize_key('"Jina AI".') == "jina ai"


def test_relax_layout_is_deterministic_and_spreads() -> None:
    pos = {"a": (0.0, 0.0), "b": (1.0, 0.0), "c": (0.0, 1.0)}
    edges = [("a", "b"), ("b", "c")]
    out1 = relax_layout(pos, edges, iterations=3)
    out2 = relax_layout(pos, edges, iterations=3)
    assert out1 == out2  # deterministic (no RNG)
    # repulsion pushes the two unconnected-ish nodes apart from their start
    assert out1["a"] != pos["a"]


def test_force_graph_widget_adds_nodes_and_edges(qapp) -> None:
    w = ForceGraphWidget()
    w.add_fact({"subject": "Jina AI", "predicate": "built", "object": "v5"})
    w.add_fact({"subject": "jina ai", "predicate": "released", "object": "v5"})
    # "Jina AI"/"jina ai" merge → 2 unique nodes (jina ai, v5)
    assert w.node_count() == 2
    assert w.fact_count() == 2


def test_force_graph_edge_click_emits_fact(qapp) -> None:
    w = ForceGraphWidget()
    fact = {"subject": "A", "predicate": "rel", "object": "B", "confidence": 90}
    w.add_fact(fact)
    received = []
    w.edge_selected.connect(lambda f: received.append(f))
    # find the edge item and trigger its click handler
    for item in w._scene.items():
        if hasattr(item, "_fact"):
            item._signal.emit(item._fact)  # type: ignore[attr-defined]  # test attaches a custom _signal probe to a Qt item
            break
    assert received and received[0]["subject"] == "A"


def test_panel_renders_streamed_facts_live(qapp) -> None:
    panel = _make_panel()
    # simulate the worker forwarding SSE events to the panel
    panel._on_event(json.dumps({"type": "round_start", "round": 1}))
    panel._on_event(
        json.dumps(
            {
                "type": "fact",
                "is_duplicate": False,
                "fact": {
                    "subject": "A",
                    "predicate": "rel",
                    "object": "B",
                    "tags": ["x"],
                },
            }
        )
    )
    panel._on_event(
        json.dumps({"type": "fact", "is_duplicate": True, "fact": {"subject": "A"}})
    )
    panel._on_event(json.dumps({"type": "job_done", "state": "done"}))
    assert panel.graph.fact_count() == 1  # duplicate not added to the graph
    assert panel._kept == 1 and panel._dupes == 1
    assert "done" in panel.status_lbl.text()


def test_panel_shows_fact_card_on_edge_click(qapp) -> None:
    panel = _make_panel()
    panel.show_fact_card(
        {
            "subject": "A",
            "predicate": "rel",
            "object": "B",
            "confidence": 88,
            "evidence_span": "quote",
            "tags": ["t"],
        }
    )
    html = panel.card.toHtml()
    assert "88" in html and "quote" in html


@pytest.mark.asyncio
async def test_gateway_submit_and_stream(monkeypatch) -> None:
    from geniusbot.services.gateway_client import GatewayClient

    gw = GatewayClient(base_url="http://localhost:8000")

    class _Resp:
        def __init__(self, payload):
            self._p = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._p

    class _Stream:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def aiter_lines(self):
            yield 'data: {"type": "fact", "is_duplicate": false, "fact": {"subject": "A"}}'
            yield 'data: {"type": "job_done", "state": "done"}'

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            return _Resp({"status": "submitted", "job_id": "j1"})

        def stream(self, *a, **k):
            return _Stream()

    monkeypatch.setattr("httpx.AsyncClient", lambda *a, **k: _Client())
    events = []
    out = await gw.submit_and_stream_extraction(
        text="doc", progress_cb=lambda s: events.append(s)
    )
    assert out["status"] == "done" and out["facts"] == 1
    assert any("fact" in e for e in events)


def _make_panel():
    from geniusbot.qt.extraction_cockpit import ExtractionCockpitPanel

    worker = MagicMock()
    gateway = MagicMock()
    gateway.submit_and_stream_extraction = AsyncMock(return_value={"status": "done"})
    return ExtractionCockpitPanel(worker, gateway=gateway)
