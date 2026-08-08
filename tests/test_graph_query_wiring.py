"""Wiring tests for the Knowledge-Graph query path.

CONCEPT:AU-GBOT.cockpit.through-gbot

``BackendAdapter.run_graph_query`` used to import ``run_graph_query`` from
``agent_utilities.graph`` — a symbol that does not exist there — and swallow the
resulting ``ImportError``, so the Graph Explorer and the temporal-graph panel
always fell through to their local simulators. These tests drive the real path:
an HTTP request must actually leave the client, hit ``/api/graph/query``, and
its rows must reach the caller.
"""

from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from typing import Any

import httpx
import pytest

# Import the two service modules without executing ``geniusbot/__init__.py``,
# which pulls in the whole Qt application. Same intent as
# ``tests/security/test_gateway_client_security.py``'s file-path import: these
# tests exercise the backend seam, not the UI.
_ROOT = Path(__file__).resolve().parents[1]
if "geniusbot" not in sys.modules:
    _pkg = types.ModuleType("geniusbot")
    _pkg.__path__ = [str(_ROOT / "geniusbot")]
    sys.modules["geniusbot"] = _pkg
    _services = types.ModuleType("geniusbot.services")
    _services.__path__ = [str(_ROOT / "geniusbot" / "services")]
    sys.modules["geniusbot.services"] = _services

from geniusbot.services.backend_adapter import BackendAdapter  # noqa: E402


class _RecordingTransport(httpx.AsyncBaseTransport):
    """A stand-in gateway that records the request and answers like the real one."""

    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(self.status_code, json=self.payload, request=request)


def _adapter_with(transport: httpx.AsyncBaseTransport) -> BackendAdapter:
    adapter = BackendAdapter()
    client = adapter._gateway()
    client._direct_http = httpx.AsyncClient(
        base_url=client.base_url, transport=transport, timeout=5.0
    )
    return adapter


def test_run_graph_query_posts_to_the_canonical_action_twin() -> None:
    transport = _RecordingTransport(
        {
            "status": "success",
            "result": {
                "evidence_spans": [
                    ["agentpay-sdk", "TRANSFERS", "ERC20_Payment_Tx"],
                ]
            },
        }
    )
    adapter = _adapter_with(transport)

    rows = asyncio.run(adapter.run_graph_query("MATCH (n) RETURN n LIMIT 1"))

    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert request.method == "POST"
    assert request.url.path == "/api/graph/query"
    body = request.read().decode("utf-8")
    assert "MATCH (n) RETURN n LIMIT 1" in body
    # The rows the gateway returned reach the caller unchanged — this is what
    # the Graph Explorer renders instead of its simulator.
    assert rows == [["agentpay-sdk", "TRANSFERS", "ERC20_Payment_Tx"]]


def test_run_graph_query_returns_none_when_the_gateway_is_unreachable() -> None:
    class _Down(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("gateway offline", request=request)

    adapter = _adapter_with(_Down())

    assert asyncio.run(adapter.run_graph_query("MATCH (n) RETURN n")) is None


def test_run_graph_query_returns_none_for_an_empty_result() -> None:
    transport = _RecordingTransport(
        {"status": "success", "result": {"evidence_spans": []}}
    )
    adapter = _adapter_with(transport)

    assert asyncio.run(adapter.run_graph_query("MATCH (n) RETURN n")) is None
    assert len(transport.requests) == 1


@pytest.mark.parametrize("route", ["query", "ask-data", "nl-query"])
def test_graph_routes_the_client_will_post_to_are_declared(route: str) -> None:
    """``_graph_post`` refuses any route not in the declared set."""
    from geniusbot.services import gateway_client

    assert route in gateway_client._GRAPH_ROUTES
