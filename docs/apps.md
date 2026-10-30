# Apps

The cockpit groups its panels into five flat categories: Dashboard, Infra, Media, Productivity and Research.

Each category shows a grid of action cards. One click starts an action.

## Panels

- Fleet cockpit: worker placement and the approval inbox (`axil/qt/fleet_cockpit.py`).
- Metrics: PromQL queries and cache stats (`axil/qt/metrics_panel.py`).
- Federated search: one query across registered graphs (`axil/qt/federated_search_panel.py`).
- Data query: plain-English questions over the graph (`axil/qt/data_query_panel.py`).
- Voice: microphone capture and transcription (`axil/qt/voice_panel.py`).
- Terminal: an embedded xterm.js session (`axil/qt/terminal_widget.py`).
