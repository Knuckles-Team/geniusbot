# GENIUSBOT-CLIENT-001 design and integration plan

## Existing wiring and architecture

At the current public main revision, `geniusbot/geniusbot.py` owns the `QMainWindow`
cockpit shell: a flat sidebar, a central stacked widget of lazily loaded views, a
right-hand telemetry drawer, and a bottom console. `geniusbot/services/gateway_client.py`
owns the one HTTP/SDK transport to the Graph OS gateway (a thin facade over the shared
`agent_utilities.gateway_client.GatewayClient` SDK plus a small set of direct
`/api/graph/*` and `/api/enhanced/*` POSTs). `geniusbot/services/backend_adapter.py` is the
single sanctioned seam for anything that still needs to reach the underlying engine
package directly (log-directory resolution, the workspace graph runner, the gateway
`ConfigManager`/`Aggregator`); every other module is barred from importing it. The
`geniusbot/qt/*` panels are presentation consumers built on this facade and worker;
`geniusbot/utils/agent_bridge.py` (`AgentBridgeWorker`/`AgentRunnable`/`QThreadPool`) is the
one dispatch path off the Qt UI thread; `geniusbot/utils/daemon.py` owns the system tray.
This is the path to extend; no panel should open a second gateway client, a second import
of the engine package, or a second thread-dispatch mechanism.

```text
sidebar click / chat input / tray action
    -> GeniusBot (QMainWindow) / panel
    -> AgentBridgeWorker (QThreadPool, one background event loop per task)
    -> GatewayClient facade (TLS-validated, bounded, graceful-offline)
    -> agent_utilities.gateway_client SDK / direct /api/graph|enhanced POST
    -> Graph OS gateway: registry, authorization, ActionPolicy approval boundary
    -> typed result/error -> Qt signal -> existing widgets (chat log, tables, status labels)
```

## Contracts and decisions

| Boundary | Contract to implement or verify |
|---|---|
| Import seam | Only `services/backend_adapter.py` and `services/gateway_client.py` import `agent_utilities`; every `qt/*` panel and `geniusbot.py` route through them. |
| Operation validation | Before invoking a Graph OS operation (specialist run, slash command, graph/data query), resolve it against the installed generated operation registry; an unknown operation or a registry/digest mismatch produces a typed unavailable result before any network call. |
| Transport | `GatewayClient.__init__` rejects a malformed endpoint (credentials in the URL, a query/fragment, a non-http(s) scheme) and plaintext HTTP to a non-loopback host without explicit opt-in; it resolves a TLS profile for the caller's verified credential and pins egress to the configured host. Every response is read through a bounded reader (`_bounded_body`) capped at a fixed byte limit. |
| Dispatch | Every async Graph OS/backend call runs inside `AgentRunnable.run()` on the global `QThreadPool`, reporting `started`/`finished`/`error`/`progress` back to the UI thread via Qt signals; nothing calls a blocking network or heavy-reasoning routine directly from a slot. |
| Errors | Every facade method catches its own transport/SDK exceptions and returns a typed `{"result": ...}` / `{"error": ...}` / safe-default value; no exception from `httpx`, the SDK, or a malformed envelope is allowed to propagate into a Qt slot. |
| Approval | The Fleet Supervisor's approval inbox and any tool-authorization dialog display a pending decision; granting or rejecting always issues a request to the gateway's server-side approval/`ActionPolicy` endpoint. No code path marks an action authorized by local logic alone. |
| Terminal | The terminal view's PTY-backed shell starts lazily on first navigation to that view (`switch_view(1)`), not at window construction. |
| Panel loading | `_PANEL_SPECS` drives lazy import + instantiate + placeholder-swap for every secondary view index; a panel is constructed at most once per window lifetime and shares the one `AgentBridgeWorker`. |
| Packaging | The same versioned source tree produces the pip-installable package (`pyproject.toml` console script `geniusbot`), a PyInstaller onefile/windowed build, a `setup.iss`-driven Windows installer, and the `packaging/linux/` desktop-entry and control file. |

## Live integration path

`geniusbot()` constructs `GeniusBot`, which wires the tray daemon, the gateway client, and
a `QTimer.singleShot` specialist-discovery call through `AgentBridgeWorker`. Every sidebar
button routes through `switch_view`, which lazily instantiates the corresponding panel
class from `_PANEL_SPECS` and swaps it into the stacked widget. Panels that need Graph OS
data construct their own `GatewayClient` (or receive the shared `AgentBridgeWorker`) and
call the facade's async methods, which always resolve to a typed success/error value. No
obsolete transport path currently exists in this repository to retire; the `ToolGuardDialog`
authorization modal exists and is exercised by its own instantiation test but is not yet
wired into any execution path — closing that gap, or explicitly scoping it out, is a
`GENIUSBOT-CLIENT-R006` task.

## Compatibility and migration

Keep `requires-python = ">=3.12, <3.15"` and the single `agent-utilities>=2.0.0` dependency
as the floor; this client does not need an optional-extra split for the generated Graph OS
client because `agent-utilities` (which vendors the gateway SDK) is already a hard
dependency of the desktop package, unlike a thin terminal client that supports a
no-Graph-OS-client base install. Packaging changes (PyInstaller spec, `setup.iss`, the
Linux desktop entry) must track `pyproject.toml`'s version via the existing
`.bumpversion.cfg` mirrors rather than drifting independently.

## Quality and reuse

Use the existing `GatewayClient` facade, `BackendAdapter` seam, `AgentBridgeWorker`,
`httpx`, and PySide6 widgets. Keep one transport-validation path (`GatewayClient.__init__`)
and one bounded-response path (`_bounded_body`); do not duplicate either in a panel. Run
the repository's configured Ruff, mypy and pytest (`pytest-qt`, `pytest-asyncio`) checks.
Apply KISS through the single `_PANEL_SPECS` dispatch table and the single `_graph_post`
route allow-list; no parallel panel-loading or graph-route-dispatch mechanism. Record any
missing CCCC/`jscpd`/Dupehound threshold for this repository as an explicit gap rather than
an unconfigured pass.

## Risks, alternatives, and decisions

- The desktop client currently validates transport security (R003) and fails closed on
  errors (R005) without a registry-backed operation validation step (R002); this is a
  tracked gap, not a silent pass.
- `ToolGuardDialog` is built and tested in isolation but has no caller; leaving it unwired
  is itself a risk (a reviewer could assume dangerous tool calls are already gated by it).
  Either wire it into the specialist-execution and slash-command paths, or record its scope
  as deferred.
- The Fleet Supervisor's "Grant" action already calls the gateway's `grant_approval`
  endpoint; this plan treats that round trip, not any local state change, as the
  authorization act, consistent with GENIUSBOT-CLIENT-R006.
