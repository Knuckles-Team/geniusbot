# GENIUSBOT-CLIENT design and integration plan

## Existing wiring and architecture

At the current public main revision, `geniusbot/geniusbot.py` owns the `QMainWindow`
cockpit shell: a flat sidebar, a central stacked widget of lazily loaded views, a
right-hand telemetry drawer, and a bottom console. `geniusbot/services/gateway_client.py`
owns HTTP transport to Arbora. It uses GatewayRoutes and bounded direct requests for graph, enhanced and dashboard endpoints.
The presentation adapter is `geniusbot/services/backend_adapter.py`. It handles graph queries, workflows, log paths and service snapshots. Dashboard layout and data must come from the existing served
`/api/dashboard/layout` and `/api/dashboard/data` endpoints through the same
GatewayClient transport implementation, not Arbora server imports. The
`geniusbot/qt/*` panels are presentation consumers built on this facade and worker;
`geniusbot/utils/agent_bridge.py` (`AgentBridgeWorker`/`AgentRunnable`/`QThreadPool`) is the
one dispatch path off the Qt UI thread; `geniusbot/utils/daemon.py` owns the system tray.
This is the path to extend. No panel should open a second gateway client.
No panel should add a second import of the engine package or a second thread-dispatch mechanism.

```text
sidebar click / chat input / tray action
    -> GeniusBot (QMainWindow) / panel
    -> AgentBridgeWorker (QThreadPool, one background event loop per task)
    -> GatewayClient facade (TLS-validated, bounded, graceful-offline)
    -> arbora.client SDK / direct /api/graph|enhanced POST
    -> Arbora gateway: registry, authorization, ActionPolicy approval boundary
    -> typed result/error -> Qt signal -> existing widgets (chat log, tables, status labels)
```

## Contracts and decisions

| Boundary | Contract to implement or verify |
|---|---|
| Import seam | No module imports `agent_utilities`; every `qt/*` panel and `geniusbot.py` route through `services/backend_adapter.py` and `services/gateway_client.py`, which call arbora (`arbora.client`). |
| Operation validation | Before invoking an Arbora operation (specialist run, slash command, graph/data query), resolve it against the installed generated operation registry; an unknown operation or a registry/digest mismatch produces a typed unavailable result before any network call. |
| Transport | `GatewayClient.__init__` rejects a malformed endpoint (credentials in the URL, a query/fragment, a non-http(s) scheme) and plaintext HTTP to a non-loopback host without explicit opt-in; it resolves a TLS profile for the caller's verified credential and pins egress to the configured host. Every response is read through a bounded reader (`_bounded_body`) capped at a fixed byte limit. |
| Dispatch | Every async Arbora/backend call runs inside `AgentRunnable.run()` on the global `QThreadPool`, reporting `started`/`finished`/`error`/`progress` back to the UI thread via Qt signals; nothing calls a blocking network or heavy-reasoning routine directly from a slot. |
| Errors | Every facade method catches its own transport/SDK exceptions and returns a typed `{"result": ...}` / `{"error": ...}` / safe-default value. No exception from `httpx`, the SDK, or a malformed envelope is allowed to propagate into a Qt slot. |
| Approval | The Fleet Supervisor's approval inbox and any tool-authorization dialog display a pending decision. Granting or rejecting always issues a request to the gateway's server-side approval/`ActionPolicy` endpoint. No code path marks an action authorized by local logic alone. |
| Terminal | The terminal view's PTY-backed shell starts lazily on first navigation to that view (`switch_view(1)`), not at window construction. |
| Panel loading | `_PANEL_SPECS` drives lazy import + instantiate + placeholder-swap for every secondary view index; a panel is constructed at most once per window lifetime and shares the one `AgentBridgeWorker`. |
| Packaging | The same versioned source tree produces the pip-installable package (`pyproject.toml` console script `geniusbot`), a PyInstaller onefile/windowed build, a `setup.iss`-driven Windows installer, and the `packaging/linux/` desktop-entry and control file. |

## Live integration path

`geniusbot()` constructs `GeniusBot`, which wires the tray daemon, the gateway client, and
a `QTimer.singleShot` specialist-discovery call through `AgentBridgeWorker`. Every sidebar
button routes through `switch_view`, which lazily instantiates the corresponding panel
class from `_PANEL_SPECS` and swaps it into the stacked widget. Panels that need Arbora
data construct their own `GatewayClient` (or receive the shared `AgentBridgeWorker`) and
call the facade's async methods, which always resolve to a typed success/error value. No
obsolete transport path currently exists in this repository to retire; the `ToolGuardDialog`
authorization modal exists and is exercised by its own instantiation test but is not yet
wired into any execution path — closing that gap, or explicitly scoping it out, is a
`GENIUSBOT-CLIENT-R006` task.

## Compatibility and migration

Keep `requires-python = ">=3.12, <3.15"` and the single `arbora>=0.1.0` dependency
as the floor; this client does not need an optional-extra split for the generated Arbora
client because `arbora` (which publishes the gateway client) is already a hard
dependency of the desktop package, unlike a thin terminal client that supports a
no-Arbora-client base install. Packaging changes (PyInstaller spec, `setup.iss`, the
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

## Structure parity with agent-webui (2026-10-11)

Gap table. Reference: `agent-webui` branch `spec-standard-conform`.

| Structural element | agent-webui | geniusbot | Action |
|---|---|---|---|
| Root layout | App, `agent/`, `e2e/`, `docker/`, `CONTRIBUTING.md` | Flat `geniusbot/` package, `packaging/`, `setup.iss` | Differs by product type; no action |
| Specs by area | Six specs | One spec, `desktop-client` | Area decisions below; rows R013, R014 |
| Spec files | Standard file set, `_template/` | Standard file set, `_template/` | Same |
| Docs | `agents`, `apps`, `architecture`, `deployment`, `design-system`, `features`, `start`, `status` and more | `index`, `overview`, `concepts`, `glossary`, `kg-extraction` | Missing pages; row R017 |
| Workflows | `advisory.yml`, `release.yml` | `pages.yml`, `pipeline.yml`, `release.yml` | Differs; no action |
| Reusable `pipelines` calls | `pages_pipeline.yml` | `pages_pipeline.yml`, `python_pipeline.yml`, `desktop_release_pipeline.yml` | Same Pages caller |
| Pre-commit location | `.config/pre-commit.yaml` | `.pre-commit-config.yaml` | Differs; no action |
| Pre-commit spec hooks | `spec-status`, `spec-decomposition`, `spec-trailers`, `public-surface`, `ste-staged`, `ste-staleness-staged`, `check-public-specs` | `spec-status`, `spec-decomposition`, `spec-trailers` | Missing four; row R016 |
| `pyproject.toml` hook sections | `public_surface`, `ste` | None | Missing; row R016 |
| `AGENTS.md` sections | Owns, Commands, Quality gates, Development rules, Documentation, Branching, Specs | Stack, Concept IDs, Structure, Safety, Git worktrees, Specs | Differs; row R018 |
| Packaged development skill | `agent-webui-development` | None | Missing; row R015 |
| Spec-delivery page | `spec_dashboard_enabled: true` | `spec_dashboard_enabled: true` and `.github/spec-dashboard.json` | Same |

Area decisions.

- Design system: the desktop client has `geniusbot/qt/colors.py`, generated from tokens. Extend `desktop-client` with R013. The generator and token files are not in the repository, so R013 adds them.
- Decision evidence: `git grep` finds no decision or calibration surface. Not implemented; no spec.
- Finance asset manager: `geniusbot/qt/finance_cockpit.py` has 606 lines and R008 already owns its lazy loading. It is a panel, not a distinct capability. Extend with R014; no new directory.
- API consumer: `geniusbot/services/operation_registry.py` and R002 already own the generated registry. No change.
- App surfaces: R008 and R011 already own the cockpit shell and panels. No change.
- Identity and access: `git grep` finds no browser identity or elevation surface. Not implemented; no spec.

## Run harness surface (GENIUSBOT-CLIENT-R019)

### Existing source and planned wiring

`GeniusBot.switch_view` (`geniusbot/geniusbot.py:500`) → the lazy run panel → a background gateway worker → `GatewayClient` (`geniusbot/services/gateway_client.py:55`).

No run panel or run facade exists in current source.
`GatewayClient.fetch_usage_traces` at `gateway_client.py:255` serves usage traces, not a run-summary contract.
The implementation must extend the existing facade and lazy panel navigation.
Network reads must use the existing background worker; Qt updates must return through signals.

The client must use the versioned Arbora operation transport and its generated envelope.
It must not add another HTTP stack or call the engine directly.

### Model and wire-to-view mapping

[Arbora run reads](https://github.com/Knuckles-Team/arbora/tree/main/specs/hosted-api-operations) own the served projection.
`ARBORA-OPS-R021.4.5` serves per-run fields; `.3` and `.4` define aggregate models and operations.
`ARBORA-OPS-R021.4.6` supplies registration and generated artifacts.

| Arbora wire field | View label and behavior |
|---|---|
| `termination_reason` | Distinct final answer, context overflow, stuck, step budget and error labels |
| `peak_context_tokens`, `context_budget_tokens` | Peak context tokens against run budget; never current occupancy |
| `cost_usd` | Per-run USD cost |
| `harness_config_ref`, `harness_config` | Applied decision reference and available configuration fields |
| `current_plan` | Available snapshot items, revision and observation time; read-only |
| `runs.metrics` result `cost_per_solved_task_usd` | Aggregate cost per solved task, with query grouping and abstention |

The client must not accept RDF camelCase fields as alternate wire names.
The client must preserve null availability and measured zero as different values.
The engine defines solved tasks and computes aggregates under `EG-ORCH-VOCAB-R010`.
Zero-solved cost abstention must display unavailable, never zero or per-run cost.
Pair-level rates and configuration-level costs must retain separate group labels.

### Current-plan prerequisite and refusals

`AU-HARNESS-R014.1` through `.5` own mutable `PlanState` outside stored message history.
Those rows supply no public snapshot read contract today.
`ARBORA-OPS-R021.4.5` defines the required cross-boundary snapshot and blocks availability until the AU producer exists.
The client must not derive a plan from messages, reconstruct state, or add a plan writer.
An available empty plan must differ from unavailable state.
Run switches, denied refreshes and expired snapshots must clear protected values from the previous display.
A missing plan must not suppress other independently available trace fields.
Unknown terminal reasons must display unavailable; the client must never infer success from a final answer alone.

### Evidence and implementation order

Implement the Arbora producer before the consumer wiring, then field rendering and served acceptance.
The six existing children remain the only client requirement family for this surface.
The tests in test-spec.md are planned acceptance paths, not proof of implementation.
Each row requires its own positive and negative served case through the production UI path above.

## Amendments

- 2026-10-11, rows R013 to R018: the operator required geniusbot to share the exact structure of agent-webui. Old statement: the spec ended at R012. New statement: R013 to R018 close the structural gaps above. Evidence: the gap table in this file.

## Source quality contract

GENIUSBOT-CLIENT-R020 preserves unresolved source-quality obligations in this owning specification.
Each child retains its source mapping in [source history](../../plans/spec-source-history/README.md).
The byte-preserved records include original unchecked items and historical completion claims.
Those claims supply no current acceptance evidence.
Each repair must name its production or tooling call path before implementation.
Each repair must bind a positive test and a counterexample to its child identifier.
The migration introduces no runtime behavior and closes no child obligation.
The [shared spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md) governs future changes.

### Source-quality wiring and served proof

The desktop command enters `main`, then `geniusbot` at `geniusbot/geniusbot.py:678`. That function creates `GeniusBot`, displays its window and starts the application event loop.
Quality repairs attach at the files each child names; they must preserve this production entry path.
The final two child rows require wiring inspection and a served integration proof.
Tooling-only children use their configured check entry points and must reject a failing fixture.

### Amendment 2026-10-22: shared checker ownership

R016.2 retains all six required checks previously invoked through removed agent-utilities scripts. The immutable pipelines pin owns no-legacy-concepts, stubs, sprawl, coupling and lockfile-version-mirrors; the repository-manager pin owns lane-guard. Coupling scans the actual geniusbot package and forbids engine and sibling UI imports, allowing only arbora.client. No adapter exemption applies. Lockfile version mirrors retains its dependency-file trigger and checks both uv.lock and requirements.txt; uv-lock-check is not a substitute.


### Amendment 2026-10-22: served dashboard client seam

R001 forbids server-internal imports even inside BackendAdapter. R004 requires dashboard layout and data reads off the UI thread. A dashboard refresh uses a task-scoped GatewayClient through BackendAdapter. Its HTTP pools open and close on the worker event loop. It preserves endpoint validation, TLS, the proxy environment, bounded reads and redirect refusal. No server endpoint, schema or storage changes are needed. A denied, malformed or unavailable response clears old dashboard values rather than presenting an empty successful dashboard. Cleanup cancels the pending async request without stopping a Qt thread or blocking the UI. Late replies do not repopulate a closed panel.


### Amendment 2026-10-22: Qt resource lifetime

R004.2 retains queued worker signals until the UI receives completion or failure. R010.2 restores standard streams on actual window close and QObject destruction, but not on tray minimization. A later window or stderr write must not access a destroyed Qt object. Tests wait for signals with a timed event-loop wait, not a fixed busy-loop count. Regression tests close their windows and stop their resources; exception capture remains active.


### Amendment 2026-10-22: bounded dashboard shutdown

R001.3 uses a QRunnable on QThreadPool, with a retained QObject for signals. Normal panel close only requests cancellation. Async cleanup gets 0.5 seconds before repeated cancellation. A 0.1-second loop deadline bounds a stalled coroutine. Application quit waits at most one second for completion. No Qt or operating-system thread is forcibly stopped. A cleanup deadline emits a warning; it is not a successful data response. Separate processes test delayed and stalled cleanup without hiding Qt exceptions.

The shutdown guarantee covers cooperative async cancellation, not synchronous blocking. The stalled fixture accepts the second cancellation; it does not exercise the final loop-stop fallback. Cleanup after the deadline is not guaranteed.
