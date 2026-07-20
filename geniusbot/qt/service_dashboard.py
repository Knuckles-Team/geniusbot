#!/usr/bin/env python3
"""Service Dashboard Panel — Homepage-style service management for GeniusBot.

Displays all configured Agent-OS services as interactive cards with
real-time status, key metrics, and clickable links. Uses the
agent_utilities.gateway backend for configuration and data fetching.

Concept: AU-019 (GUI Dashboard Panel)
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from geniusbot.qt.colors import (
    ACCENT_PRIMARY,
    ACCENT_SUCCESS,
    BG_PRIMARY,
    BG_SECONDARY,
    BORDER_COLOR,
    TEXT_MAIN,
    TEXT_MUTED,
)

logger = logging.getLogger(__name__)

# ── Status Colors ───────────────────────────────────────────────────

_STATUS_COLORS = {
    "ok": "#00E676",
    "warning": "#FFD600",
    "error": "#FF5252",
    "unknown": "#8A8A93",
}

_STATUS_ICONS = {
    "ok": "●",
    "warning": "●",
    "error": "●",
    "unknown": "○",
}


# ── Background Worker Thread ────────────────────────────────────────


class _FetchWorker(QThread):
    """Background thread that fetches all widget data."""

    data_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._aggregator = None

    def run(self):
        try:
            from geniusbot.services.backend_adapter import backend

            result = backend.fetch_service_widget_data()
            self.data_ready.emit(result)
        except ImportError:
            self.error.emit("agent-utilities gateway module not available.")
        except Exception as e:
            self.error.emit(type(e).__name__)


# ── ServiceCard QFrame ──────────────────────────────────────────────


class ServiceCard(QFrame):
    """A single glassmorphic service card widget."""

    def __init__(
        self,
        service_id: str,
        display_name: str,
        url: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.service_id = service_id
        self.display_name = display_name
        self.url = url

        self.setObjectName("ServiceCard")
        self.setStyleSheet(
            f"""
            QFrame#ServiceCard {{
                background-color: {BG_SECONDARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                padding: 14px;
            }}
            QFrame#ServiceCard:hover {{
                border: 1px solid {ACCENT_PRIMARY};
            }}
        """
        )
        self.setMinimumWidth(220)
        self.setMinimumHeight(120)
        self.setMaximumWidth(350)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Top row: status + name
        top_row = QHBoxLayout()
        self.status_label = QLabel("○")
        self.status_label.setStyleSheet(
            f"font-size: 14px; color: {_STATUS_COLORS['unknown']};"
        )
        top_row.addWidget(self.status_label)

        self.name_label = QLabel(display_name)
        self.name_label.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {TEXT_MAIN};"
        )
        top_row.addWidget(self.name_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        # URL line
        if url:
            url_label = QLabel(url)
            url_label.setStyleSheet(
                f"font-size: 10px; color: {TEXT_MUTED}; font-style: italic;"
            )
            layout.addWidget(url_label)

        # Fields area
        self.fields_container = QVBoxLayout()
        self.fields_container.setSpacing(2)
        layout.addLayout(self.fields_container)

        # Error label (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("font-size: 11px; color: #FF5252;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        layout.addStretch()

    def update_data(
        self,
        status: str,
        fields: list[dict[str, str]],
        error: str | None = None,
    ) -> None:
        """Update card with fresh widget data."""
        color = _STATUS_COLORS.get(status, _STATUS_COLORS["unknown"])
        icon = _STATUS_ICONS.get(status, "○")
        self.status_label.setText(icon)
        self.status_label.setStyleSheet(f"font-size: 14px; color: {color};")

        # Clear existing fields
        while self.fields_container.count():
            item = self.fields_container.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        if error:
            self.error_label.setText(f"⚠ {type(error).__name__}")
            self.error_label.show()
            return

        self.error_label.hide()

        # Render fields (max 5)
        for field in fields[:5]:
            field_widget = QLabel(
                f"<span style='color:{TEXT_MUTED};'>{field['label']}:</span> "
                f"<span style='font-weight:bold;color:{TEXT_MAIN};'>{field['value']}</span>"
            )
            field_widget.setStyleSheet("font-size: 11px;")
            self.fields_container.addWidget(field_widget)


# ── Category Group Header ───────────────────────────────────────────


class CategoryHeader(QLabel):
    """Styled category group header."""

    def __init__(self, category_name: str, parent: QWidget | None = None) -> None:
        super().__init__(f"▸ {category_name.upper()}", parent)
        self.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {ACCENT_PRIMARY}; padding: 8px 0 4px 0; margin-top: 12px;"
        )


# ── ServiceDashboardPanel ──────────────────────────────────────────


class ServiceDashboardPanel(QWidget):
    """Homepage-style service dashboard with grouped service cards.

    Integrates with agent_utilities.gateway for:
    - XDG-compliant config discovery (services.yaml / MCP auto-detect)
    - Aggregator for concurrent widget data fetching
    - Unified data models (WidgetData, ServiceConfig, DashboardLayout)
    """

    def __init__(self, worker: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.worker = worker
        self._cards: dict[str, ServiceCard] = {}
        self._fetch_worker: _FetchWorker | None = None
        self._refresh_timer: QTimer | None = None

        self._init_ui()
        self._populate_dashboard()
        self._start_auto_refresh()

    def _init_ui(self) -> None:
        """Build the panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header bar
        header_layout = QHBoxLayout()

        title = QLabel("🏠 Agent-OS Service Dashboard")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {ACCENT_PRIMARY};"
        )
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        header_layout.addWidget(self.stats_label)

        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.clicked.connect(self._refresh_data)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Scrollable card grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_container = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_container)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

    def _populate_dashboard(self) -> None:
        """Load layout via the backend seam and create cards."""
        try:
            from geniusbot.services.backend_adapter import backend

            layout = backend.load_service_layout()
        except ImportError:
            empty = QLabel(
                "⚠ agent-utilities gateway not available.\nInstall agent-utilities with: pip install agent-utilities"
            )
            empty.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 14px; font-style: italic; padding: 40px;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty)
            return
        except Exception as e:
            logger.error(
                "Failed to load dashboard config: error_type=%s", type(e).__name__
            )
            error_label = QLabel("⚠ Failed to load config")
            error_label.setStyleSheet("color: #FF5252; font-size: 14px;")
            self.grid_layout.addWidget(error_label)
            return

        if not layout.groups:
            empty = QLabel(
                "No services configured.\nAdd services to $XDG_CONFIG_HOME/agent-os/services.yaml"
            )
            empty.setStyleSheet(
                f"color: {TEXT_MUTED}; font-size: 14px; font-style: italic; padding: 40px;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty)
            return

        for group in layout.groups:
            # Category header
            self.grid_layout.addWidget(CategoryHeader(group.name))

            # Card grid (3 columns)
            grid = QGridLayout()
            grid.setSpacing(12)

            col = 0
            row = 0
            for svc in group.services:
                if not svc.visible:
                    continue
                card = ServiceCard(
                    service_id=svc.id,
                    display_name=svc.name,
                    url=svc.url or "",
                )
                self._cards[svc.id] = card
                grid.addWidget(card, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

            # Add grid to the layout
            grid_widget = QWidget()
            grid_widget.setLayout(grid)
            self.grid_layout.addWidget(grid_widget)

        self.grid_layout.addStretch()

        # Update stats
        total = len(self._cards)
        self.stats_label.setText(f"{total} services  |  Loading data...")

        # Initial data fetch
        self._refresh_data()

    def _refresh_data(self) -> None:
        """Kick off a background data fetch."""
        if self._fetch_worker and self._fetch_worker.isRunning():
            return

        self._fetch_worker = _FetchWorker(self)
        self._fetch_worker.data_ready.connect(self._on_data_ready)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.start()

    def _on_data_ready(self, data: dict) -> None:
        """Update cards with fetched data."""
        ok_count = 0
        err_count = 0

        for svc_id, widget_data in data.items():
            card = self._cards.get(svc_id)
            if not card:
                continue

            card.update_data(
                status=widget_data["status"],
                fields=widget_data.get("fields", []),
                error=widget_data.get("error"),
            )

            if widget_data["status"] == "ok":
                ok_count += 1
            elif widget_data["status"] == "error":
                err_count += 1

        total = len(self._cards)
        self.stats_label.setText(
            f"{total} services  |  {ok_count} healthy  |  {err_count} errors"
        )

    def _on_fetch_error(self, error_msg: str) -> None:
        """Handle fetch error."""
        logger.error("Dashboard fetch failed")
        self.stats_label.setText("⚠ Fetch error")

    def _start_auto_refresh(self) -> None:
        """Start periodic auto-refresh (every 30 seconds)."""
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_data)
        self._refresh_timer.start(30_000)

    def cleanup(self) -> None:
        """Stop timers and threads on cleanup."""
        if self._refresh_timer:
            self._refresh_timer.stop()
        if self._fetch_worker and self._fetch_worker.isRunning():
            self._fetch_worker.terminate()
