# Geniusbot

Geniusbot is the desktop cockpit for the agent platform. It gives operators a native interface for graph-backed panels, agent tools, approvals, and an embedded terminal.

Its primary panels use [Graph OS](https://knuckles-team.github.io/graph-os/) as the governed gateway and composition host. A limited in-process adapter path remains for selected Agent Utilities functions; see the [current architecture](overview.md).

## Start here

- [Architecture](overview.md)
- [Concept registry](concepts.md)
- [Epistemic Graph](https://knuckles-team.github.io/epistemic-graph/)
- [Agent Utilities](https://knuckles-team.github.io/agent-utilities/)
- [Graph OS](https://knuckles-team.github.io/graph-os/)
- [Agent Connector SDK](https://knuckles-team.github.io/agent-connector-sdk/)
- [Agent Web UI](https://knuckles-team.github.io/agent-webui/)

## Install and launch

Use Python 3.12–3.14. Start Graph OS and its platform services, then install and launch Geniusbot:

```bash
python -m pip install geniusbot
geniusbot
```

Gateway-backed panels use `http://localhost:8000` by default. See the [Graph OS documentation](https://knuckles-team.github.io/graph-os/) to configure the gateway and its services.
