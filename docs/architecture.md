# Architecture

Axil is a PySide6 (Qt6) desktop cockpit. It talks to Arbora through the gateway client in `meristem`.

## Layers

- `axil/axil.py` builds the main window and the system tray.
- `axil/qt/` holds the cockpit panels, the terminal widget and the tool guard.
- `axil/services/` holds the packaging commands and backend adapters.
- `axil/utils/` holds the agent bridge and the background daemon.

## Rules

- Qt calls must run on the UI thread. Long work must run on `QThreadPool`.
- The backend owns orchestration, graph memory and policy. The cockpit must reuse its clients.

See the [technical overview](overview.md) for diagrams.
