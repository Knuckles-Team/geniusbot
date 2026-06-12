"""
CONCEPT:GBOT-6.0
Service layer for communicating with the agent-utilities gateway.

Thin geniusbot-facing facade over the shared surface SDK
(:class:`agent_utilities.gateway_client.GatewayClient`, CONCEPT:ECO-4.37) — the
single client every surface uses, so transport/auth/retry live in one place. This
facade preserves geniusbot's graceful-offline contract: every method swallows
transport errors and returns a safe default so the Qt event loop never sees an
exception from a missing gateway.
"""

import logging

from agent_utilities.gateway_client import GatewayClient as _SdkGatewayClient

logger = logging.getLogger("geniusbot.gateway")

DEFAULT_BASE_URL = "http://localhost:8000"


class GatewayClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        # One pooled SDK client for the app's lifetime (desktop singleton).
        self._sdk = _SdkGatewayClient(base_url, timeout=15.0)

    async def fetch_specialists(self):
        """Fetch all specialists from the Knowledge Graph via the Gateway."""
        try:
            return await self._sdk.list_agents()
        except Exception as e:
            logger.warning(f"Failed to fetch specialists from gateway: {e}")
            return []

    async def run_health_check(self):
        """Run health check against the centralized Gateway."""
        try:
            data = await self._sdk.maintenance_status()
            return {
                "status": "success",
                "result": f"Gateway healthy. Maintenance Required: {data.get('maintenance_required', False)}",
            }
        except Exception as e:
            logger.warning(f"Gateway health check failed: {e}")
            return {"status": "error", "result": "❌ central Gateway offline."}

    async def fetch_autocomplete_suggestions(self, query: str):
        """Fetch autocomplete suggestions for slash commands."""
        try:
            return await self._sdk.autocomplete(query)
        except Exception as e:
            logger.debug(f"Autocomplete fetch failed: {e}")
            return []

    async def execute_slash_command(self, query: str):
        """Execute a slash command on the gateway."""
        try:
            return await self._sdk.execute_command(query)
        except Exception as e:
            return {
                "result": f"❌ Gateway connection failed: {e}. Falling back to local run is not supported for slash commands."
            }

    async def fetch_fleet_topology(self):
        """Fetch the fleet/worker placement topology (OS-5.10)."""
        try:
            return await self._sdk.fleet_topology()
        except Exception as e:
            logger.warning(f"Fleet topology fetch failed: {e}")
            return {}

    async def fetch_fleet_approvals(self):
        """Fetch pending ActionPolicy approvals awaiting a human decision (OS-5.24)."""
        try:
            return await self._sdk.fleet_approvals()
        except Exception as e:
            logger.warning(f"Fleet approvals fetch failed: {e}")
            return []

    async def grant_approval(self, approval_id: str):
        """Grant a pending fleet approval by id."""
        try:
            return await self._sdk.grant_approval(approval_id)
        except Exception as e:
            logger.warning(f"Grant approval failed: {e}")
            return {"error": str(e)}

    async def stream_copilot_query(self, query: str, progress_cb=None):
        """Execute master copilot query with streaming output."""
        try:
            final_output = ""
            async for event in self._sdk.stream(
                query, mode="ask", topology="basic", timeout=60.0
            ):
                ev_type = event.get("type")
                if ev_type == "final_output":
                    final_output = event.get("content", "")
                elif ev_type == "thought" and progress_cb:
                    progress_cb(f"💭 {event.get('thought', '')}")
                elif ev_type == "call_tool" and progress_cb:
                    progress_cb(f"🛠️ Tool: {event.get('tool', '')}")
                elif progress_cb:
                    progress_cb(
                        f"📡 {ev_type}: {event.get('message', '') or event.get('error', '')}"
                    )
            if final_output:
                return {"result": final_output}
        except Exception as e:
            logger.warning(f"Gateway SSE execution failed: {e}")

        return {
            "result": "❌ Gateway is offline. Please make sure the agent-utilities gateway is running at http://localhost:8000."
        }
