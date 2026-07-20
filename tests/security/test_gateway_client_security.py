from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

import httpx
import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "geniusbot"
    / "services"
    / "gateway_client.py"
)
_SPEC = importlib.util.spec_from_file_location("gateway_client_security_target", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
GatewayClient = _MODULE.GatewayClient


class _Stream(httpx.AsyncByteStream):
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    async def __aiter__(self):
        for chunk in self._chunks:
            yield chunk


@pytest.mark.parametrize(
    "url",
    [
        "file:///tmp/gateway",
        "https://user:secret@example.test",
        "https://example.test/path?secret=value",
        "http://example.test",
    ],
)
def test_gateway_rejects_unsafe_endpoint_configuration(url: str) -> None:
    with pytest.raises(ValueError):
        GatewayClient(url)


def test_gateway_bounded_body_rejects_stream_over_limit() -> None:
    response = httpx.Response(200, stream=_Stream([b"1234", b"5678"]))

    with pytest.raises(RuntimeError, match="size limit"):
        asyncio.run(GatewayClient._bounded_body(response, limit=7))


def test_gateway_bounded_body_rejects_declared_oversize() -> None:
    response = httpx.Response(
        200,
        headers={"content-length": "9"},
        stream=_Stream([]),
    )

    with pytest.raises(RuntimeError, match="size limit"):
        asyncio.run(GatewayClient._bounded_body(response, limit=8))
