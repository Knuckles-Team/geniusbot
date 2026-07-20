# Concept Registry — GeniusBot

> **Prefix**: `CONCEPT:GBOT-*`
> **Version**: 3.29.6
> **Bridge**: [`CONCEPT:AU-ECO.messaging.native-backend-abstraction`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:GB-GBOT.cockpit.gbot` | Flat Zero-Nesting GUI | Single-pane cockpit layout split into a flat category sidebar, dynamic card grid, and retractable detail drawers. |
| `CONCEPT:GB-GBOT.cockpit.gbot-2` | Dynamic Card Schema Grid | Dynamic QSS-themed form widget building compiled on the fly from introspection of agent specialist schemas. |
| `CONCEPT:GB-GBOT.cockpit.gbot-3` | Embedded WebEngine Terminal Panel | Hosts local xterm.js instance running agent-terminal-ui inside the main Qt application context. |
| `CONCEPT:GB-GBOT.cockpit.gbot-4` | Zero-Trust Security Tool Guard | Native interceptor modal requiring explicit human operator verification for dangerous tool executions. |
| `CONCEPT:GB-GBOT.cockpit.gbot-5` | Background Runnable Workers | Non-blocking specialist discovery and action run loops managed on Qt background thread pools. |
| `CONCEPT:AU-GBOT.cockpit.through-gbot` | Snappy Native Finance Charts | High-speed PySide6.QtCharts graphics engine replacement for Matplotlib rendering. |
| `CONCEPT:GB-GBOT.cockpit.multi-backend-ingestion-simulated` | Multi-Backend Trade Ingestion | Ingesting tick metrics dynamically from emerald-exchange Paper, CCXT, or predict loops. |
| `CONCEPT:GB-GBOT.cockpit.unified-parity-finance-cockpit` | Unified Parity Finance Cockpit | Feature-complete visual cockpit combining active portfolio grids, order books, and RSS news feeds. |


## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:AU-ECO.messaging.native-backend-abstraction` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:AU-ORCH.adapter.hot-cache-invalidation` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:AU-OS.governance.reactive-multi-axis-budget` | Guardrail Engine | agent-utilities |
| `CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox` | Audit Logging | agent-utilities |
| `CONCEPT:AU-KG.query.object-graph-mapper` | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

GeniusBot interfaces directly with the `agent-utilities` core via `CONCEPT:AU-ECO.messaging.native-backend-abstraction`. When GeniusBot boots, it queries the `agent_utilities.agent.discovery` engine to load the list of available specialist agents and auto-renders individual tool widgets. Execution actions pass through the confidence-gated router (`CONCEPT:AU-ORCH.adapter.hot-cache-invalidation`) and trigger the Zero-Trust Security Tool Guard (`CONCEPT:GB-GBOT.cockpit.gbot-4`) to intercept potential system mutations before they are executed.
