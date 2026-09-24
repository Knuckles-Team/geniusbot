"""Tests for the geniusbot temporal graph scrubber panel (CONCEPT:GB-GBOT.cockpit.gbot-7).

Qt runs offscreen (conftest). The pure query/expiry math is tested without a
display; the panel is exercised by feeding it fact rows directly and checking
that expired edges are flagged for the greyed/dashed renderer.
"""

from __future__ import annotations

from datetime import UTC, datetime, timezone
from unittest.mock import MagicMock

import pytest

from geniusbot.qt.temporal_graph_panel import (
    BASE_UQL,
    TemporalGraphPanel,
    mark_expired,
    slider_to_iso,
    temporal_uql,
)


def test_base_query_is_uql_not_cypher() -> None:
    assert BASE_UQL == "MATCH () |> LIMIT 200"


def test_as_of_is_a_stage_in_unix_seconds_before_the_cap() -> None:
    assert (
        temporal_uql("2026-06-01T00:00:00+00:00")
        == "MATCH () |> AS OF @1780272000 |> LIMIT 200"
    )
    assert temporal_uql("2026-06-01T02:00:00+02:00") == temporal_uql(
        "2026-06-01T00:00:00"
    )


def test_a_non_iso_timestamp_is_refused() -> None:
    with pytest.raises(ValueError):
        temporal_uql("yesterday")


def test_slider_to_iso_endpoints() -> None:
    now = datetime(2026, 6, 30, 0, 0, 0, tzinfo=UTC)
    # Position 100 == now; position 0 == 30 days earlier.
    assert slider_to_iso(100, now=now) == now.isoformat()
    assert (
        slider_to_iso(0, now=now)
        == datetime(2026, 5, 31, 0, 0, 0, tzinfo=UTC).isoformat()
    )


def test_mark_expired_flags_old_edges() -> None:
    facts = [
        {"subject": "a", "predicate": "r", "object": "b"},  # no valid_until -> live
        {
            "subject": "a",
            "predicate": "r",
            "object": "c",
            "valid_until": "2026-01-01T00:00:00+00:00",  # before ts -> expired
        },
    ]
    out = mark_expired(facts, "2026-06-01T00:00:00+00:00")
    assert out[0]["expired"] is False
    assert out[1]["expired"] is True
    # original dicts not mutated
    assert "expired" not in facts[0]


def test_panel_renders_and_flags_expired(qapp) -> None:
    panel = TemporalGraphPanel(MagicMock())
    iso_ts = "2026-06-01T00:00:00+00:00"
    panel.render_facts(
        [
            {"subject": "a", "predicate": "links", "object": "b"},
            {
                "subject": "a",
                "predicate": "old",
                "object": "c",
                "valid_until": "2026-01-01T00:00:00+00:00",
            },
        ],
        iso_ts,
    )
    # Both facts rendered as edges; one carries the expired flag.
    assert panel.graph.fact_count() == 2
    expired_flags = [f.get("expired") for f in panel.graph._facts]
    assert expired_flags.count(True) == 1


def test_panel_current_query_carries_as_of(qapp) -> None:
    panel = TemporalGraphPanel(MagicMock())
    query = panel.current_query()
    assert query.startswith("MATCH () |> AS OF @")
    assert query.endswith("|> LIMIT 200")


def test_rows_to_facts_handles_triples_and_dicts() -> None:
    rows = [
        ["a", "rel", "b"],
        {"subject": "x", "predicate": "p", "object": "y"},
        ["too", "short"],  # ignored
    ]
    facts = TemporalGraphPanel._rows_to_facts(rows)
    assert len(facts) == 2
    assert facts[0] == {"subject": "a", "predicate": "rel", "object": "b"}
    assert facts[1]["subject"] == "x"
