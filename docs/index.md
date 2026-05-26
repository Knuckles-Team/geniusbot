# GeniusBot — Desktop Cockpit for AI Agents

Welcome to **GeniusBot**, the premium, unified space cockpit and visual control deck built on top of the `agent-utilities` powerhouse backend.

GeniusBot integrates all 37+ specialist agent and MCP packages from our multi-agent ecosystem into a single-pane-of-glass user interface, offering 1-click execution, embedded hybrid terminals, zero-nesting visual layouts, and a zero-trust hardware protection layer.

---

## 🚀 Key Features

* **Zero-Nesting Dynamic UI**: Avoid deep click-through menus with flat left sidebar navigation and dynamic agent grid decks.
* **Asynchronous Execution Threading**: Main Qt event loops remain highly responsive utilizing custom `QRunnable` worker pools.
* **Embedded xterm.js Hybrid Terminal**: Direct terminal window launching for `agent-terminal-ui` inside the main GUI tab.
* **Tool-Guard Authorization Modal**: A strict interceptor boundary protecting user systems from dangerous agent mutations.
* **Automated Package Parity**: Auto-maps specialist tool schemas into QSS-themed form widgets on the fly.

---

## 🛠️ Quick Start

### Prerequisites
* Python 3.10+
* [uv](https://github.com/astral-sh/uv) (recommended)
* Active `agent-utilities` backend environment

### Installation
Install dependencies and build with `uv`:
```bash
# Clone the repository
git clone https://github.com/Knuckles-Team/geniusbot.git
cd geniusbot

# Setup virtual environment and sync
uv venv
uv pip sync requirements.txt
```

### Launch
To start the cockpit in desktop mode:
```bash
uv run geniusbot
```

To run in headless or virtual environments (CI/CD):
```bash
QT_QPA_PLATFORM=offscreen uv run geniusbot
```
