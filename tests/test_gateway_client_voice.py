"""Tests for GatewayClient.transcribe_voice (CONCEPT:AU-ECO.mcp.webui-voice-transcription-delegation).

Exercises the real request-building path (multipart ``files=``) against an
``httpx.MockTransport`` double, so these prove the ACTUAL HTTP shape sent,
not just that some method was called.
"""

from __future__ import annotations

import json

import httpx
import pytest

from geniusbot.services.gateway_client import GatewayClient


def _client_with_transport(handler) -> GatewayClient:
    client = GatewayClient("http://localhost:8000", allow_insecure_http=True)
    client._direct_http = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://localhost:8000"
    )
    return client


@pytest.mark.asyncio
async def test_transcribe_voice_posts_multipart_and_returns_text() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["content_type"] = request.headers.get("content-type", "")
        captured["body"] = request.read()
        return httpx.Response(200, json={"text": "hello from the mic"})

    client = _client_with_transport(handler)
    result = await client.transcribe_voice(b"raw-wav-bytes", content_type="audio/wav")

    assert result == {"text": "hello from the mic"}
    assert captured["method"] == "POST"
    assert captured["path"] == "/api/enhanced/voice/transcribe"
    assert captured["content_type"].startswith("multipart/form-data")
    assert b"raw-wav-bytes" in captured["body"]


@pytest.mark.asyncio
async def test_transcribe_voice_marks_501_as_unavailable_not_a_generic_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(501, json={"detail": "Capability is not available"})

    client = _client_with_transport(handler)
    result = await client.transcribe_voice(b"clip")

    assert result == {
        "error": "voice transcription is not enabled on this server",
        "unavailable": True,
    }


@pytest.mark.asyncio
async def test_transcribe_voice_marks_404_as_unavailable_too() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Not Found"})

    client = _client_with_transport(handler)
    result = await client.transcribe_voice(b"clip")

    assert result["unavailable"] is True


@pytest.mark.asyncio
async def test_transcribe_voice_reports_a_genuine_error_distinctly() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "Transcription failed"})

    client = _client_with_transport(handler)
    result = await client.transcribe_voice(b"clip")

    assert "error" in result
    assert "unavailable" not in result


@pytest.mark.asyncio
async def test_transcribe_voice_rejects_oversize_clip_without_a_network_call() -> None:
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json={"text": "should not get here"})

    client = _client_with_transport(handler)
    result = await client.transcribe_voice(b"x" * (25 * 1024 * 1024 + 1))

    assert "error" in result
    assert called is False


@pytest.mark.asyncio
async def test_transcribe_voice_never_raises_on_transport_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = _client_with_transport(handler)
    result = await client.transcribe_voice(b"clip")

    assert result == {"error": "voice transcription failed"}
