"""
CONCEPT:AU-GBOT.cockpit.through-gbot
Service layer for communicating with the agent-utilities gateway.

Thin geniusbot-facing facade over the shared surface SDK
(:class:`agent_utilities.gateway_client.GatewayClient`, CONCEPT:AU-ECO.interop.gateway-client-sdk) — the
single client every surface uses, so transport/auth/retry live in one place. This
facade preserves geniusbot's graceful-offline contract: every method swallows
transport errors and returns a safe default so the Qt event loop never sees an
exception from a missing gateway.
"""

import json
import logging
import re
from typing import Any
from urllib.parse import urlsplit

import httpx
from agent_utilities.core.http_client import create_async_http_client, is_local_host
from agent_utilities.core.transport_security import resolve_tls_profile
from agent_utilities.gateway_client import GatewayClient as _SdkGatewayClient

logger = logging.getLogger("geniusbot.gateway")

DEFAULT_BASE_URL = "http://localhost:8000"
_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
_MAX_STREAM_EVENTS = 100_000
_MAX_STREAM_LINE_BYTES = 256 * 1024
_SAFE_JOB_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_GRAPH_ROUTES = frozenset(
    {"ask-data", "nl-query", "promql", "kvcache", "federated-search"}
)


class GatewayClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        allow_insecure_http: bool = False,
    ):
        parsed = urlsplit(str(base_url).strip())
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Gateway endpoint is invalid")
        host = parsed.hostname.lower().rstrip(".")
        if (
            parsed.scheme.lower() == "http"
            and not is_local_host(host)
            and not allow_insecure_http
        ):
            raise ValueError("Plaintext gateway transport requires explicit opt-in")

        self.base_url = str(base_url).rstrip("/")
        # One pooled SDK client for the app's lifetime (desktop singleton).
        self._sdk = _SdkGatewayClient(self.base_url, timeout=15.0)
        tls = resolve_tls_profile("GENIUSBOT_GATEWAY")
        self._direct_http = create_async_http_client(
            base_url=self.base_url,
            timeout=httpx.Timeout(120.0, connect=10.0),
            verify=tls.ssl_context,
            pin_egress=True,
            allowed_private_hosts=(host,),
            allow_loopback=True,
            limits=httpx.Limits(max_connections=8, max_keepalive_connections=4),
        )

    @staticmethod
    async def _bounded_body(
        response: httpx.Response, *, limit: int = _MAX_RESPONSE_BYTES
    ) -> bytes:
        declared = response.headers.get("content-length")
        if declared:
            try:
                if int(declared) > limit:
                    raise RuntimeError("Gateway response exceeded its size limit")
            except ValueError as exc:
                raise RuntimeError("Gateway response length was invalid") from exc
        body = bytearray()
        async for chunk in response.aiter_bytes():
            body.extend(chunk)
            if len(body) > limit:
                raise RuntimeError("Gateway response exceeded its size limit")
        return bytes(body)

    async def _json_request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with self._direct_http.stream(
            method, path, json=payload, follow_redirects=False
        ) as response:
            response.raise_for_status()
            body = await self._bounded_body(response)
        try:
            value = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Gateway returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise RuntimeError("Gateway returned an invalid envelope")
        return value

    async def aclose(self) -> None:
        """Release the direct HTTP pool and the shared SDK when supported."""

        await self._direct_http.aclose()
        close = getattr(self._sdk, "aclose", None)
        if callable(close):
            await close()

    async def fetch_specialists(self):
        """Fetch all specialists from the Knowledge Graph via the Gateway."""
        try:
            return await self._sdk.list_agents()
        except Exception as e:
            logger.warning(
                "Failed to fetch specialists: error_type=%s", type(e).__name__
            )
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
            logger.warning(
                "Gateway health check failed: error_type=%s", type(e).__name__
            )
            return {"status": "error", "result": "❌ central Gateway offline."}

    async def fetch_autocomplete_suggestions(self, query: str):
        """Fetch autocomplete suggestions for slash commands."""
        try:
            return await self._sdk.autocomplete(query)
        except Exception as e:
            logger.debug(
                "Autocomplete fetch failed: error_type=%s", type(e).__name__
            )
            return []

    async def execute_slash_command(self, query: str):
        """Execute a slash command on the gateway."""
        try:
            return await self._sdk.execute_command(query)
        except Exception as e:
            return {
                "result": "❌ Gateway connection failed. Falling back to local run "
                "is not supported for slash commands."
            }

    async def fetch_fleet_topology(self):
        """Fetch the fleet/worker placement topology (OS-5.10)."""
        try:
            return await self._sdk.fleet_topology()
        except Exception as e:
            logger.warning(
                "Fleet topology fetch failed: error_type=%s", type(e).__name__
            )
            return {}

    async def fetch_fleet_approvals(self):
        """Fetch pending ActionPolicy approvals awaiting a human decision (OS-5.24)."""
        try:
            return await self._sdk.fleet_approvals()
        except Exception as e:
            logger.warning(
                "Fleet approvals fetch failed: error_type=%s", type(e).__name__
            )
            return []

    async def grant_approval(self, approval_id: str):
        """Grant a pending fleet approval by id."""
        try:
            return await self._sdk.grant_approval(approval_id)
        except Exception as e:
            logger.warning("Grant approval failed: error_type=%s", type(e).__name__)
            return {"error": "Approval request failed"}

    # ── Usage / cost / observability (CONCEPT:AU-ECO.mcp.usage-cost-observability-surface) ─────────────────
    async def fetch_usage_summary(self, **f):
        try:
            return await self._sdk.usage_summary(**f)
        except Exception as e:
            logger.warning(
                "Usage summary fetch failed: error_type=%s", type(e).__name__
            )
            return {}

    async def fetch_usage_by_model(self, **f):
        try:
            return await self._sdk.usage_by_model(**f)
        except Exception as e:
            logger.warning(
                "Usage by-model fetch failed: error_type=%s", type(e).__name__
            )
            return []

    async def fetch_usage_tools(self, **f):
        try:
            return await self._sdk.analytics_tools(**f)
        except Exception as e:
            logger.warning(
                "Usage tools fetch failed: error_type=%s", type(e).__name__
            )
            return []

    async def fetch_usage_activity(self, **f):
        try:
            return await self._sdk.analytics_activity(**f)
        except Exception as e:
            logger.warning(
                "Usage activity fetch failed: error_type=%s", type(e).__name__
            )
            return []

    async def fetch_usage_sessions(self, **f):
        try:
            return await self._sdk.usage_top_sessions(**f)
        except Exception as e:
            logger.warning(
                "Usage sessions fetch failed: error_type=%s", type(e).__name__
            )
            return []

    async def fetch_usage_traces(self):
        try:
            return await self._sdk.usage_traces()
        except Exception as e:
            logger.warning(
                "Usage traces fetch failed: error_type=%s", type(e).__name__
            )
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
        try:
            if len(text.encode("utf-8")) > 4 * 1024 * 1024 or len(url) > 8_192:
                raise ValueError("Extraction request exceeded its size limit")
            if not 1 <= int(rounds) <= 100:
                raise ValueError("Extraction rounds are outside the allowed range")
            sub = await self._json_request(
                "POST",
                "/api/enhanced/extract/submit",
                payload={
                    "text": text,
                    "url": url,
                    "rounds": int(rounds),
                    "dedup": bool(dedup),
                },
            )
            job_id = sub.get("job_id")
            if (
                sub.get("status") != "submitted"
                or not isinstance(job_id, str)
                or not _SAFE_JOB_ID.fullmatch(job_id)
            ):
                return {"status": "unavailable", "message": "Request unavailable"}

            kept = 0
            event_count = 0
            async with self._direct_http.stream(
                "GET",
                f"/api/enhanced/extract/stream/{job_id}",
                follow_redirects=False,
            ) as stream:
                stream.raise_for_status()
                async for line in stream.aiter_lines():
                    event_count += 1
                    if event_count > _MAX_STREAM_EVENTS:
                        raise RuntimeError("Gateway event stream exceeded its limit")
                    if len(line.encode("utf-8")) > _MAX_STREAM_LINE_BYTES:
                        raise RuntimeError("Gateway event exceeded its size limit")
                    if not line.startswith("data: "):
                        continue
                    try:
                        ev = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(ev, dict):
                        continue
                    if ev.get("type") == "fact" and not ev.get("is_duplicate"):
                        kept += 1
                    if progress_cb:
                        progress_cb(line[6:])
                    if ev.get("type") == "job_done":
                        break
            return {"status": "done", "job_id": job_id, "facts": kept}
        except Exception as e:
            logger.warning(
                "Extraction stream failed: error_type=%s", type(e).__name__
            )
            return {"status": "error", "message": "Extraction stream failed"}

    async def fetch_extraction_jsonl(self, job_id: str) -> str:
        """Fetch a finished job's facts as JSONL text (upstream parity)."""
        try:
            if not _SAFE_JOB_ID.fullmatch(str(job_id)):
                raise ValueError("Extraction job id is invalid")
            async with self._direct_http.stream(
                "GET",
                f"/api/enhanced/extract/jsonl/{job_id}",
                follow_redirects=False,
            ) as response:
                response.raise_for_status()
                body = await self._bounded_body(response)
            return body.decode("utf-8")
        except Exception as e:
            logger.warning("JSONL fetch failed: error_type=%s", type(e).__name__)
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
        try:
            if route not in _GRAPH_ROUTES:
                raise ValueError("Gateway graph route is invalid")
            env = await self._json_request(
                "POST", f"/api/graph/{route}", payload=payload
            )
        except Exception as e:
            logger.warning("Graph request failed: error_type=%s", type(e).__name__)
            return {"error": "gateway offline or route unavailable"}
        if isinstance(env, dict) and env.get("status") == "error":
            return {"error": "gateway graph request failed"}
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
            logger.warning(
                "Gateway SSE execution failed: error_type=%s", type(e).__name__
            )

        return {
            "result": "❌ Gateway is offline. Please make sure the agent-utilities gateway is running at http://localhost:8000."
        }
