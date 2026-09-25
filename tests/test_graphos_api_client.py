"""Focused contract tests for the desktop GraphOS client."""

import json

import httpx
import pytest

from geniusbot.services.graphos_api_client import (
    GraphOSAPIClient,
    GraphOSOperationError,
)


@pytest.mark.asyncio
async def test_invoke_sends_versioned_op_and_returns_result():
    seen = []

    def reply(request):
        seen.append(request)
        return httpx.Response(200, json={"ok": True, "result": {"rows": [1]}})

    client = GraphOSAPIClient("http://localhost:8000", "caller-token")
    await client._http.aclose()
    client._http = httpx.AsyncClient(
        transport=httpx.MockTransport(reply),
        headers={"Authorization": "Bearer caller-token"},
    )
    assert await client.invoke("query.uql", {"query": "MATCH ()"}) == {"rows": [1]}
    assert seen[0].url.path == "/api/v1/ops/query.uql"
    assert seen[0].headers["Authorization"] == "Bearer caller-token"
    assert seen[0].headers["Idempotency-Key"]
    await client.aclose()


@pytest.mark.asyncio
async def test_console_refusal_is_not_confirmed_locally():
    def reply(request):
        return httpx.Response(
            428,
            json={
                "ok": False,
                "error": {
                    "code": "STEP_UP_REQUIRED",
                    "details": {"console_url": "/console/confirm/ref"},
                },
            },
        )

    client = GraphOSAPIClient("http://localhost:8000", "caller-token")
    await client._http.aclose()
    client._http = httpx.AsyncClient(
        transport=httpx.MockTransport(reply),
        headers={"Authorization": "Bearer caller-token"},
    )
    with pytest.raises(GraphOSOperationError) as caught:
        await client.invoke("approvals.grant", {"approval_id": "a1"})
    assert caught.value.code == "STEP_UP_REQUIRED"
    assert caught.value.details["console_url"] == "/console/confirm/ref"
    await client.aclose()


@pytest.mark.asyncio
async def test_plan_confirm_carries_exact_binding():
    seen = []

    def reply(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, json={"jsonrpc": "2.0", "result": {"done": True}})

    client = GraphOSAPIClient("http://localhost:8000", "caller-token")
    await client._http.aclose()
    client._http = httpx.AsyncClient(
        transport=httpx.MockTransport(reply),
        headers={"Authorization": "Bearer caller-token"},
    )
    assert await client.confirm_plan(
        plan_ref="p1", op="query.uql", params={"query": "MATCH ()"}
    ) == {"done": True}
    assert seen[0]["method"] == "graphos.plan/confirm"
    assert seen[0]["params"]["params"] == {"query": "MATCH ()"}
    await client.aclose()


def test_remote_plaintext_and_missing_identity_fail_closed():
    with pytest.raises(ValueError):
        GraphOSAPIClient("http://remote.example:8000", "token")
    with pytest.raises(ValueError):
        GraphOSAPIClient("https://remote.example", "")
