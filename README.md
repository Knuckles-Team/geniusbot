# Geniusbot

<p align="center"><img src="https://raw.githubusercontent.com/Knuckles-Team/pipelines/64e34ca63385200f5ddfef5286e6886bf7dc80b4/templates/mkdocs-theme/assets/brands/geniusbot-logo-v1.png" alt="Geniusbot logo" width="160"></p>

[![PyPI version](https://img.shields.io/pypi/v/geniusbot)](https://pypi.org/project/geniusbot/)
[![License](https://img.shields.io/github/license/Knuckles-Team/geniusbot)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-526CFE)](https://knuckles-team.github.io/geniusbot/)

Geniusbot is the desktop cockpit for the agent platform. It gives operators a native PySide6 interface for graph-backed panels, agent tools, approvals, and an embedded terminal.

## Overview

Geniusbot is a user entry point alongside Agent Terminal UI, Agent Web UI, and Graph OS messaging. Its primary panels use Graph OS as the governed gateway and composition host. Agent Utilities supplies the agent control plane, and Epistemic Graph owns durable graph data and reasoning.

## Key capabilities

- Desktop dashboards and panels for graph queries, metrics, fleet status, and federated search.
- Dynamic tool forms built from discovered agent schemas.
- Operator approval prompts for sensitive actions.
- Background workers that keep long-running requests off the Qt event loop.
- An embedded xterm.js terminal.

## Documentation

- [Geniusbot documentation](https://knuckles-team.github.io/geniusbot/)
- [Current architecture](docs/overview.md)
- [Concept registry](docs/concepts.md)
- [Epistemic Graph](https://knuckles-team.github.io/epistemic-graph/)
- [Agent Utilities](https://knuckles-team.github.io/agent-utilities/)
- [Graph OS](https://knuckles-team.github.io/graph-os/)
- [Agent Connector SDK](https://knuckles-team.github.io/agent-connector-sdk/)
- [Agent Web UI](https://knuckles-team.github.io/agent-webui/)

## Architecture

![Knuckles-Team runtime architecture](https://raw.githubusercontent.com/Knuckles-Team/pipelines/64e34ca63385200f5ddfef5286e6886bf7dc80b4/templates/mkdocs-theme/assets/runtime-architecture.svg)

Graph OS owns the governed gateway and composes the platform services. Most Geniusbot panels reach those services through the shared gateway client. A limited in-process adapter path remains for workspace graph execution and service-dashboard configuration/data, and the adapter resolves the local log directory through Agent Utilities.

## Quick start

Start Graph OS with its platform services, then install Geniusbot with Python 3.12–3.14:

```bash
python -m pip install geniusbot
geniusbot
```

Gateway-backed panels use `http://localhost:8000` by default. See the [Graph OS deployment guide](https://knuckles-team.github.io/graph-os/) for service configuration.

## Contributing

Issues and pull requests are welcome in the [Geniusbot repository](https://github.com/Knuckles-Team/geniusbot).

## License

Geniusbot is released under the [MIT License](LICENSE).
