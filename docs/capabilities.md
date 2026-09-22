# Capabilities

Geniusbot is a PySide6 desktop cockpit for operator-facing work across the Knuckles Team platform.

- Graph-backed views present metrics, fleet status, and federated search.
- Discovered agent schemas drive dynamic tool forms.
- Sensitive actions require operator confirmation in the desktop interface.
- Background workers keep longer requests off the Qt event loop.
- An embedded terminal provides shell access within the cockpit.

The [architecture guide](overview.md) describes which panels use Graph OS and where limited in-process adapter paths remain.
