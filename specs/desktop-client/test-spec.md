# GENIUSBOT-CLIENT-001 test specification

| Requirement | Layer and fixture | Expected positive result | Required negative proof |
|---|---|---|---|
| GENIUSBOT-CLIENT-R001 | Source-tree scan over `geniusbot/` | Only `services/backend_adapter.py` and `services/gateway_client.py` import `agent_utilities` | Any other file importing `agent_utilities` (or `from agent_utilities...`) fails the scan |
| GENIUSBOT-CLIENT-R002 | Unit test against the gateway facade's operation-invocation path with a fake installed registry | A known, registered operation with valid input produces one request | An unknown operation id, and a registry/digest mismatch, make zero network requests and return a typed unavailable result |
| GENIUSBOT-CLIENT-R003 | `GatewayClient.__init__` and `_bounded_body` with parametrized URLs and `httpx.Response` streams | A valid `https://` or loopback `http://` endpoint constructs the client; a response under the limit is returned | A URL with embedded credentials, a query/fragment, a non-http(s) scheme, or non-opted-in remote plaintext raises `ValueError`; a streamed or declared-oversize response raises `RuntimeError` |
| GENIUSBOT-CLIENT-R004 | `AgentBridgeWorker`/`AgentRunnable` signal contract with a fake async callable | `started`, `progress`, and `finished` signals fire in order with the callable's result | An exception raised inside the async callable emits `error` and never raises out of `run()` |
| GENIUSBOT-CLIENT-R005 | Gateway facade methods (`stream_copilot_query`, `fetch_specialists`, `run_health_check`, etc.) against a fake/mock transport that times out, disconnects, or raises | Success path returns the typed `{"result": ...}` payload | Timeout, disconnect, and raised-exception paths each return a typed offline/error payload, never an uncaught exception |
| GENIUSBOT-CLIENT-R006 | Fleet Supervisor `_grant` against a fake gateway/worker | Granting an approval issues exactly one `grant_approval(approval_id)` call to the gateway and refreshes from its response | No code path marks an approval granted, or executes a tool past `ToolGuardDialog`, without that gateway round trip completing |
| GENIUSBOT-CLIENT-R007 | `TerminalWidget`/`TerminalBridge` instantiation; `GeniusBot.switch_view` | Terminal widget and bridge construct cleanly; navigating to the terminal view starts its shell exactly once | Re-navigating to the terminal view does not start a second shell process |
| GENIUSBOT-CLIENT-R008 | `GeniusBot.switch_view` walked over every secondary view index | Each panel attribute is `None` before first visit, is constructed and swapped into the stack on first visit, and is reused (not reconstructed) on a second visit; only the active sidebar button loses its transparent styling | Navigating to an index twice does not re-instantiate or re-import the panel |
| GENIUSBOT-CLIENT-R009 | `VoicePanel` fed synthetic recorder/gateway responses | A successful transcription renders the returned text | No-device, each mapped `QMediaRecorder.Error`, a gateway `unavailable` response, and a generic gateway error each render a distinct message |
| GENIUSBOT-CLIENT-R010 | `GeniusBotDaemon` signal wiring; `GeniusBot.closeEvent` | Each tray action (show/terminal/health-check/exit) triggers its bound window method | Closing the main window while the tray icon is visible hides the window and leaves the process running; exiting via the tray stops the daemon and allows the close |
| GENIUSBOT-CLIENT-R011 | `WidgetSchemaMapper.build_deck` / `AgentControlPanel` with synthetic specialist records | A `skills` list produces one input field per skill; a specialist with no capabilities produces the `task_query` fallback field | A malformed or empty specialist list produces an empty deck rather than a crash |
| GENIUSBOT-CLIENT-R012 | PyInstaller onefile build, Inno Setup compile, and a lint of the Linux desktop-entry/control file, each against a tagged revision | Each artifact builds without error and the resulting entry point launches the cockpit window | A build against a revision with a missing/renamed entry point or icon path fails the build step, not the launch |

## Negative and boundary cases

- Invalid or hostile transport configuration (credentials embedded in the gateway URL,
  non-loopback plaintext, oversized or truncated responses) is rejected before or during
  the request, never after rendering partial data.
- A Graph OS operation or specialist invocation with malformed, missing, or oversized input
  is rejected locally before any network effect (mirrors the extraction-request and
  job-id validation already enforced in `gateway_client.py`).
- An approval or tool-authorization action can be rejected (not only granted); a rejection
  must not execute the underlying action.
- Every panel must remain interactive (no modal deadlock, no unhandled exception dialog)
  after its backing gateway call fails.
- Idempotency: repeated navigation to the same view, and repeated grant/health-check/refresh
  clicks, must not accumulate duplicate panels, duplicate shells, or duplicate in-flight
  requests beyond what the user explicitly triggered.

## Quality and release proof

- Run `pytest` (unit + `pytest-qt` + `pytest-asyncio` markers), `ruff check`, and `mypy`
  against the exact public revision; capture the revision, environment, and pass/fail in
  `status.json`.
- Run the source-tree import-seam scan (`tests/test_backend_adapter_seam.py`) and the
  gateway-client security suite (`tests/security/test_gateway_client_security.py`) as part
  of the same gate; a source test pass alone does not serve acceptance without the packaging
  and live-gateway receipts below.
- Build and run the packaged artifacts (PyInstaller onefile, Windows installer, Linux
  desktop entry) from a tagged revision and confirm the entry point launches the cockpit
  window against a reachable and an unreachable Graph OS gateway.
- Record configured CCCC, `jscpd`, and Dupehound ecosystem checks if present in this
  repository's tracked configuration; where absent, record that as an acceptance gap
  rather than an unconfigured pass.

No manual-only proof substitutes for the negative tests above. If a live Graph OS gateway
is unavailable, keep the approval and registry-validation requirements' acceptance pending
rather than requiring private infrastructure to run the baseline tests.
