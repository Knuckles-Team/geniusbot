"""Typed access to the Arbora gateway's REST routes and its ``/stream`` channel.

Arbora 0.1.2 no longer publishes a hand-written gateway client (its generated
operation client replaced it), so GeniusBot keeps the few route calls its
desktop panels use here. Each method unwraps the JSON body and returns a safe
empty value when the gateway answers with an unexpected shape. Transport and
HTTP errors raise; :class:`geniusbot.services.gateway_client.GatewayClient`
catches them and returns typed offline results to the UI.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

DEFAULT_GATEWAY_URL = "http://localhost:8000"


class GatewayRoutes:
    """Async client for the gateway REST and SSE routes the desktop panels call."""

    def __init__(
        self,
        base_url: str = DEFAULT_GATEWAY_URL,
        *,
        timeout: float = 30.0,
        verify: Any = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify,
            transport=transport,
            follow_redirects=False,
        )

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = await self._http.get(path, params=params or None)
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, payload: dict[str, Any]) -> Any:
        response = await self._http.post(path, json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _as_dict(body: Any) -> dict[str, Any]:
        return body if isinstance(body, dict) else {}

    @staticmethod
    def _as_list(body: Any) -> list[dict[str, Any]]:
        return body if isinstance(body, list) else []

    async def list_agents(self) -> list[dict[str, Any]]:
        body = await self._get("/api/enhanced/agents")
        if isinstance(body, dict) and body.get("status") == "ok":
            return list(body.get("agents", []))
        return []

    async def maintenance_status(self) -> dict[str, Any]:
        return self._as_dict(await self._get("/api/enhanced/maintenance/status"))

    async def autocomplete(self, query: str) -> list[str]:
        body = await self._get("/api/enhanced/commands/autocomplete", {"query": query})
        return list(body.get("suggestions", [])) if isinstance(body, dict) else []

    async def execute_command(self, command: str) -> dict[str, Any]:
        body = await self._post("/api/enhanced/commands/execute", {"command": command})
        if not isinstance(body, dict):
            return {"result": ""}
        return {
            "result": body.get("response_markdown", ""),
            "client_actions": body.get("client_actions", []),
        }

    async def fleet_topology(self) -> dict[str, Any]:
        return self._as_dict(await self._get("/api/fleet/topology"))

    async def fleet_approvals(self) -> list[dict[str, Any]]:
        body = await self._get("/api/fleet/approvals")
        if isinstance(body, dict):
            return list(body.get("approvals", []))
        return self._as_list(body)

    async def grant_approval(self, approval_id: str) -> dict[str, Any]:
        return self._as_dict(
            await self._post("/api/fleet/approvals/grant", {"approval_id": approval_id})
        )

    async def usage_summary(self, **filters: Any) -> dict[str, Any]:
        return self._as_dict(await self._get("/api/observability/summary", filters))

    async def usage_by_model(self, **filters: Any) -> list[dict[str, Any]]:
        return self._as_list(await self._get("/api/observability/by-model", filters))

    async def analytics_tools(self, **filters: Any) -> list[dict[str, Any]]:
        return self._as_list(
            await self._get("/api/observability/analytics/tools", filters)
        )

    async def analytics_activity(self, **filters: Any) -> list[dict[str, Any]]:
        return self._as_list(
            await self._get("/api/observability/analytics/activity", filters)
        )

    async def usage_top_sessions(
        self, *, limit: int = 20, **filters: Any
    ) -> list[dict[str, Any]]:
        return self._as_list(
            await self._get(
                "/api/observability/top-sessions", {"limit": limit, **filters}
            )
        )

    async def usage_traces(self, **filters: Any) -> dict[str, Any]:
        body = await self._get("/api/observability/traces", filters)
        return body if isinstance(body, dict) else {"enabled": False, "traces": []}

    async def stream(
        self,
        query: str,
        *,
        mode: str = "ask",
        topology: str = "basic",
        timeout: float = 120.0,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream an agent run over ``/stream``, yielding each parsed SSE event."""
        async with self._http.stream(
            "POST",
            "/stream",
            json={"query": query, "mode": mode, "topology": topology},
            timeout=timeout,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                try:
                    yield json.loads(line[6:])
                except json.JSONDecodeError:
                    continue

    async def aclose(self) -> None:
        await self._http.aclose()
