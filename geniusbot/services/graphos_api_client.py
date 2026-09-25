"""Versioned GraphOS operation and A2A approval client for GeniusBot.

The desktop UI supplies a caller credential. This client has no local authority
fallback: an unserved operation or malformed response is a refusal.
"""

from __future__ import annotations

import uuid
from typing import Any
from urllib.parse import quote, urlsplit

import httpx


class GraphOSOperationError(RuntimeError):
    """A versioned GraphOS operation was refused."""

    def __init__(self, code: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.details = details or {}


class GraphOSAPIClient:
    """Small HTTP/A2A transport until MCPI-25 emits the shared Python client."""

    def __init__(self, base_url: str, bearer_token: str) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("invalid GraphOS endpoint")
        if parsed.scheme == "http" and parsed.hostname not in {
            "localhost", "127.0.0.1", "::1"
        }:
            raise ValueError("remote GraphOS endpoint requires TLS")
        if not bearer_token:
            raise ValueError("caller credential is required")
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {bearer_token}"}, timeout=30.0
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def invoke(
        self,
        op: str,
        params: dict[str, Any],
        *,
        plan_ref: str | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        """Invoke an op and preserve the server's explicit refusal code."""
        if not op or not isinstance(params, dict):
            raise ValueError("operation id and object params are required")
        headers = {"Idempotency-Key": idempotency_key or uuid.uuid4().hex}
        if plan_ref:
            headers["GraphOS-Plan-Ref"] = plan_ref
        response = await self._http.post(
            f"{self.base_url}/api/v1/ops/{quote(op, safe='.')}",
            json=params,
            headers=headers,
        )
        body = response.json()
        if not isinstance(body, dict) or not isinstance(body.get("ok"), bool):
            raise GraphOSOperationError("INVALID_ENVELOPE")
        if not body["ok"]:
            error = body.get("error")
            code = error.get("code") if isinstance(error, dict) else None
            details = error.get("details") if isinstance(error, dict) else None
            raise GraphOSOperationError(
                code if isinstance(code, str) else "UNKNOWN",
                details if isinstance(details, dict) else None,
            )
        response.raise_for_status()
        return body.get("result")

    async def confirm_plan(
        self,
        *,
        plan_ref: str,
        op: str,
        params: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> Any:
        """Confirm a PLAN-bound action through the caller's A2A session."""
        if not plan_ref or not op or not isinstance(params, dict):
            raise ValueError("complete plan binding is required")
        response = await self._http.post(
            f"{self.base_url}/a2a",
            json={
                "jsonrpc": "2.0",
                "id": uuid.uuid4().hex,
                "method": "graphos.plan/confirm",
                "params": {
                    "plan_ref": plan_ref,
                    "op": op,
                    "params": params,
                    "idempotency_key": idempotency_key or uuid.uuid4().hex,
                },
            },
        )
        body = response.json()
        if not isinstance(body, dict):
            raise GraphOSOperationError("INVALID_ENVELOPE")
        error = body.get("error")
        if isinstance(error, dict):
            data = error.get("data")
            code = data.get("code") if isinstance(data, dict) else None
            raise GraphOSOperationError(code if isinstance(code, str) else "UNKNOWN")
        response.raise_for_status()
        if "result" not in body:
            raise GraphOSOperationError("INVALID_ENVELOPE")
        return body["result"]
