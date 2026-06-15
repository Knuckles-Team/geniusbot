# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **KG extraction cockpit with native force graph (`CONCEPT:ECO-4.43`)**: `extraction_cockpit.py` (`ExtractionCockpitPanel`) brings the document→KG experience to the Qt cockpit over the real gateway with live SSE — text/URL input streams extracted facts onto `force_graph.py`, a native `QGraphicsView` force-directed widget (pure, unit-testable Fruchterman-Reingold `relax_layout`) where each fact is a clickable directed edge and node keys are normalized to mirror the backend.
- **Usage & Cost cockpit (`CONCEPT:ECO-4.41`)**: `UsageCockpitPanel` (sidebar 💰 Usage & Cost) with agentsview parity — KPI cards, cost-by-model, tool/skill/db-call metrics, a day×hour heatmap, top-sessions browser, and Langfuse links, all over the shared SDK facade via the `QThreadPool` worker (never blocks the Qt loop, graceful-offline).
- Documented previously missing environment variables (`QT_QPA_PLATFORM`, `TERM`, `_MEIPASS`, `_MEIPASS2`) in `.env.example` and `README.md`.
- Expanded `AGENTS.md` with explicit project structure rules.

### Changed
- Bumped dependency constraints for `pytest-qt`, `PySide6`, `agent-utilities`, and `ruff` in `pyproject.toml` to address code audit findings.
- Replaced `pypiwin32` with `pywin32` in `pyproject.toml` dependencies.
- Updated `ruff-pre-commit` hook to `v0.15.15` in `.pre-commit-config.yaml`.
## [3.29.6] - 2026-05-25

### Added
- **Visual Finance Dashboard Panel (`finance_cockpit.py`)**: Renders high-performance native `PySide6.QtCharts` supporting candlestick charts, line charts, bid/ask depth volume graphs, togglable RSI/MACD strategy indicators, and background-loaded RSS financial news feeds. Integrates CCXT, Paper, Alpaca, and Polymarket simulated feeds (`CONCEPT:GBOT-6.0`, `CONCEPT:GBOT-7.0`, `CONCEPT:GBOT-8.0`).
- **Integrated Systems Cockpit panels**: Renders 5 modular space-dark visual monitors:
  * `graph_explorer.py` — Cypher shells + interactive node graph views.
  * `telemetry_dashboard.py` — Health success dial gauges + logfire trace lists.
  * `workflow_builder.py` — specialist agent pipeline layout + swarm debate console logs.
  * `security_policy.py` — Zero-Trust permission grid checkboxes + strictness slider.
  * `infra_cockpit.py` — Docker stack container tables + SSH tunnels map load meters.
- **Embedded Hybrid Terminal (`terminal_widget.py`)**: Hosts local xterm.js sessions via QWebEngineView + high-speed QWebChannel streams (`CONCEPT:GBOT-3.0`).
- **Dynamic Widget Schema Mapper (`widget_mapper.py`)**: Generates premium widgets from agent schemas on the fly (`CONCEPT:GBOT-2.0`).
- **Ecosystem Packaging Infrastructure**:
  * Added `setup.iss` Inno Setup compiler config to package Windows standalone executables.
  * Added `packaging/linux/control` and `packaging/linux/geniusbot.desktop` Debian configuration templates.
  * Added reusable Github workflow `pipelines/.github/workflows/desktop_release_pipeline.yml` to compile and distribute `.deb`, `.rpm`, `.exe` multi-platform releases.
- **Packaging Files**: Added `.bumpversion.cfg`, `.env`, `.env.example`, `requirements.txt`, and modern `pyproject.toml` Hatchling builds.
- **Headless Test Framework**: Added `tests/conftest.py` with session-scoped `qapp` fixtures, `tests/test_init_dynamics.py` import checks, `tests/test_concept_parity.py` registry validation, and `tests/test_cockpit_views.py` views verification.

### Changed
- Migrated core UI system from legacy PyQt6 to PySide6 and refactored startup to use async thread pools (`AgentBridgeWorker` / `CONCEPT:GBOT-5.0`).
- Updated central stack widget layouts to support left category navigation sidebars, action card decks, and retracting details drawers.

### Removed
- Safely deprecated and deleted all legacy plugins in `geniusbot/plugins/` (including subshift, webarchiver, systems manager, rom manager, media manager) and stripped `setup.py` packaging structures.
