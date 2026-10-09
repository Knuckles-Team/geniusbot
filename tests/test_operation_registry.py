"""Tests for the typed operation-registry model (GENIUSBOT-CLIENT-R002.1)."""

import pytest

from geniusbot.services.operation_registry import (
    OperationRegistryEntry,
    OperationRegistryError,
    build_registry,
)

VALID_DIGEST = "a" * 64


@pytest.mark.spec("GENIUSBOT-CLIENT-R002.1", "GENIUSBOT-CLIENT-R012.1")
def test_valid_entry_accepted():
    entry = OperationRegistryEntry(
        operation="graph.query", digest=VALID_DIGEST, method="POST"
    )
    assert entry.operation == "graph.query"


@pytest.mark.spec("GENIUSBOT-CLIENT-R002.1", "GENIUSBOT-CLIENT-R012.1")
def test_rejects_empty_operation():
    with pytest.raises(OperationRegistryError):
        OperationRegistryEntry(operation="", digest=VALID_DIGEST)


@pytest.mark.spec("GENIUSBOT-CLIENT-R002.1", "GENIUSBOT-CLIENT-R012.1")
def test_rejects_malformed_digest():
    with pytest.raises(OperationRegistryError):
        OperationRegistryEntry(operation="graph.query", digest="not-a-digest")


def test_rejects_unsupported_method():
    with pytest.raises(OperationRegistryError):
        OperationRegistryEntry(
            operation="graph.query", digest=VALID_DIGEST, method="TRACE"
        )


def test_build_registry_rejects_missing_field():
    with pytest.raises(OperationRegistryError):
        build_registry([{"operation": "graph.query"}])


def test_build_registry_rejects_duplicate():
    raw = [
        {"operation": "graph.query", "digest": VALID_DIGEST},
        {"operation": "graph.query", "digest": VALID_DIGEST},
    ]
    with pytest.raises(OperationRegistryError):
        build_registry(raw)


def test_build_registry_accepts_valid_entries_and_lookup():
    raw = [{"operation": "graph.query", "digest": VALID_DIGEST, "method": "GET"}]
    registry = build_registry(raw)
    assert registry.lookup("graph.query").method == "GET"


def test_registry_lookup_rejects_unknown_operation():
    registry = build_registry([{"operation": "graph.query", "digest": VALID_DIGEST}])
    with pytest.raises(OperationRegistryError):
        registry.lookup("graph.unknown")


def test_registry_validate_digest_rejects_mismatch():
    registry = build_registry([{"operation": "graph.query", "digest": VALID_DIGEST}])
    with pytest.raises(OperationRegistryError):
        registry.validate_digest("graph.query", "b" * 64)
