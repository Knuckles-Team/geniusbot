# Geniusbot

## What this repository owns

Geniusbot is the PySide6 desktop cockpit for operators using the Knuckles Team agent platform. It provides graph-backed panels, capability forms, approval prompts, and an embedded terminal. It is a user interface, not the platform gateway or durable graph store.

## Architecture and module map

Graph OS is the governed gateway and composition host. Agent Utilities owns agent execution and control-plane behavior. Epistemic Graph owns durable graph data and reasoning. Agent Connector SDK connects external systems to the graph.

Most networked Geniusbot panels call Graph OS through `geniusbot/services/gateway_client.py`. `geniusbot/services/backend_adapter.py` retains limited in-process Agent Utilities paths for workspace graph execution, service-dashboard configuration and aggregation, and local log-directory resolution. Do not present those paths as the gateway contract.

- `geniusbot/qt/` contains desktop panels and widgets.
- `geniusbot/services/` contains platform clients and adapters.
- `geniusbot/utils/` contains desktop support services.
- `tests/` contains automated tests.
- `docs/` contains operator and architecture documentation.

## Commands

Use Python 3.12 through 3.14.

```bash
uv sync --all-extras
uv run geniusbot
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
mkdocs build --strict
```

## Quality gates

Run `pre-commit run --all-files` before committing. Run the test suite and strict documentation build when changing application behavior or public documentation. Keep package metadata, lock artifacts, and test expectations consistent when dependencies change.

## Development rules

- Keep Qt event handlers responsive; move blocking work to background workers.
- Keep governed service requests on the Graph OS gateway and retain the documented adapter boundary.
- Keep credentials and operator secrets outside the repository.
- Write concise, accurate documentation with present-tense architecture and display names.
- Add focused tests for behavior changes and keep generated build output out of commits.

## Documentation

The [README](README.md) is the package entry point. The [documentation home](docs/index.md) links to the [architecture guide](docs/overview.md), [capabilities](docs/capabilities.md), [interfaces](docs/interfaces.md), and [status](docs/status.md). The five platform references are [Epistemic Graph](https://knuckles-team.github.io/epistemic-graph/), [Agent Utilities](https://knuckles-team.github.io/agent-utilities/), [Graph OS](https://knuckles-team.github.io/graph-os/), [Agent Connector SDK](https://knuckles-team.github.io/agent-connector-sdk/), and [Agent Web UI](https://knuckles-team.github.io/agent-webui/).

## Branching & isolation

Use a focused branch and commit only reviewed files for the task. Check `git status` and the staged diff before committing. Keep credentials, caches, build output, logs, and scratch files out of version control. Preserve unrelated operator changes in shared checkouts.
