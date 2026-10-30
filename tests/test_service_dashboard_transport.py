"""The desktop reads dashboard snapshots over the served client boundary."""

import asyncio

import httpx
import pytest

from axil.services.backend_adapter import BackendAdapter
from axil.services.gateway_client import GatewayClient


@pytest.mark.spec("AXIL-CLIENT-R001.2")
@pytest.mark.asyncio
async def test_dashboard_routes_preserve_headers_and_project_served_values():
    seen = []

    def handler(request):
        seen.append(
            (request.method, request.url.path, request.headers["authorization"])
        )
        if request.url.path.endswith("/layout"):
            return httpx.Response(200, json={"groups": []})
        return httpx.Response(
            200, json={"svc": {"status": "ok", "fields": {"jobs": 4}}}
        )

    client = GatewayClient()
    await client._direct_http.aclose()
    client._direct_http = httpx.AsyncClient(
        base_url=client.base_url,
        transport=httpx.MockTransport(handler),
        headers={"Authorization": "Bearer fixture"},
    )
    adapter = BackendAdapter()
    try:
        assert await adapter.load_service_layout(client) == {"groups": []}
        assert await adapter.fetch_service_widget_data(client) == {
            "svc": {
                "status": "ok",
                "fields": [{"label": "jobs", "value": "4"}],
                "error": None,
            }
        }
    finally:
        await client.aclose()
    assert seen == [
        ("GET", "/api/dashboard/layout", "Bearer fixture"),
        ("GET", "/api/dashboard/data", "Bearer fixture"),
    ]


@pytest.mark.spec("AXIL-CLIENT-R001.2")
@pytest.mark.parametrize("method", ["dashboard_layout", "dashboard_data"])
@pytest.mark.parametrize("status", [301, 302, 303, 307, 308, 401, 403, 500])
@pytest.mark.asyncio
async def test_dashboard_refuses_redirects_and_http_errors(method, status):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status, headers={"Location": "https://other.invalid"}, json={"groups": []}
        )

    client = GatewayClient()
    await client._direct_http.aclose()
    client._direct_http = httpx.AsyncClient(
        base_url=client.base_url, transport=httpx.MockTransport(handler)
    )
    try:
        with pytest.raises(httpx.HTTPStatusError):
            await getattr(client, method)()
    finally:
        await client.aclose()
    assert len(requests) == 1


@pytest.mark.spec("AXIL-CLIENT-R001.2")
@pytest.mark.parametrize(
    "method, body",
    [
        ("dashboard_layout", {}),
        ("dashboard_layout", {"groups": [None]}),
        ("dashboard_layout", {"groups": [{"name": "x", "services": [None]}]}),
        ("dashboard_data", {"error": "denied"}),
        ("dashboard_data", {"svc": {"status": "ok", "fields": []}}),
    ],
)
@pytest.mark.asyncio
async def test_dashboard_refuses_malformed_shapes(method, body):
    client = GatewayClient()
    await client._direct_http.aclose()
    client._direct_http = httpx.AsyncClient(
        base_url=client.base_url,
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body)),
    )
    try:
        with pytest.raises(RuntimeError):
            await getattr(client, method)()
    finally:
        await client.aclose()


@pytest.mark.spec("AXIL-CLIENT-R001.2")
@pytest.mark.asyncio
async def test_snapshot_closes_transport_when_cancelled(monkeypatch):
    entered = asyncio.Event()
    closed = []

    class Client:
        def __init__(self, base_url):
            assert base_url == "http://localhost:8123"

        async def dashboard_layout(self):
            entered.set()
            await asyncio.Event().wait()

        async def aclose(self):
            closed.append(True)

    monkeypatch.setattr("axil.services.gateway_client.GatewayClient", Client)
    task = asyncio.create_task(
        BackendAdapter("http://localhost:8123").service_dashboard_snapshot()
    )
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert closed == [True]


@pytest.mark.spec("AXIL-CLIENT-R001.2")
@pytest.mark.parametrize("method", ["dashboard_layout", "dashboard_data"])
@pytest.mark.parametrize("response_kind", ["oversize", "invalid-json", "typed-failure"])
@pytest.mark.asyncio
async def test_dashboard_rejects_oversize_invalid_and_typed_failure(
    method, response_kind
):
    def handler(request):
        if response_kind == "oversize":
            return httpx.Response(
                200, headers={"Content-Length": str(9 * 1024 * 1024)}, json={}
            )
        if response_kind == "invalid-json":
            return httpx.Response(200, content=b"not JSON")
        return httpx.Response(
            403, json={"status": "failed", "result": {"error": {"code": "denied"}}}
        )

    client = GatewayClient()
    await client._direct_http.aclose()
    client._direct_http = httpx.AsyncClient(
        base_url=client.base_url, transport=httpx.MockTransport(handler)
    )
    try:
        with pytest.raises(RuntimeError):
            await getattr(client, method)()
    finally:
        await client.aclose()
