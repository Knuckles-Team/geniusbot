# Geniusbot architecture

Geniusbot is a PySide6 desktop entry point for the agent platform. It provides operator-facing graph, fleet, metrics, search, tool, and terminal panels.

## Platform boundary

Graph OS is the governed gateway and composition host. Agent Utilities owns agent execution and control-plane behavior. Epistemic Graph owns durable graph storage, ontology, and reasoning. Agent Connector SDK connects external systems to the graph.

![Knuckles-Team runtime architecture](https://raw.githubusercontent.com/Knuckles-Team/pipelines/64e34ca63385200f5ddfef5286e6886bf7dc80b4/templates/mkdocs-theme/assets/runtime-architecture.svg)

## Geniusbot request paths

Most networked panels use `GatewayClient` to call Graph OS. The desktop UI sends longer work through background workers so the Qt event loop remains responsive.

`BackendAdapter` retains a limited in-process Agent Utilities path for workspace graph execution, service-dashboard configuration and aggregation, and local log-directory resolution. This path is used by specific panels; it is not the gateway contract.

## Operator approvals

The tool guard presents sensitive actions and their arguments for operator approval before execution. The UI provides the confirmation step; Graph OS remains the platform gateway and policy boundary for governed service requests.

## Related documentation

- [Geniusbot documentation home](index.md)
- [Concept registry](concepts.md)
- [Epistemic Graph](https://knuckles-team.github.io/epistemic-graph/)
- [Agent Utilities](https://knuckles-team.github.io/agent-utilities/)
- [Graph OS](https://knuckles-team.github.io/graph-os/)
- [Agent Connector SDK](https://knuckles-team.github.io/agent-connector-sdk/)
- [Agent Web UI](https://knuckles-team.github.io/agent-webui/)
