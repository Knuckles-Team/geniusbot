"""Native force-directed graph widget for knowledge-graph facts (CONCEPT:ECO-4.43).

A lightweight QGraphicsView force graph: each fact is a directed edge
``(subject) -[predicate]-> (object)`` between canonical entity nodes; hovering or
clicking an edge surfaces the full fact card. The layout math (`relax_layout`) is
a pure function so it can be unit-tested without a display, matching the upstream
force-graph experience on our Qt cockpit.
"""

from __future__ import annotations

import math
import re
import unicodedata

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


def normalize_key(s: str) -> str:
    """Canonical node key — mirrors ExtractedFact.normalize_key on the backend."""
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[\s ]+", " ", s)
    s = re.sub(r"^[\s\"'`([{]+|[\s\"'`)\]}.,;:!?]+$", "", s)
    return s.strip()


def relax_layout(
    positions: dict[str, tuple[float, float]],
    edges: list[tuple[str, str]],
    *,
    iterations: int = 1,
    k: float = 120.0,
    repulsion: float = 9000.0,
    center: tuple[float, float] = (0.0, 0.0),
) -> dict[str, tuple[float, float]]:
    """One or more Fruchterman-Reingold-style relaxation steps (pure).

    Returns new positions; deterministic given the inputs (no RNG), so it is
    unit-testable. Disconnected nodes are pulled gently toward ``center`` so the
    graph stays on-screen.
    """
    pos = {n: [x, y] for n, (x, y) in positions.items()}
    nodes = list(pos.keys())
    for _ in range(max(1, iterations)):
        disp = {n: [0.0, 0.0] for n in nodes}
        # repulsion between every pair
        for i, a in enumerate(nodes):
            for b in nodes[i + 1 :]:
                dx = pos[a][0] - pos[b][0]
                dy = pos[a][1] - pos[b][1]
                dist2 = dx * dx + dy * dy or 0.01
                force = repulsion / dist2
                dist = math.sqrt(dist2)
                ux, uy = dx / dist, dy / dist
                disp[a][0] += ux * force
                disp[a][1] += uy * force
                disp[b][0] -= ux * force
                disp[b][1] -= uy * force
        # attraction along edges
        for s, t in edges:
            if s not in pos or t not in pos:
                continue
            dx = pos[s][0] - pos[t][0]
            dy = pos[s][1] - pos[t][1]
            dist = math.sqrt(dx * dx + dy * dy) or 0.01
            force = (dist * dist) / k
            ux, uy = dx / dist, dy / dist
            disp[s][0] -= ux * force
            disp[s][1] -= uy * force
            disp[t][0] += ux * force
            disp[t][1] += uy * force
        # gravity toward center + integrate (capped step)
        for n in nodes:
            disp[n][0] += (center[0] - pos[n][0]) * 0.02
            disp[n][1] += (center[1] - pos[n][1]) * 0.02
            mag = math.sqrt(disp[n][0] ** 2 + disp[n][1] ** 2) or 1.0
            step = min(mag, 30.0)
            pos[n][0] += disp[n][0] / mag * step
            pos[n][1] += disp[n][1] / mag * step
    return {n: (xy[0], xy[1]) for n, xy in pos.items()}


class ForceGraphWidget(QGraphicsView):
    """Interactive force-directed view of extracted facts."""

    edge_selected = Signal(dict)  # emits the fact dict when an edge is clicked

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._positions: dict[str, tuple[float, float]] = {}
        self._edges: list[tuple[str, str]] = []  # (s_key, o_key)
        self._facts: list[dict] = []
        self._node_items: dict[str, QGraphicsEllipseItem] = {}
        self._degree: dict[str, int] = {}
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    # -- data ------------------------------------------------------------- #

    def clear_graph(self) -> None:
        self._scene.clear()
        self._positions.clear()
        self._edges.clear()
        self._facts.clear()
        self._node_items.clear()
        self._degree.clear()

    def add_fact(self, fact: dict) -> None:
        """Add one fact edge (+ its nodes); kicks the layout/redraw timer."""
        s_key = normalize_key(fact.get("subject", "")) or "?"
        o_key = normalize_key(fact.get("object", "")) or "?"
        idx = len(self._facts)
        for key in (s_key, o_key):
            if key not in self._positions:
                # deterministic seed placement on a ring (no RNG)
                ang = (len(self._positions) * 137.5) * math.pi / 180.0
                r = 40 + 8 * len(self._positions)
                self._positions[key] = (r * math.cos(ang), r * math.sin(ang))
            self._degree[key] = self._degree.get(key, 0) + 1
        self._edges.append((s_key, o_key))
        self._facts.append(fact)
        self._node_labels = getattr(self, "_node_labels", {})
        self._node_labels[s_key] = fact.get("subject", s_key)
        self._node_labels[o_key] = fact.get("object", o_key)
        # remember which fact each edge index maps to
        if not self._timer.isActive():
            self._timer.start(60)
        # run a few immediate relaxation steps + draw so the edge is clickable
        # right away (the timer continues animating afterwards)
        self._positions = relax_layout(self._positions, self._edges, iterations=2)
        self._redraw()
        _ = idx

    # -- layout/redraw ---------------------------------------------------- #

    def _tick(self) -> None:
        self._positions = relax_layout(self._positions, self._edges, iterations=1)
        self._redraw()

    def _redraw(self) -> None:
        self._scene.clear()
        self._node_items.clear()
        labels = getattr(self, "_node_labels", {})
        # edges first (under nodes)
        for i, (s, t) in enumerate(self._edges):
            if s not in self._positions or t not in self._positions:
                continue
            x1, y1 = self._positions[s]
            x2, y2 = self._positions[t]
            fact = self._facts[i]
            dup = bool(fact.get("is_duplicate"))
            line = _EdgeItem(x1, y1, x2, y2, fact, self.edge_selected)  # type: ignore[arg-type]  # PySide6 SignalInstance vs Signal (incomplete stubs)
            color = QColor(180, 60, 60) if dup else QColor(120, 120, 130)
            line.setPen(QPen(color, 2.4 if not dup else 1.0))
            self._scene.addItem(line)
        # nodes
        for key, (x, y) in self._positions.items():
            r = 6 + min(10, self._degree.get(key, 1) * 1.5)
            item = QGraphicsEllipseItem(x - r / 2, y - r / 2, r, r)
            item.setBrush(QColor(26, 26, 30))
            item.setPen(QPen(QColor(0, 229, 255), 1))
            self._scene.addItem(item)
            self._node_items[key] = item
            text = QGraphicsSimpleTextItem(labels.get(key, key))
            text.setBrush(QColor(228, 228, 231))
            text.setPos(x + r, y - r)
            self._scene.addItem(text)
        if self._scene.itemsBoundingRect().isValid():
            self.setSceneRect(
                self._scene.itemsBoundingRect().adjusted(-40, -40, 40, 40)
            )

    def fact_count(self) -> int:
        return len(self._facts)

    def node_count(self) -> int:
        return len(self._positions)


class _EdgeItem(QGraphicsLineItem):
    """A clickable fact edge that emits its fact dict on click."""

    def __init__(self, x1, y1, x2, y2, fact: dict, signal: Signal) -> None:
        super().__init__(x1, y1, x2, y2)
        self._fact = fact
        self._signal = signal
        self.setAcceptHoverEvents(True)
        title = fact.get("title") or (
            f"{fact.get('subject', '')} {fact.get('predicate', '')} {fact.get('object', '')}"
        )
        self.setToolTip(title)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]  # PySide6 Qt.PointingHandCursor enum (incomplete stubs)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self._signal.emit(self._fact)  # type: ignore[attr-defined]  # PySide6 Signal.emit (incomplete stubs)
        super().mousePressEvent(event)
