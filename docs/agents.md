# Agents

GeniusBot discovers the specialist agents of the ecosystem and shows each one as a panel.

- `geniusbot/plugins/` scans the agent packages and adds a control widget per agent.
- `geniusbot/utils/agent_bridge.py` sends queries to the backend off the UI thread.
- The tool guard asks for approval before an agent runs a risky command.
- The background daemon runs scheduled agent tasks from the system tray.
