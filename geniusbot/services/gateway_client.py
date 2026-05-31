"""
CONCEPT:GBOT-6.0
Service layer for communicating with the agent-utilities gateway.
"""

import json
import logging

import httpx

logger = logging.getLogger("geniusbot.gateway")


class GatewayClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    async def fetch_specialists(self):
        """Fetch all specialists from the Knowledge Graph via the Gateway."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/enhanced/agents", timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        return data.get("agents", [])
        except Exception as e:
            logger.warning(f"Failed to fetch specialists from gateway: {e}")
        return []

    async def run_health_check(self):
        """Run health check against the centralized Gateway."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/enhanced/maintenance/status",
                    timeout=5.0,
                )
                if response.status_code == 200:
                    data = response.json()
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
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/enhanced/commands/autocomplete?query={query}",
                    timeout=3.0,
                )
                if response.status_code == 200:
                    return response.json().get("suggestions", [])
        except Exception as e:
            logger.debug(f"Autocomplete fetch failed: {e}")
        return []

    async def execute_slash_command(self, query: str):
        """Execute a slash command on the gateway."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/enhanced/commands/execute",
                    json={"command": query},
                    timeout=15.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "result": data.get("response_markdown", ""),
                        "client_actions": data.get("client_actions", []),
                    }
                else:
                    return {
                        "result": f"❌ Gateway command error: Code {response.status_code}"
                    }
        except Exception as e:
            return {
                "result": f"❌ Gateway connection failed: {e}. Falling back to local run is not supported for slash commands."
            }

    async def stream_copilot_query(self, query: str, progress_cb=None):
        """Execute master copilot query with streaming output."""
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/stream",
                    json={"query": query, "mode": "ask", "topology": "basic"},
                    timeout=60.0,
                ) as stream:
                    final_output = ""
                    async for line in stream.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event = json.loads(line[6:])
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
                            except Exception:
                                continue
                    if final_output:
                        return {"result": final_output}
        except Exception as e:
            logger.warning(f"Gateway SSE execution failed: {e}")

        return {
            "result": "❌ Gateway is offline. Please make sure the agent-utilities gateway is running at http://localhost:8000."
        }
