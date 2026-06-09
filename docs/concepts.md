# Concept Registry — GeniusBot

> **Prefix**: `CONCEPT:GBOT-*`
> **Version**: 3.29.6
> **Bridge**: [`CONCEPT:ECO-4.0`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:GBOT-1.0` | Flat Zero-Nesting GUI | Single-pane cockpit layout split into a flat category sidebar, dynamic card grid, and retractable detail drawers. |
| `CONCEPT:GBOT-2.0` | Dynamic Card Schema Grid | Dynamic QSS-themed form widget building compiled on the fly from introspection of agent specialist schemas. |
| `CONCEPT:GBOT-3.0` | Embedded WebEngine Terminal Panel | Hosts local xterm.js instance running agent-terminal-ui inside the main Qt application context. |
| `CONCEPT:GBOT-4.0` | Zero-Trust Security Tool Guard | Native interceptor modal requiring explicit human operator verification for dangerous tool executions. |
| `CONCEPT:GBOT-5.0` | Background Runnable Workers | Non-blocking specialist discovery and action run loops managed on Qt background thread pools. |
| `CONCEPT:GBOT-6.0` | Snappy Native Finance Charts | High-speed PySide6.QtCharts graphics engine replacement for Matplotlib rendering. |
| `CONCEPT:GBOT-7.0` | Multi-Backend Trade Ingestion | Ingesting tick metrics dynamically from emerald-exchange Paper, CCXT, or predict loops. |
| `CONCEPT:GBOT-8.0` | Unified Parity Finance Cockpit | Feature-complete visual cockpit combining active portfolio grids, order books, and RSS news feeds. |


## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:OS-5.3` | Guardrail Engine | agent-utilities |
| `CONCEPT:OS-5.4` | Audit Logging | agent-utilities |
| `CONCEPT:KG-2.0` | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

GeniusBot interfaces directly with the `agent-utilities` core via `CONCEPT:ECO-4.0`. When GeniusBot boots, it queries the `agent_utilities.agent.discovery` engine to load the list of available specialist agents and auto-renders individual tool widgets. Execution actions pass through the confidence-gated router (`CONCEPT:ORCH-1.2`) and trigger the Zero-Trust Security Tool Guard (`CONCEPT:GBOT-4.0`) to intercept potential system mutations before they are executed.
