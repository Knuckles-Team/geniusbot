"""Characterization tests for GatewayClient.stream_copilot_query.

Exercises the real event-dispatch path against a fake async generator
standing in for the SDK's ``stream()``, so these prove event-type routing
(final_output / thought / call_tool / other) and the graceful-offline
fallback, ahead of a cyc/cog refactor (CX wD10-c-misc).
"""

from __future__ import annotations

import pytest

from geniusbot.services.gateway_client import GatewayClient


def _client() -> GatewayClient:
    return GatewayClient("http://localhost:8000", allow_insecure_http=True)


async def _events(*evs):
    for ev in evs:
        yield ev


@pytest.mark.spec("GENIUSBOT-CLIENT-R005")
@pytest.mark.asyncio
async def test_stream_copilot_query_returns_final_output_and_progress() -> None:
    client = _client()
    client._sdk.stream = lambda *a, **k: _events(
        {"type": "thought", "thought": "thinking"},
        {"type": "call_tool", "tool": "search"},
        {"type": "custom_event", "message": "doing a thing"},
        {"type": "final_output", "content": "the answer"},
    )
    seen: list[str] = []
    result = await client.stream_copilot_query("hi", progress_cb=seen.append)

    assert result == {"result": "the answer"}
    assert seen == [
        "💭 thinking",
        "🛠️ Tool: search",
        "📡 custom_event: doing a thing",
    ]


@pytest.mark.spec("GENIUSBOT-CLIENT-R005")
@pytest.mark.asyncio
async def test_stream_copilot_query_final_output_event_does_not_call_progress_cb() -> (
    None
):
    client = _client()
    client._sdk.stream = lambda *a, **k: _events(
        {"type": "final_output", "content": "x"}
    )
    seen: list[str] = []
    result = await client.stream_copilot_query("hi", progress_cb=seen.append)

    assert result == {"result": "x"}
    assert seen == []


@pytest.mark.spec("GENIUSBOT-CLIENT-R005")
@pytest.mark.asyncio
async def test_stream_copilot_query_no_progress_cb_does_not_raise() -> None:
    client = _client()
    client._sdk.stream = lambda *a, **k: _events(
        {"type": "thought", "thought": "t"}, {"type": "final_output", "content": "y"}
    )
    result = await client.stream_copilot_query("hi")
    assert result == {"result": "y"}


@pytest.mark.asyncio
async def test_stream_copilot_query_falls_back_when_no_final_output() -> None:
    client = _client()
    client._sdk.stream = lambda *a, **k: _events({"type": "thought", "thought": "t"})
    result = await client.stream_copilot_query("hi")
    assert result == {
        "result": "❌ Gateway is offline. Please make sure the agent-utilities gateway is running at http://localhost:8000."
    }


@pytest.mark.asyncio
async def test_stream_copilot_query_falls_back_on_exception() -> None:
    client = _client()

    async def _boom(*a, **k):
        raise RuntimeError("gateway down")
        yield  # pragma: no cover - never reached; keeps this an async generator

    client._sdk.stream = _boom
    result = await client.stream_copilot_query("hi")
    assert result == {
        "result": "❌ Gateway is offline. Please make sure the agent-utilities gateway is running at http://localhost:8000."
    }
