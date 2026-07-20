#!/usr/bin/env python3
"""Temporal graph scrubber panel (CONCEPT:GB-GBOT.cockpit.gbot-7).

A thin cockpit panel that adds a bi-temporal time scrubber over the existing
force-directed graph renderer (:class:`ForceGraphWidget`). The user drags a
``QSlider`` to pick a historical instant; on change the panel re-issues the base
graph query with the engine's ``|> AS OF @<ts>`` operator (KG-2.250) appended,
and rebuilds the graph at that instant. Edges that have expired by the selected
timestamp render greyed and dashed (see ``ForceGraphWidget._redraw``).

The panel holds no business logic: it adapts the slider position into a query
suffix (via :func:`with_as_of`) and into an ``expired`` flag per fact (via
:func:`mark_expired`), then hands facts to the renderer. Query/expiry math are
pure functions so they are unit-testable without a display, and the only backend
seam used is ``backend.run_graph_query`` through the worker — keeping the
``agent_utilities`` import confined to ``backend_adapter`` (coupling rule).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.force_graph import ForceGraphWidget

# Base query re-issued at each scrubber instant; the backend translates UQL.
BASE_UQL = "MATCH (n) RETURN n LIMIT 200"

# Scrubber span: the last 30 days mapped onto a 0..100 slider.
_WINDOW_DAYS = 30
_SLIDER_MAX = 100


def with_as_of(query: str, iso_ts: str) -> str:
    """Append the bi-temporal ``|> AS OF @<ts>`` operator to a UQL query.

    Args:
        query: The base UQL query string.
        iso_ts: An ISO-8601 timestamp.

    Returns:
        The query with the temporal operator appended.
    """
    return f"{query.strip()} |> AS OF @{iso_ts}"


def slider_to_iso(pos: int, *, now: datetime | None = None) -> str:
    """Map a 0..100 slider position to an ISO-8601 timestamp.

    Position 0 is ``_WINDOW_DAYS`` ago; position 100 is ``now``.

    Args:
        pos: Slider position in ``[0, _SLIDER_MAX]``.
        now: Optional reference "now" (for deterministic tests).

    Returns:
        An ISO-8601 timestamp string.
    """
    ref = now or datetime.now(UTC)
    start = ref - timedelta(days=_WINDOW_DAYS)
    frac = max(0, min(_SLIDER_MAX, pos)) / _SLIDER_MAX
    ts = start + (ref - start) * frac
    return ts.isoformat()


def mark_expired(facts: list[dict[str, Any]], iso_ts: str) -> list[dict[str, Any]]:
    """Return copies of ``facts`` flagged ``expired`` when no longer live at ts.

    A fact is expired when it carries a ``valid_until`` that is a non-null
    ISO-8601 string lexicographically ``<= iso_ts`` (ISO strings sort
    chronologically). Facts without ``valid_until`` are considered live.

    Args:
        facts: Fact dicts (subject/predicate/object, optionally valid_until).
        iso_ts: The current scrubber timestamp.

    Returns:
        New fact dicts with an ``expired`` boolean set.
    """
    out: list[dict[str, Any]] = []
    for fact in facts:
        valid_until = fact.get("valid_until")
        expired = (
            isinstance(valid_until, str) and bool(valid_until) and valid_until <= iso_ts
        )
        out.append({**fact, "expired": expired})
    return out


class TemporalGraphPanel(QWidget):
    """Force-directed graph with a bi-temporal AS OF time scrubber."""

    def __init__(self, worker, parent=None) -> None:
        super().__init__(parent)
        self.worker = worker
        self._facts: list[dict[str, Any]] = []
        self.initialize_ui()

    def initialize_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_lbl = QLabel("🕰️ Temporal Graph Scrubber")
        title_lbl.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #7C4DFF; margin-bottom: 5px;"
        )
        layout.addWidget(title_lbl)

        subtitle_lbl = QLabel(
            "Scrub through time: the graph re-renders at the selected instant and "
            "edges expired by then are greyed and dashed."
        )
        subtitle_lbl.setStyleSheet(
            "color: #8A8A93; font-size: 12px; margin-bottom: 10px;"
        )
        layout.addWidget(subtitle_lbl)

        # ── Scrubber row ──
        scrub_row = QHBoxLayout()
        scrub_row.setSpacing(10)
        scrub_row.addWidget(QLabel("Past"))

        self.slider = QSlider(Qt.Horizontal)  # type: ignore[attr-defined]  # PySide6 Qt.Horizontal enum (incomplete stubs)
        self.slider.setMinimum(0)
        self.slider.setMaximum(_SLIDER_MAX)
        self.slider.setValue(_SLIDER_MAX)  # default to "now"
        self.slider.valueChanged.connect(self.on_scrub)
        scrub_row.addWidget(self.slider, stretch=1)

        scrub_row.addWidget(QLabel("Now"))
        layout.addLayout(scrub_row)

        self.ts_label = QLabel(f"AS OF {slider_to_iso(_SLIDER_MAX)}")
        self.ts_label.setStyleSheet(
            "color: #F5F5F7; font-family: monospace; font-size: 12px;"
        )
        layout.addWidget(self.ts_label)

        self.graph = ForceGraphWidget()
        layout.addWidget(self.graph, stretch=1)

    # -- scrubbing -------------------------------------------------------- #

    def current_query(self) -> str:
        """The UQL query for the current slider position, with AS OF appended."""
        return with_as_of(BASE_UQL, slider_to_iso(self.slider.value()))

    def on_scrub(self, pos: int) -> None:
        """Re-issue the AS OF query for the new slider position and re-render."""
        iso_ts = slider_to_iso(pos)
        self.ts_label.setText(f"AS OF {iso_ts}")
        query = with_as_of(BASE_UQL, iso_ts)

        async def query_runner():
            from geniusbot.services.backend_adapter import backend

            res = await backend.run_graph_query(query)
            return res or []

        def on_done(results):
            self.render_facts(self._rows_to_facts(results), iso_ts)

        def on_fail(_err):
            # On failure leave the prior render in place; re-flag the cached facts.
            self.render_facts(self._facts, iso_ts)

        self.worker.run_agent_task(query_runner, on_finished=on_done, on_error=on_fail)

    @staticmethod
    def _rows_to_facts(results: Any) -> list[dict[str, Any]]:
        """Normalize backend rows into fact dicts the renderer understands."""
        facts: list[dict[str, Any]] = []
        if not isinstance(results, list):
            return facts
        for row in results:
            if isinstance(row, dict):
                facts.append(row)
            elif isinstance(row, (list, tuple)) and len(row) >= 3:
                facts.append({"subject": row[0], "predicate": row[1], "object": row[2]})
        return facts

    def render_facts(self, facts: list[dict[str, Any]], iso_ts: str) -> None:
        """Rebuild the graph from ``facts`` at ``iso_ts``, marking expired edges."""
        self._facts = facts
        self.graph.clear_graph()
        for fact in mark_expired(facts, iso_ts):
            self.graph.add_fact(fact)
