"""Gateway operation-registry preflight tests (AXIL-CLIENT-R002.2)."""

from __future__ import annotations

import httpx
import pytest

from geniusbot.services.gateway_client import GatewayClient
from geniusbot.services.operation_registry import build_registry

VALID_DIGEST = "a" * 64


class _RecordingTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(
            200,
            json={"status": "success", "result": {"ok": True}},
            request=request,
        )


def _client(transport: _RecordingTransport) -> GatewayClient:
    client = GatewayClient(
        "http://localhost:8000",
        allow_insecure_http=True,
        operation_registry=build_registry(
            [{"operation": "graph.query", "digest": VALID_DIGEST}]
        ),
    )
    client._direct_http = httpx.AsyncClient(
        base_url=client.base_url,
        transport=transport,
    )
    return client


@pytest.mark.spec("AXIL-CLIENT-R002.2")
@pytest.mark.asyncio
async def test_registered_operation_posts_once_after_preflight() -> None:
    transport = _RecordingTransport()
    client = _client(transport)
    try:
        result = await client.invoke_operation(
            "graph.query",
            VALID_DIGEST,
            path="/api/graph/query",
            payload={"cypher": "MATCH (n) RETURN n"},
        )
    finally:
        await client.aclose()

    assert result == {"status": "success", "result": {"ok": True}}
    assert len(transport.requests) == 1


@pytest.mark.spec("AXIL-CLIENT-R002.2")
@pytest.mark.parametrize(
    ("operation", "digest"),
    [
        ("graph.unknown", VALID_DIGEST),
        ("graph.query", "b" * 64),
    ],
)
@pytest.mark.asyncio
async def test_rejected_operation_has_zero_network_effect(
    operation: str, digest: str
) -> None:
    transport = _RecordingTransport()
    client = _client(transport)
    try:
        result = await client.invoke_operation(
            operation,
            digest,
            path="/api/graph/query",
            payload={"cypher": "MATCH (n) RETURN n"},
        )
    finally:
        await client.aclose()

    assert result == {
        "error": "Arbora operation unavailable",
        "code": "CLIENT_UNAVAILABLE",
    }
    assert transport.requests == []
