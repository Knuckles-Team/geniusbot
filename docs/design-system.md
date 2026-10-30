# Design system

The cockpit follows the ecosystem Human Interface Guidelines (CONCEPT-HIG).

## Principles

- Navigation stays flat. A panel should need no more than one click.
- Colors come from `axil/qt/colors.py`. Panels must not hard-code palettes.
- Dynamic QPalette and stylesheet theming must keep working in light and dark modes.
- Disruptive prompts use a depth-aware modal, as in `axil/qt/tool_guard.py`.
- Rail navigation animates with `QPropertyAnimation`.
