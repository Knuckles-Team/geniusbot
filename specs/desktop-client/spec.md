# GENIUSBOT-CLIENT-001: Desktop GraphOS operation client

**Owner:** geniusbot

**Delivery:** specified; implementation and acceptance require separate evidence.

**Requirement:** GENIUSBOT-CLIENT-R001 through GENIUSBOT-CLIENT-R012 (the desktop cockpit's
share of the GraphOS operation-client contract, plus its desktop-specific cockpit, approval
and packaging surfaces). See [`requirements.md`](requirements.md) for the full definition of
every requirement ID this spec owns and [`status.json`](status.json) for their current
delivery and acceptance state.

**Related public owners:** the [GraphOS hosted operation service](https://github.com/Knuckles-Team/graph-os/tree/main/specs/hosted-api-operations)
supplies the operation registry, generated client and authorization boundary consumed by
every GraphOS surface. The [terminal GraphOS operation client](https://github.com/Knuckles-Team/agent-terminal-ui/tree/main/specs/terminal-runtime)
states the same shared wire contract for the terminal surface; geniusbot owns its own
consumer implementation and states its own desktop-specific requirements here.

## Purpose and user stories

1. As an operator, I open the cockpit and it discovers the available specialist agents from
   the Knowledge Graph and renders one control card per specialist, so I can run a specialist
   with zero configuration.
2. As an operator, I ask the master copilot a question or run a slash command, and I see the
   typed result or a clear, actionable error; the cockpit never freezes and never reports a
   false success for a failed request.
3. As an operator reviewing the Fleet Supervisor, I see pending autonomous-action approvals
   and can grant or hold each one; my decision is always sent to Graph OS's server-side
   approval authority, never decided inside the desktop process.
4. As an operator, I use the embedded terminal, chat, graph explorer, telemetry, security
   policy, infrastructure, finance, service dashboard, fleet, usage, extraction, temporal
   graph, ask-data, metrics, federated-search and voice-dictation views from one flat
   sidebar, without the cockpit loading code for views I never open.
5. As a user on Windows, macOS or Linux, I can install the cockpit from PyPI, run a single
   bundled executable, or use a platform-native installer/desktop entry, and launch the same
   application.

## Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| GENIUSBOT-CLIENT-R001 | Every panel and the main window reach Graph OS only through the shared gateway client facade and the single `BackendAdapter` seam. | Source-tree import-scan test |
| GENIUSBOT-CLIENT-R002.1 | A typed registry-entry model and validator refuse a malformed or duplicate registry entry. | `tests/test_operation_registry.py` |
| GENIUSBOT-CLIENT-R002.2 | `/op`-equivalent and specialist invocations validate against the installed generated operation registry before any network call. | Unit tests on unknown/mismatched operations |
| GENIUSBOT-CLIENT-R003 | The caller's verified credential reaches Graph OS only over TLS for non-loopback hosts; every response is bounded. | Endpoint-validation and bounded-body tests |
| GENIUSBOT-CLIENT-R004 | All network/reasoning work dispatches off the Qt UI thread through typed signals. | Worker signal-contract tests |
| GENIUSBOT-CLIENT-R005 | Every facade failure mode resolves to a typed error/offline result, never an uncaught exception or false success. | Timeout/disconnect/exception unit tests |
| GENIUSBOT-CLIENT-R006 | No code path authorizes a governed action locally; every approval decision is forwarded to Graph OS's server-side endpoint. | Approval-forwarding contract test |
| GENIUSBOT-CLIENT-R007 | The embedded terminal view hosts an interactive shell over a PTY/conpty bridge, started lazily. | Instantiation + lazy-start tests |
| GENIUSBOT-CLIENT-R008 | Every secondary cockpit view loads lazily, exactly once, on first navigation. | Per-index characterization test |
| GENIUSBOT-CLIENT-R009 | The voice-dictation panel renders no-device, recorder-failure, backend-unavailable and generic-error states distinctly. | Per-state unit tests |
| GENIUSBOT-CLIENT-R010 | A tray daemon keeps the cockpit resident; closing the window minimizes to tray while the tray is active. | Tray action + close-event tests |
| GENIUSBOT-CLIENT-R011 | The specialist deck is discovered and rendered dynamically from declared skills/capabilities. | Discovery + control-card field tests |
| GENIUSBOT-CLIENT-R012.1 | A typed packaging manifest model and validator refuse an incomplete manifest (missing target, missing field, or version mismatch), with no build tool invoked. | `tests/test_packaging_manifest.py` |
| GENIUSBOT-CLIENT-R012.2 | The client packages as a pip install, a bundled executable, a Windows installer and a Linux desktop entry. | Packaging build + launch check |

## Scenarios and failure behavior

- Given a reachable Graph OS gateway, the cockpit's startup timer fetches specialists and
  populates the deck without blocking the window from opening.
- Given an unreachable gateway, every affected panel (specialist deck, health check,
  copilot chat, fleet supervisor, voice dictation, graph/ask-data/metrics/federated-search
  panels) shows a clear offline/error state and the rest of the cockpit remains usable.
- Given an unknown or mismatched Graph OS operation, the client makes no network request and
  surfaces a clear unavailable result.
- Given a pending `ActionPolicy` approval in the Fleet Supervisor, granting it sends the
  decision to the gateway's approval endpoint; the desktop process never marks the action
  authorized on its own.
- Given the terminal view is opened for the first time, its backing shell starts exactly
  once; reopening the view does not restart it.
- Given no capture device, a denied microphone permission, a backend route that answers
  404/501, or a genuine transcription failure, the voice panel renders a distinct message
  for each one.
- Given the main window is closed while the tray icon is visible, the cockpit hides to the
  tray instead of exiting; exiting from the tray menu stops the daemon and closes the
  process.

## Success and scope

Success requires the positive and negative scenarios above, each requirement's listed
acceptance evidence, and a packaged, launchable build on each target platform. A source
commit or a unit-test pass alone is not acceptance; a served end-to-end approval receipt is
required before GENIUSBOT-CLIENT-R006 can be marked accepted. This specification does not
own Graph OS's operation registry, generated client, or server-side authorization boundary,
the `agent-terminal-ui` client's own requirements, or the Knowledge Graph's persistence or
reasoning behavior.

## Traceability

Current delivery and acceptance state for each requirement ID above is recorded in
[`status.json`](status.json), not here.

| Local ownership | Other owner contract |
|---|---|
| This cockpit's gateway facade, backend-adapter seam, cockpit/dashboard views, tray daemon and packaging (`GENIUSBOT-CLIENT-R001`-`R012`) | Graph OS's generated operation client, versioned HTTP envelope and server-side authorization/approval boundary (see the links above); `agent-terminal-ui` implements its own consumer |
| Displaying and forwarding an approval decision, never deciding it locally | Graph OS's signed approval authority and durable human identity, proven end to end before an approval action can be accepted |
