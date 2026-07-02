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

    # ── Usage / cost / observability (CONCEPT:ECO-4.41) ─────────────────
    async def fetch_usage_summary(self, **f):
        try:
            return await self._sdk.usage_summary(**f)
        except Exception as e:
            logger.warning(f"Usage summary fetch failed: {e}")
            return {}

    async def fetch_usage_by_model(self, **f):
        try:
            return await self._sdk.usage_by_model(**f)
        except Exception as e:
            logger.warning(f"Usage by-model fetch failed: {e}")
            return []

    async def fetch_usage_tools(self, **f):
        try:
            return await self._sdk.analytics_tools(**f)
        except Exception as e:
            logger.warning(f"Usage tools fetch failed: {e}")
            return []

    async def fetch_usage_activity(self, **f):
        try:
            return await self._sdk.analytics_activity(**f)
        except Exception as e:
            logger.warning(f"Usage activity fetch failed: {e}")
            return []

    async def fetch_usage_sessions(self, **f):
        try:
            return await self._sdk.usage_top_sessions(**f)
        except Exception as e:
            logger.warning(f"Usage sessions fetch failed: {e}")
            return []

    async def fetch_usage_traces(self):
        try:
            return await self._sdk.usage_traces()
        except Exception as e:
            logger.warning(f"Usage traces fetch failed: {e}")
            return {"enabled": False, "traces": []}

    async def submit_and_stream_extraction(
        self,
        *,
        text: str = "",
        url: str = "",
        rounds: int = 1,
        dedup: bool = True,
        progress_cb=None,
    ):
        """Submit a fact-extraction job and stream its events (ECO-4.43).

        Each event (round_start|fact|…|job_done) is forwarded to ``progress_cb``
        as a JSON string so the Qt panel can render facts live on the main thread.
        Returns a summary dict; graceful-offline like every facade method.
        """
        import json

        import httpx

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post(
                    f"{self.base_url}/api/enhanced/extract/submit",
                    json={"text": text, "url": url, "rounds": rounds, "dedup": dedup},
                    timeout=15.0,
                )
                resp.raise_for_status()
                sub = resp.json()
                job_id = sub.get("job_id")
                if sub.get("status") != "submitted" or not job_id:
                    return {"status": "unavailable", "message": sub.get("message", "")}

                kept = 0
                async with client.stream(
                    "GET", f"{self.base_url}/api/enhanced/extract/stream/{job_id}"
                ) as stream:
                    async for line in stream.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        try:
                            ev = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
                        if ev.get("type") == "fact" and not ev.get("is_duplicate"):
                            kept += 1
                        if progress_cb:
                            progress_cb(line[6:])
                        if ev.get("type") == "job_done":
                            break
                return {"status": "done", "job_id": job_id, "facts": kept}
        except Exception as e:
            logger.warning(f"Extraction stream failed: {e}")
            return {"status": "error", "message": str(e)}

    async def fetch_extraction_jsonl(self, job_id: str) -> str:
        """Fetch a finished job's facts as JSONL text (upstream parity)."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{self.base_url}/api/enhanced/extract/jsonl/{job_id}"
                )
                resp.raise_for_status()
                return resp.text
        except Exception as e:
            logger.warning(f"JSONL fetch failed: {e}")
            return ""

    # ── Epistemic-graph capability surface (W2) ─────────────────────────
    # Thin POSTs to the gateway's action-routed ``/api/graph/*`` twins — the
    # REST side of the graph-os MCP tools nl_query / ask_data / graph_promql /
    # graph_kvcache / graph_federated_search (backend KG-2.305 / KG-2.308 /
    # KG-2.310). Every call is graceful-offline like the rest of this facade:
    # transport or tool errors collapse to a dict carrying an ``"error"`` key so
    # the Qt event loop never sees an exception from a missing gateway/route.
    async def _graph_post(self, route: str, payload: dict) -> dict:
        """POST ``payload`` to ``/api/graph/{route}`` and unwrap the envelope."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/graph/{route}", json=payload
                )
                resp.raise_for_status()
                env = resp.json()
        except Exception as e:
            logger.warning(f"/api/graph/{route} call failed: {e}")
            return {"error": f"gateway offline or route unavailable: {e}"}
        if isinstance(env, dict) and env.get("status") == "error":
            return {"error": env.get("message", "unknown gateway error")}
        result = env.get("result") if isinstance(env, dict) else env
        return result if isinstance(result, dict) else {"result": result}

    async def ask_data(
        self, question: str, *, dialect: str = "auto", limit: int = 50
    ) -> dict:
        """Answer a natural-language DATA question over the KG (backend KG-2.308).

        Runs the DB-GPT-style multi-step data-analysis agent: schema-link →
        generate a read-only query → execute → self-correct → synthesize an
        answer. Returns answer + auditable query + rows + citations + trace.
        """
        return await self._graph_post(
            "ask-data", {"question": question, "dialect": dialect, "limit": limit}
        )

    async def nl_query(
        self, text: str, *, dialect: str = "auto", execute: bool = True, limit: int = 50
    ) -> dict:
        """Translate NL → one auditable read-only query and run it (backend KG-2.305).

        Set ``execute=False`` to preview the generated query without running it.
        """
        return await self._graph_post(
            "nl-query",
            {"text": text, "dialect": dialect, "execute": execute, "limit": limit},
        )

    async def promql(self, query: str, *, action: str = "instant") -> dict:
        """Query the engine's observability metrics with PromQL (backend KG-2.310)."""
        return await self._graph_post("promql", {"query": query, "action": action})

    async def kvcache_stats(self) -> dict:
        """Shared content-addressed KV-cache occupancy + dedup counters (KG-2.310)."""
        return await self._graph_post("kvcache", {"action": "stats"})

    async def federated_search(
        self, query: str, *, top_k: int = 10, references: str = ""
    ) -> dict:
        """Federated search across registered external graphs (backend KG-2.310)."""
        payload: dict = {"query": query, "top_k": top_k}
        if references:
            payload["references"] = references
        return await self._graph_post("federated-search", payload)

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
