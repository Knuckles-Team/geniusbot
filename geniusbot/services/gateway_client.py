"""
CONCEPT:AU-GBOT.cockpit.through-gbot
Service layer for communicating with the arbora gateway.

Thin geniusbot-facing facade over the gateway routes in
:class:`geniusbot.services.gateway_routes.GatewayRoutes`, so transport lives in
one place. This
facade preserves geniusbot's graceful-offline contract: every method swallows
transport errors and returns a safe default so the Qt event loop never sees an
exception from a missing gateway.
"""

import ipaddress
import json
import logging
import os
import re
import ssl
from typing import Any
from urllib.parse import urlsplit

import httpx

from geniusbot.services.gateway_routes import GatewayRoutes
from geniusbot.services.operation_registry import (
    OperationRegistry,
    OperationRegistryError,
)

logger = logging.getLogger("geniusbot.gateway")

DEFAULT_BASE_URL = "http://localhost:8000"
_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
_MAX_STREAM_EVENTS = 100_000
_MAX_STREAM_LINE_BYTES = 256 * 1024
_SAFE_JOB_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_GRAPH_ROUTES = frozenset(
    {"ask-data", "nl-query", "promql", "kvcache", "federated-search", "query"}
)


def is_local_host(host: str) -> bool:
    """True for loopback hosts, where plaintext HTTP is acceptable."""
    host = host.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _tls_verify() -> ssl.SSLContext | bool:
    """Verify gateway TLS, trusting ``GENIUSBOT_GATEWAY_CA_BUNDLE`` when set."""
    bundle = os.environ.get("GENIUSBOT_GATEWAY_CA_BUNDLE", "").strip()
    return ssl.create_default_context(cafile=bundle) if bundle else True


def _decode_envelope(body: bytes) -> dict[str, Any] | None:
    """The gateway's JSON object envelope, or ``None`` when the body is not one."""
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _is_failed_envelope(value: dict[str, Any] | None) -> bool:
    """``{"status": "failed", "result": {...error...}}`` from a REST tool twin."""
    return (
        value is not None
        and value.get("status") == "failed"
        and isinstance(value.get("result"), dict)
        and "error" in value["result"]
    )


class GatewayClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        allow_insecure_http: bool = False,
        operation_registry: OperationRegistry | None = None,
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
        # The application loads the installed generated registry once and injects
        # the same immutable view into its gateway client. Direct test/utility
        # clients may omit it until they opt into a registered operation call.
        self.operation_registry = operation_registry
        # One pooled SDK client for the app's lifetime (desktop singleton).
        self._sdk = GatewayRoutes(self.base_url, timeout=15.0, verify=_tls_verify())
        self._direct_http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(120.0, connect=10.0),
            verify=_tls_verify(),
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
        operation: str | None = None,
        digest: str | None = None,
    ) -> dict[str, Any]:
        if operation is not None or digest is not None:
            if operation is None or digest is None:
                raise OperationRegistryError(
                    "registered operation calls require an operation and digest"
                )
            self._validate_operation(operation, digest, method=method)
        async with self._direct_http.stream(
            method, path, json=payload, follow_redirects=False
        ) as response:
            body = await self._bounded_body(response)
            value = _decode_envelope(body)
            # The gateway answers a typed failed operation with its
            # public HTTP status (400/403/500/503) and a ``{"status":
            # "failed"}`` envelope. That envelope is the tool's answer, not a
            # transport error, so it is returned for the caller to classify.
            if not (response.is_error and _is_failed_envelope(value)):
                response.raise_for_status()
        if value is None:
            raise RuntimeError("Gateway returned an invalid envelope")
        return value

    def _validate_operation(self, operation: str, digest: str, *, method: str) -> None:
        """Validate an operation against the injected registry before transport."""
        if self.operation_registry is None:
            raise OperationRegistryError("operation registry is unavailable")
        entry = self.operation_registry.lookup(operation)
        self.operation_registry.validate_digest(operation, digest)
        if entry.method.upper() != method.upper():
            raise OperationRegistryError(
                f"method mismatch for operation {operation!r}: "
                f"expected {entry.method.upper()}, got {method.upper()}"
            )

    async def invoke_operation(
        self,
        operation: str,
        digest: str,
        *,
        path: str,
        method: str = "POST",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Invoke one registered Arbora operation through the existing transport.

        Registry validation deliberately happens inside ``_json_request`` before
        opening the HTTP stream. Unknown operations, digest mismatches, missing
        registry injection, and method mismatches therefore return the same typed
        unavailable result without any network effect.
        """
        try:
            return await self._json_request(
                method,
                path,
                payload=payload,
                operation=operation,
                digest=digest,
            )
        except OperationRegistryError as exc:
            logger.warning(
                "Arbora operation rejected before transport: "
                "operation=%s error_type=%s",
                operation,
                type(exc).__name__,
            )
            return {
                "error": "Arbora operation unavailable",
                "code": "CLIENT_UNAVAILABLE",
            }

    async def aclose(self) -> None:
        """Release the direct HTTP pool and the shared SDK when supported."""

        await self._direct_http.aclose()
        close = getattr(self._sdk, "aclose", None)
        if callable(close):
            await close()

    async def dashboard_layout(self) -> dict[str, Any]:
        """Read the served layout without importing gateway configuration."""
        value = await self._json_request("GET", "/api/dashboard/layout")
        if not isinstance(value.get("groups"), list):
            raise RuntimeError("Dashboard layout is unavailable")
        for group in value["groups"]:
            if not isinstance(group, dict) or not isinstance(group.get("name"), str):
                raise RuntimeError("Dashboard group is invalid")
            if not isinstance(group.get("services"), list):
                raise RuntimeError("Dashboard services are invalid")
            for service in group["services"]:
                if not isinstance(service, dict) or any(
                    not isinstance(service.get(key), str) for key in ("id", "name")
                ):
                    raise RuntimeError("Dashboard service is invalid")
                if not isinstance(service.get("visible", True), bool) or not isinstance(
                    service.get("url", ""), str
                ):
                    raise RuntimeError("Dashboard service presentation is invalid")
        return value

    async def dashboard_data(self) -> dict[str, Any]:
        """Read widget values; failed or malformed replies are not empty success."""
        value = await self._json_request("GET", "/api/dashboard/data")
        for widget in value.values():
            if not isinstance(widget, dict) or not isinstance(
                widget.get("status"), str
            ):
                raise RuntimeError("Dashboard widget is invalid")
            if not isinstance(widget.get("fields", {}), dict):
                raise RuntimeError("Dashboard widget fields are invalid")
            if widget.get("error") is not None and not isinstance(widget["error"], str):
                raise RuntimeError("Dashboard widget error is invalid")
        return value

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
            logger.debug("Autocomplete fetch failed: error_type=%s", type(e).__name__)
            return []

    async def execute_slash_command(self, query: str):
        """Execute a slash command on the gateway."""
        try:
            return await self._sdk.execute_command(query)
        except Exception as e:
            return {
                "result": "❌ Gateway connection failed. Falling back to local run is not supported for slash commands."
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
            logger.warning("Usage tools fetch failed: error_type=%s", type(e).__name__)
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
            logger.warning("Usage traces fetch failed: error_type=%s", type(e).__name__)
            return {"enabled": False, "traces": []}

    @staticmethod
    def _validate_extraction_request(text: str, url: str, rounds: int) -> None:
        if len(text.encode("utf-8")) > 4 * 1024 * 1024 or len(url) > 8_192:
            raise ValueError("Extraction request exceeded its size limit")
        if not 1 <= int(rounds) <= 100:
            raise ValueError("Extraction rounds are outside the allowed range")

    @staticmethod
    def _check_extraction_stream_limits(event_count: int, line: str) -> None:
        if event_count > _MAX_STREAM_EVENTS:
            raise RuntimeError("Gateway event stream exceeded its limit")
        if len(line.encode("utf-8")) > _MAX_STREAM_LINE_BYTES:
            raise RuntimeError("Gateway event exceeded its size limit")

    @staticmethod
    def _parse_extraction_event(payload: str) -> dict[str, Any] | None:
        try:
            ev = json.loads(payload)
        except json.JSONDecodeError:
            return None
        return ev if isinstance(ev, dict) else None

    async def _consume_extraction_stream(self, job_id: str, progress_cb) -> int:
        """Stream one submitted job's SSE events, forwarding each ``data: ``
        payload to ``progress_cb``. Returns the count of kept (non-duplicate)
        facts seen."""
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
                self._check_extraction_stream_limits(event_count, line)
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                ev = self._parse_extraction_event(payload)
                if ev is None:
                    continue
                if ev.get("type") == "fact" and not ev.get("is_duplicate"):
                    kept += 1
                if progress_cb:
                    progress_cb(payload)
                if ev.get("type") == "job_done":
                    break
        return kept

    async def submit_and_stream_extraction(
        self,
        *,
        text: str = "",
        url: str = "",
        rounds: int = 1,
        dedup: bool = True,
        progress_cb=None,
    ):
        """Submit a fact-extraction job and stream its events (AU-ECO.connector.git-task-resolver).

        Each event (round_start|fact|…|job_done) is forwarded to ``progress_cb``
        as a JSON string so the Qt panel can render facts live on the main thread.
        Returns a summary dict; graceful-offline like every facade method.
        """
        try:
            self._validate_extraction_request(text, url, rounds)
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

            kept = await self._consume_extraction_stream(job_id, progress_cb)
            return {"status": "done", "job_id": job_id, "facts": kept}
        except Exception as e:
            logger.warning("Extraction stream failed: error_type=%s", type(e).__name__)
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
    # REST side of the arbora MCP tools nl_query / ask_data / graph_promql /
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
        if env.get("status") == "error":
            return {"error": "gateway graph request failed"}
        if _is_failed_envelope(env):
            # A typed failed operation keeps its own public error, so the
            # caller shows why, not a misleading "gateway offline".
            failed = env.get("result")
            return failed if isinstance(failed, dict) else {"error": "failed"}
        result = env.get("result")
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

    async def graph_query(
        self, cypher: str, *, scope: str = "local", as_of: str = ""
    ) -> dict:
        """Run one read-only graph query and return its EvidenceBundle.

        The REST twin of the ``graph_query`` MCP tool. ``scope`` selects the
        dialect (``local`` Cypher | ``sql`` | ``sparql`` | ``federated``) and
        ``as_of`` pins a bitemporal instant. Result rows arrive in the bundle's
        ``evidence_spans``.
        """
        payload: dict = {"cypher": cypher, "scope": scope}
        if as_of:
            payload["as_of"] = as_of
        return await self._graph_post("query", payload)

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

    # ── Voice dictation (CONCEPT:AU-ECO.mcp.webui-voice-transcription-delegation) ──
    async def transcribe_voice(
        self, audio_bytes: bytes, *, content_type: str = "audio/wav"
    ) -> dict:
        """Transcribe one bounded audio clip via the WebUI's voice route.

        POSTs a multipart upload to ``POST /api/enhanced/voice/transcribe``
        (``agent_webui.api_extensions``, mounted on this SAME gateway app --
        ``build_agent_app`` embeds the WebUI's whole backend at ``/`` -- and
        delegated server-side through
        ``agent_utilities.server.webui_voice_delegation`` to the governed
        ``audio-transcriber-mcp`` sidecar). The same route the web dictation
        control calls; no separate backend for the desktop client.

        Returns ``{"text": "..."}`` on success. On failure, graceful-offline
        like the rest of this facade: ``{"error": "..."}`` for a genuine
        error, or ``{"error": "...", "unavailable": True}`` specifically
        when the route answers 404/501 (no ``transcribe_voice`` workspace
        helper registered server-side) -- distinct so a caller can tell
        "not enabled here" from "something broke" instead of collapsing
        both into one generic failure message.
        """
        try:
            if len(audio_bytes) > 25 * 1024 * 1024:
                raise ValueError("Audio clip exceeds the transcription size limit")
            files = {"file": ("clip.wav", audio_bytes, content_type)}
            async with self._direct_http.stream(
                "POST",
                "/api/enhanced/voice/transcribe",
                files=files,
                follow_redirects=False,
            ) as response:
                if response.status_code in (404, 501):
                    return {
                        "error": "voice transcription is not enabled on this server",
                        "unavailable": True,
                    }
                response.raise_for_status()
                body = await self._bounded_body(response)
            value = json.loads(body)
            if not isinstance(value, dict):
                raise RuntimeError("Gateway returned an invalid envelope")
            return value
        except Exception as e:
            logger.warning(
                "Voice transcription failed: error_type=%s", type(e).__name__
            )
            return {"error": "voice transcription failed"}

    @staticmethod
    def _emit_copilot_progress(
        ev_type: str, event: dict[str, Any], progress_cb
    ) -> None:
        """Forward one non-final-output copilot event to progress_cb, if any."""
        if not progress_cb:
            return
        if ev_type == "thought":
            progress_cb(f"💭 {event.get('thought', '')}")
        elif ev_type == "call_tool":
            progress_cb(f"🛠️ Tool: {event.get('tool', '')}")
        else:
            progress_cb(
                f"📡 {ev_type}: {event.get('message', '') or event.get('error', '')}"
            )

    async def stream_copilot_query(self, query: str, progress_cb=None):
        """Execute master copilot query with streaming output."""
        try:
            final_output = ""
            async for event in self._sdk.stream(
                query, mode="ask", topology="basic", timeout=60.0
            ):
                ev_type = str(event.get("type") or "")
                if ev_type == "final_output":
                    final_output = event.get("content", "")
                else:
                    self._emit_copilot_progress(ev_type, event, progress_cb)
            if final_output:
                return {"result": final_output}
        except Exception as e:
            logger.warning(
                "Gateway SSE execution failed: error_type=%s", type(e).__name__
            )

        return {
            "result": "❌ Gateway is offline. Please make sure the arbora gateway is running at http://localhost:8000."
        }
