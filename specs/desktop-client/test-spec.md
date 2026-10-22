# GENIUSBOT-CLIENT test specification

| Requirement | Layer and fixture | Expected positive result | Required negative proof |
|---|---|---|---|
| GENIUSBOT-CLIENT-R001 | Source-tree scan over `geniusbot/` | No file imports `agent_utilities` | Any file importing `agent_utilities` (or `from agent_utilities...`) fails the scan |
| GENIUSBOT-CLIENT-R002 | Unit test against the gateway facade's operation-invocation path with a fake installed registry | A known, registered operation with valid input produces one request | An unknown operation id, and a registry/digest mismatch, make zero network requests and return a typed unavailable result |
| GENIUSBOT-CLIENT-R003 | `GatewayClient.__init__` and `_bounded_body` with parametrized URLs and `httpx.Response` streams | A valid `https://` or loopback `http://` endpoint constructs the client; a response under the limit is returned | A URL with embedded credentials, a query/fragment, a non-http(s) scheme, or non-opted-in remote plaintext raises `ValueError`; a streamed or declared-oversize response raises `RuntimeError` |
| GENIUSBOT-CLIENT-R004 | `AgentBridgeWorker`/`AgentRunnable` signal contract with a fake async callable | `started`, `progress`, and `finished` signals fire in order with the callable's result | An exception raised inside the async callable emits `error` and never raises out of `run()` |
| GENIUSBOT-CLIENT-R005 | Gateway facade methods (`stream_copilot_query`, `fetch_specialists`, `run_health_check`, etc.) against a fake/mock transport that times out, disconnects, or raises | Success path returns the typed `{"result": ...}` payload | Timeout, disconnect, and raised-exception paths each return a typed offline/error payload, never an uncaught exception |
| GENIUSBOT-CLIENT-R006 | Fleet Supervisor `_grant` against a fake gateway/worker. | A grant issues exactly one `grant_approval(approval_id)` gateway call. The view refreshes from its response. | No code marks approval granted before that round trip completes. No tool passes `ToolGuardDialog` before completion. |
| GENIUSBOT-CLIENT-R007 | `TerminalWidget`/`TerminalBridge` instantiation; `GeniusBot.switch_view` | Terminal widget and bridge construct cleanly; navigating to the terminal view starts its shell exactly once | Re-navigating to the terminal view does not start a second shell process |
| GENIUSBOT-CLIENT-R008 | `GeniusBot.switch_view` walked over every secondary view index | Each panel attribute is `None` before first visit, is constructed and swapped into the stack on first visit, and is reused (not reconstructed) on a second visit; only the active sidebar button loses its transparent styling | Navigating to an index twice does not re-instantiate or re-import the panel |
| GENIUSBOT-CLIENT-R009 | `VoicePanel` fed synthetic recorder/gateway responses | A successful transcription renders the returned text | No-device, each mapped `QMediaRecorder.Error`, a gateway `unavailable` response, and a generic gateway error each render a distinct message |
| GENIUSBOT-CLIENT-R010 | `GeniusBotDaemon` signal wiring; `GeniusBot.closeEvent` | Each tray action (show/terminal/health-check/exit) triggers its bound window method | Closing the main window while the tray icon is visible hides the window and leaves the process running; exiting via the tray stops the daemon and allows the close |
| GENIUSBOT-CLIENT-R011 | `WidgetSchemaMapper.build_deck` / `AgentControlPanel` with synthetic specialist records | A `skills` list produces one input field per skill; a specialist with no capabilities produces the `task_query` fallback field | A malformed or empty specialist list produces an empty deck rather than a crash |
| GENIUSBOT-CLIENT-R012 | PyInstaller onefile build, Inno Setup compile, and a lint of the Linux desktop-entry/control file, each against a tagged revision | Each artifact builds without error and the resulting entry point launches the cockpit window | A build against a revision with a missing/renamed entry point or icon path fails the build step, not the launch |
| GENIUSBOT-CLIENT-R013 | Unit test comparing `geniusbot/qt/colors.py` with generator output | Regenerated file is byte-identical | A hand-edited constant fails |
| GENIUSBOT-CLIENT-R014 | Offscreen Qt test of `FinanceCockpitPanel` with a fake failing gateway | Panel shows the unavailable state | A gateway exception never escapes |
| GENIUSBOT-CLIENT-R015 | Packaging test reading `geniusbot/skills/geniusbot-development/SKILL.md` | Front matter parses and the file ships in the wheel | Missing front matter fails |
| GENIUSBOT-CLIENT-R016 | Parse `.pre-commit-config.yaml` and `pyproject.toml` | All required hook ids and tool sections exist | A removed hook id fails |
| GENIUSBOT-CLIENT-R017 | Parse `mkdocs.yml` and list `docs/` | Every page is in nav | A page absent from nav fails |
| GENIUSBOT-CLIENT-R018 | Read `AGENTS.md` headings | Required headings exist in order | A missing heading fails |

## Negative and boundary cases

- Invalid or hostile transport configuration (credentials embedded in the gateway URL,
  non-loopback plaintext, oversized or truncated responses) is rejected before or during
  the request, never after rendering partial data.
- An Arbora operation or specialist invocation with malformed, missing, or oversized input
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
- Build and run packaged artifacts from a tagged revision: PyInstaller onefile, Windows installer and Linux desktop entry.
  Confirm that the entry point opens the cockpit with a reachable and an unreachable Arbora gateway.
- Record configured CCCC, `jscpd`, and Dupehound ecosystem checks if present in this
  repository's tracked configuration; where absent, record that as an acceptance gap
  rather than an unconfigured pass.

No manual-only proof substitutes for the negative tests above. If a live Arbora gateway
is unavailable, keep the approval and registry-validation requirements' acceptance pending
rather than requiring private infrastructure to run the baseline tests.

## Planned run-surface acceptance

These tests are planned, not execution receipts. Each test must bind its exact requirement ID.
Each case must enter the production UI, existing client, and a served Arbora operation fixture.
A mocked widget value alone must not count as served evidence.

| Requirement | Planned test | Positive served requirement | Negative served requirement |
|---|---|---|---|
| GENIUSBOT-CLIENT-R019.1 | `tests/test_run_view.py::test_run_read_uses_arbora_operations` | A selected run must render through the served operation and existing client. | Absent registration, timeout or denial must show unavailable without direct engine calls. |
| GENIUSBOT-CLIENT-R019.2 | `tests/test_run_view.py::test_harness_config_shown` | A committed configuration must retain its reference and values through the client. | Missing or inaccessible configuration must not use defaults or the latest configuration. |
| GENIUSBOT-CLIENT-R019.3 | `tests/test_run_view.py::test_context_and_cost_shown` | Measured zero must render as zero; aggregate cost must retain its solved-task label. | Null values must show unavailable; zero-solved abstention must not render zero cost. |
| GENIUSBOT-CLIENT-R019.4 | `tests/test_run_view.py::test_plan_read_only` | A fresh matching snapshot must preserve item order, revision and AU statuses. | Expired, wrong-run, regressing or unavailable snapshots must reveal no items or edit controls. |
| GENIUSBOT-CLIENT-R019.5 | `tests/test_run_view.py::test_termination_reasons_distinct` | Each of final_answer, context_overflow, stuck, step_budget and error must have its own label. | Unknown or missing reasons must show unavailable; overflow and stuck must not collapse to generic failure. |
| GENIUSBOT-CLIENT-R019.6 | `tests/test_run_view.py::test_run_surface_end_to_end` | A served fixture must render summary, configuration, context, cost and an available plan. | Denied reads after success must clear prior protected values; the UI must stay responsive without fabricated data. |

## Source quality acceptance

| ID | Acceptance evidence |
|---|---|
| `GENIUSBOT-CLIENT-R020` | All child tests must pass through their owning production or tooling entry points. |
| `GENIUSBOT-CLIENT-R020.1` | Planned `tests/test_source_quality.py::test_source_quality_1` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.2` | Planned `tests/test_source_quality.py::test_source_quality_2` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.3` | Planned `tests/test_source_quality.py::test_source_quality_3` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.4` | Planned `tests/test_source_quality.py::test_source_quality_4` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.5` | Planned `tests/test_source_quality.py::test_source_quality_5` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.6` | Planned `tests/test_source_quality.py::test_source_quality_6` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.7` | Planned `tests/test_source_quality.py::test_source_quality_7` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.8` | Planned `tests/test_source_quality.py::test_source_quality_8` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.9` | Planned `tests/test_source_quality.py::test_source_quality_9` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.10` | Planned `tests/test_source_quality.py::test_source_quality_10` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.11` | Planned `tests/test_source_quality.py::test_source_quality_11` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.12` | Planned `tests/test_source_quality.py::test_source_quality_12` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.13` | Planned `tests/test_source_quality.py::test_source_quality_13` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.14` | Planned `tests/test_source_quality.py::test_source_quality_14` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.15` | Planned `tests/test_source_quality.py::test_source_quality_15` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.16` | Planned `tests/test_source_quality.py::test_source_quality_16` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.17` | Planned `tests/test_source_quality.py::test_source_quality_17` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.18` | Planned `tests/test_source_quality.py::test_source_quality_18` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.19` | Planned `tests/test_source_quality.py::test_source_quality_19` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.20` | Planned `tests/test_source_quality.py::test_source_quality_20` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.21` | Planned `tests/test_source_quality.py::test_source_quality_21` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.22` | Planned `tests/test_source_quality.py::test_source_quality_22` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.23` | Planned `tests/test_source_quality.py::test_source_quality_23` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.24` | Planned `tests/test_source_quality.py::test_source_quality_24` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.25` | Planned `tests/test_source_quality.py::test_source_quality_25` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.26` | Planned `tests/test_source_quality.py::test_source_quality_26` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.27` | Planned `tests/test_source_quality.py::test_source_quality_27` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.28` | Planned `tests/test_source_quality.py::test_source_quality_28` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.29` | Planned `tests/test_source_quality.py::test_source_quality_29` must enter the owning path and prove the requirement. |
| `GENIUSBOT-CLIENT-R020.30` | Planned `tests/test_source_quality.py::test_source_quality_30` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.31` | Planned `tests/test_source_quality.py::test_source_quality_31` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.32` | Planned `tests/test_source_quality.py::test_source_quality_32` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.33` | Planned `tests/test_source_quality.py::test_source_quality_33` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.34` | Planned `tests/test_source_quality.py::test_source_quality_34` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.35` | Planned `tests/test_source_quality.py::test_source_quality_35` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.36` | Planned `tests/test_source_quality.py::test_source_quality_36` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.37` | Planned `tests/test_source_quality.py::test_source_quality_37` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.38` | Planned `tests/test_source_quality.py::test_source_quality_38` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.39` | Planned `tests/test_source_quality.py::test_source_quality_39` must measure this criterion through the quality-check entry point. |
| `GENIUSBOT-CLIENT-R020.40` | Planned `tests/test_source_quality.py::test_source_quality_entry_wiring` must enter the installed command against an authorized served fixture. |
| `GENIUSBOT-CLIENT-R020.41` | Planned `tests/test_source_quality.py::test_source_quality_served_entry` must enter the installed command against an authorized served fixture. |

## Served dashboard acceptance

R001.1 retains the original adapter-seam obligation and source scan. R001.2 binds tests/test_service_dashboard_transport.py: exact public routes, headers, widget projection, redirects, status errors, malformed payloads and transport closure on cancellation. R001.3 binds tests/test_service_dashboard_async.py. It checks worker-thread dispatch, single concurrent refresh, refusal clearing, successful retry and cleanup/late-result safety. R016.2 also binds test_canonical_shared_guardrails_preserve_client_boundary. These are controlled fixtures, not a live-server or release receipt.

## Qt lifetime acceptance

R004.2 binds both test_agent_bridge_worker.py tests. R010.2 binds test_output_wrapper_lifecycle.py. They cover queued signal lifetime and stream ownership, not all dispatch or tray behavior. R004.1 and R010.1 retain their original obligations.

R016.1 binds the existing docs-hook regression. R016.2 binds the shared-guardrail regression and requires actual full pre-commit execution.

R001.3 also launches isolated Qt processes that quit during delayed and stalled fetch cleanup. Both must finish the worker and exit without a running-thread abort. The delayed case must finish its finalizer.

## Scoped graph-client failure evidence

GENIUSBOT-CLIENT-R005.1 binds `test_typed_failed_operation_keeps_its_own_error` and `test_non_envelope_gateway_error_still_reads_as_unavailable` in `tests/test_graph_query_wiring.py`. GENIUSBOT-CLIENT-R005.2 binds `test_redirect_envelopes_are_rejected_without_following` and its ten cases. These tests use the production client and adapter with a recording HTTP transport, not a live gateway or Qt UI. Other generic R005 failure paths remain separate qualification work.

R005.3 retains the prior generic R005 obligation and its LANDED state with no test evidence. The generated R005 rollup must not promote that unresolved coverage from the two scoped children.

| GENIUSBOT-CLIENT-R016.3 | Execute the CI setup command with recording package-manager executables | Frozen test-extra sync, Qt libraries, offscreen rendering and supported audio backend precede full tests | Missing declared test extra, unfrozen sync, absent Qt setup or a disabled test scope fails the regression |
