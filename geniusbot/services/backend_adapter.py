"""
CONCEPT:AU-GBOT.cockpit.through-gbot
Single backend adapter seam for GeniusBot.

This module is the ONLY place in the geniusbot package that is permitted to
import from ``agent_utilities``. Every qt/* widget and ``geniusbot.py`` must
route backend access (graph queries, workspace graph execution, gateway
aggregation/config, centralized log paths) through this facade instead of
reaching into ``agent_utilities`` engine internals directly.

Design:
  * Where the centralized HTTP gateway exposes an equivalent method, the
    adapter prefers :class:`geniusbot.services.gateway_client.GatewayClient`.
  * Where no gateway endpoint exists yet, the adapter lazily imports the
    ``agent_utilities`` engine *inside the relevant method only*, so the
    coupling stays confined to this file and degrades gracefully (returns a
    fallback / raises a clear error) when ``agent_utilities`` is not installed.

Keeping all of this behind one class makes the backend a single swappable
seam: a future ACP-SDK / pure-HTTP backend can replace the lazy engine
imports here without touching any UI code.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("geniusbot.backend")


class BackendAdapter:
    """Facade over the GeniusBot backend (agent-utilities engine + gateway).

    All methods are defensive: if a backend is unavailable they fall back to a
    safe default (empty result / sentinel) rather than letting an
    ``agent_utilities`` import error escape into UI code.
    """

    def __init__(self, gateway_base_url: str = "http://localhost:8000") -> None:
        self._gateway_base_url = gateway_base_url

    # ── Paths / telemetry ────────────────────────────────────────────
    @staticmethod
    def resolve_log_dir() -> Path:
        """Resolve the centralized log directory.

        Prefers ``agent_utilities.core.paths.log_dir`` and falls back to a
        platformdirs-derived path when agent-utilities is not installed. This
        replaces the duplicated try/except blocks previously scattered across
        ``logger.py``, ``utils.py`` and ``geniusbot.py``.
        """
        try:
            from agent_utilities.core.paths import log_dir

            return log_dir()
        except Exception:  # ImportError or any engine-side failure
            import platformdirs

            return Path(platformdirs.user_log_path("agent-utilities", "knuckles-team"))

    # ── Knowledge Graph query ────────────────────────────────────────
    async def run_graph_query(self, query_text: str) -> Any:
        """Execute a Cypher/graph query against the agent-utilities engine.

        Returns the engine result, or ``None`` if the engine is unavailable
        or the query produced no result (callers fall back to a local
        simulator in that case).
        """
        try:
            from agent_utilities.graph import run_graph_query

            return await run_graph_query(query_text)
        except Exception as exc:  # ImportError or runtime failure
            logger.debug("Operation failed: error_type=%s", type(exc).__name__)
            return None

    # ── Workspace graph execution ────────────────────────────────────
    async def run_workspace_graph(self, query: str, config: dict | None = None) -> Any:
        """Initialize the workspace graph and run it for a query.

        Mirrors the previous inline behaviour in ``widget_mapper.py``:
        initialize the workspace, build the graph from the workspace and run
        it. Raises on failure so the caller can apply its specialist-response
        fallback (the caller already wraps this in try/except).
        """
        from agent_utilities import initialize_workspace
        from agent_utilities.graph import (
            initialize_graph_from_workspace,
            run_graph,
        )

        if config is None:
            config = {
                "agent_model": "gemini-2.5-flash",
                "router_model": "gemini-2.5-flash",
            }

        initialize_workspace()
        graph = initialize_graph_from_workspace()
        return await run_graph(graph, config, query)

    # ── Gateway service dashboard ────────────────────────────────────
    def load_service_layout(self) -> Any:
        """Load the service dashboard layout via the gateway ConfigManager.

        Returns the layout object (with ``.groups``) or raises ImportError if
        the gateway config module is unavailable, so the caller can render its
        "gateway not available" placeholder. Other exceptions propagate for
        the caller's error placeholder.
        """
        from agent_utilities.gateway.config import ConfigManager

        return ConfigManager().load()

    def fetch_service_widget_data(self) -> dict:
        """Fetch and serialize all service widget data via the aggregator.

        Runs the gateway :class:`Aggregator` to completion and converts the
        returned ``WidgetData`` objects into plain serializable dicts suitable
        for emitting across a Qt signal. Raises ImportError when the gateway
        module is unavailable (caller surfaces a clear message).
        """
        import asyncio

        from agent_utilities.gateway.aggregator import Aggregator

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
