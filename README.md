# Geniusbot

<p align="center"><img src="docs/assets/brands/geniusbot-logo-v1.png" alt="Geniusbot logo" width="160"></p>

<p align="center"><strong>A desktop cockpit for governed agent operations.</strong><br><sub>Explore graph-backed panels, agent tools, approvals, and an embedded terminal.</sub></p>

[![PyPI - Version](https://img.shields.io/pypi/v/geniusbot)](https://pypi.org/project/geniusbot/) [![PyPI - Downloads](https://img.shields.io/pypi/dd/geniusbot)](https://pypi.org/project/geniusbot/) [![PyPI - License](https://img.shields.io/pypi/l/geniusbot)](https://pypi.org/project/geniusbot/) [![PyPI - Wheel](https://img.shields.io/pypi/wheel/geniusbot)](https://pypi.org/project/geniusbot/) [![PyPI - Implementation](https://img.shields.io/pypi/implementation/geniusbot)](https://pypi.org/project/geniusbot/)

[![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot) [![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot) [![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot) [![GitHub license](https://img.shields.io/github/license/Knuckles-Team/geniusbot)](LICENSE) [![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot/commits/main)

[![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot/pulls) [![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot/pulls?q=is%3Apr+is%3Aclosed) [![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot/issues) [![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot) [![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot) [![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot) [![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/geniusbot)](https://github.com/Knuckles-Team/geniusbot)

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-526CFE)](https://knuckles-team.github.io/geniusbot/)

<p align="center"><a href="https://knuckles-team.github.io/geniusbot/">Documentation</a> · <a href="https://knuckles-team.github.io/geniusbot/capabilities/">Capabilities</a> · <a href="https://knuckles-team.github.io/geniusbot/interfaces/">Interfaces</a> · <a href="https://knuckles-team.github.io/geniusbot/status/">Status</a></p>

## Overview

Geniusbot is a PySide6 desktop entry point for the agent platform. Its primary panels use [Graph OS](https://knuckles-team.github.io/graph-os/) as the governed gateway and composition host. [Agent Utilities](https://knuckles-team.github.io/agent-utilities/) provides the agent control plane, while [Epistemic Graph](https://knuckles-team.github.io/epistemic-graph/) owns durable graph data and reasoning.

## Key capabilities

- Graph-backed dashboards for metrics, fleet status, and federated search.
- Dynamic tool forms built from discovered agent schemas.
- Operator confirmation for sensitive actions.
- Background workers for long-running requests and an embedded terminal.

## Documentation

- [Documentation home](https://knuckles-team.github.io/geniusbot/)
- [Capabilities](https://knuckles-team.github.io/geniusbot/capabilities/)
- [Interfaces](https://knuckles-team.github.io/geniusbot/interfaces/)
- [Status](https://knuckles-team.github.io/geniusbot/status/)
- [Architecture](docs/overview.md)
- Core projects: [Epistemic Graph](https://knuckles-team.github.io/epistemic-graph/), [Agent Utilities](https://knuckles-team.github.io/agent-utilities/), [Graph OS](https://knuckles-team.github.io/graph-os/), [Agent Connector SDK](https://knuckles-team.github.io/agent-connector-sdk/), and [Agent Web UI](https://knuckles-team.github.io/agent-webui/).

## Architecture

![Knuckles-Team runtime architecture](docs/assets/runtime-architecture.svg)

Most networked panels call Graph OS through the shared gateway client. A limited in-process adapter path remains for workspace graph execution, service-dashboard configuration and aggregation, and local log-directory resolution. See the [current architecture](docs/overview.md) for these boundaries.

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
