# Apps

The cockpit groups its panels into five flat categories: Dashboard, Infra, Media, Productivity and Research.

Each category shows a grid of action cards. One click starts an action.

## Panels

- Fleet cockpit: worker placement and the approval inbox (`geniusbot/qt/fleet_cockpit.py`).
- Metrics: PromQL queries and cache stats (`geniusbot/qt/metrics_panel.py`).
- Federated search: one query across registered graphs (`geniusbot/qt/federated_search_panel.py`).
- Data query: plain-English questions over the graph (`geniusbot/qt/data_query_panel.py`).
- Voice: microphone capture and transcription (`geniusbot/qt/voice_panel.py`).
- Terminal: an embedded xterm.js session (`geniusbot/qt/terminal_widget.py`).
