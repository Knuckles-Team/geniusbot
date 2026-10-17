"""
CONCEPT:AU-GBOT.cockpit.through-gbot
Single backend adapter seam for GeniusBot.

GeniusBot is a client of arbora. Every qt/* widget and ``geniusbot.py``
routes backend access (graph queries, agent workflow execution, gateway
aggregation/config, centralized log paths) through this facade. Backend calls
go to arbora through :class:`geniusbot.services.gateway_client.GatewayClient`
(built on ``geniusbot.services.gateway_routes``); nothing here imports ``agent_utilities``, and
no agent harness runs in-process.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("geniusbot.backend")


class BackendAdapter:
    """Facade over the GeniusBot backend (arbora gateway).

    All methods are defensive: if a backend is unavailable they fall back to a
    safe default (empty result / sentinel) rather than letting an
    backend import error escape into UI code.
    """

    def __init__(self, gateway_base_url: str = "http://localhost:8000") -> None:
        self._gateway_base_url = gateway_base_url
        self._gateway_client: Any = None

    def _gateway(self) -> Any:
        """The shared :class:`GatewayClient` for this adapter's base URL.

        Built once, lazily — ``gateway_base_url`` was stored by ``__init__``
        and never used by anything before.
        """
        if self._gateway_client is None:
            from geniusbot.services.gateway_client import GatewayClient

            self._gateway_client = GatewayClient(self._gateway_base_url)
        return self._gateway_client

    # ── Paths / telemetry ────────────────────────────────────────────
    @staticmethod
    def resolve_log_dir() -> Path:
        """Resolve the centralized log directory.

        Uses the platformdirs-derived path shared with the rest of the
        ecosystem, with no agent-utilities import. This replaces the duplicated try/except blocks previously scattered across
        ``logger.py``, ``utils.py`` and ``geniusbot.py``.
        """
        import platformdirs

        return Path(platformdirs.user_log_path("agent-utilities", "knuckles-team"))

    # ── Knowledge Graph query ────────────────────────────────────────
    async def run_graph_query(self, query_text: str) -> Any:
        """Execute a read-only Cypher/graph query and return its result rows.

        Goes through the gateway's ``/api/graph/query`` action twin — the REST
        side of the ``graph_query`` MCP tool — like every other backend read in
        this facade.

        It previously did ``from agent_utilities.graph import run_graph_query``,
        a symbol that does not exist in ``agent_utilities.graph`` (which exports
        ``run_graph`` / ``run_graph_stream`` / ``validate_graph`` / builder
        helpers). The ``ImportError`` was caught and logged at DEBUG, so both
        callers — the Graph Explorer and the temporal-graph panel — silently
        fell through to their local simulators on *every* run and never once
        displayed real graph data.

        Returns the result rows, or ``None`` when the gateway is unreachable or
        the query produced none (callers fall back to a local simulator then).
        """
        result = await self._gateway().graph_query(query_text)
        if not isinstance(result, dict) or "error" in result:
            return None
        rows = result.get("evidence_spans")
        return rows if isinstance(rows, list) and rows else None

    # ── Agent workflow execution ─────────────────────────────────────
    async def run_agent_workflow(self, query: str, progress_cb: Any = None) -> Any:
        """Run an agent workflow on arbora and return its result.

        GeniusBot is a client of arbora: the request is sent to the served
        ``/stream`` operation through the gateway client, never executed
        in-process. Raises when arbora is unreachable or produced no output
        so the caller can apply its specialist-response fallback.
        """
        result = await self._gateway().stream_copilot_query(query, progress_cb)
        text = result.get("result", "") if isinstance(result, dict) else ""
        if not text or text.startswith("\u274c"):
            raise RuntimeError("arbora produced no workflow output")
        return result

    # ── Gateway service dashboard ────────────────────────────────────
    def load_service_layout(self) -> Any:
        """Load the service dashboard layout via the gateway ConfigManager.

        Returns the layout object (with ``.groups``) or raises ImportError if
        the gateway config module is unavailable, so the caller can render its
        "gateway not available" placeholder. Other exceptions propagate for
        the caller's error placeholder.
        """
        from arbora.gateway.config import ConfigManager

        return ConfigManager().load()

    def fetch_service_widget_data(self) -> dict:
        """Fetch and serialize all service widget data via the aggregator.

        Runs the gateway :class:`Aggregator` to completion and converts the
        returned ``WidgetData`` objects into plain serializable dicts suitable
        for emitting across a Qt signal. Raises ImportError when the gateway
        module is unavailable (caller surfaces a clear message).
        """
        import asyncio

        from arbora.gateway.aggregator import Aggregator

        aggregator = Aggregator()
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(aggregator.fetch_all())
        finally:
            loop.close()

        result: dict = {}
        for svc_id, wd in data.items():
            fields = []
            if wd.fields:
                for f in wd.fields:
                    fields.append({"label": f.label, "value": str(f.value)})
            result[svc_id] = {
                "status": wd.status,
                "fields": fields,
                "error": wd.error,
            }
        return result


# Module-level singleton — UI code imports this directly.
backend = BackendAdapter()

__all__ = ["BackendAdapter", "backend"]
