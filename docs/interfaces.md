# Interfaces

Geniusbot runs as a native PySide6 desktop application. Its main platform-facing panels use the shared gateway client to call Graph OS.

| Interface | Role |
| --- | --- |
| Desktop panels | Display graph-backed dashboards, fleet state, metrics, and federated search. |
| Graph OS gateway | Provides the governed gateway and composition surface used by most networked panels. |
| Agent tools | Dynamic forms use schemas discovered from the agent control plane. |
| Embedded terminal | Provides terminal interaction inside the desktop application. |
| Backend adapter | Retains limited direct Agent Utilities paths for workspace graph execution, dashboard configuration and aggregation, and local log-directory resolution. |

Graph OS owns the governed gateway boundary. The remaining adapter paths are documented in the [architecture guide](overview.md); they are not a replacement gateway contract.
