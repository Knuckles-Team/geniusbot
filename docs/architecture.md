# Architecture

GeniusBot is a PySide6 (Qt6) desktop cockpit. It talks to Arbora through the gateway client in `agent-utilities`.

## Layers

- `geniusbot/geniusbot.py` builds the main window and the system tray.
- `geniusbot/qt/` holds the cockpit panels, the terminal widget and the tool guard.
- `geniusbot/services/` holds the packaging commands and backend adapters.
- `geniusbot/utils/` holds the agent bridge and the background daemon.

## Rules

- Qt calls must run on the UI thread. Long work must run on `QThreadPool`.
- The backend owns orchestration, graph memory and policy. The cockpit must reuse its clients.

See the [technical overview](overview.md) for diagrams.
