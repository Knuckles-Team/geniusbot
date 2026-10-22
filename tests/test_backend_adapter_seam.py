"""Enforce the backend-adapter seam invariant.

GeniusBot is a client of Arbora: no module under ``geniusbot/`` may import
``agent_utilities``, and the adapter facade exposes the method surface the UI
relies on.
"""

import re
from pathlib import Path

import pytest

# Repo layout: <repo>/tests/this_file.py  and  <repo>/geniusbot/<package>
PACKAGE_ROOT = Path(__file__).resolve().parent.parent / "geniusbot"

ALLOWED: set[str] = set()

_IMPORT_RE = re.compile(r"^\s*(from agent_utilities|import agent_utilities)", re.M)


def _offending_files():
    offenders = []
    for path in PACKAGE_ROOT.rglob("*.py"):
        rel = path.relative_to(PACKAGE_ROOT).as_posix()
        if rel in ALLOWED:
            continue
        text = path.read_text(encoding="utf-8")
        if _IMPORT_RE.search(text):
            offenders.append(rel)
    return offenders


@pytest.mark.spec("GENIUSBOT-CLIENT-R001.1")
def test_no_module_imports_agent_utilities():
    offenders = _offending_files()
    assert not offenders, (
        "These modules import agent_utilities; geniusbot is an arbora client: "
        f"{offenders}"
    )


def test_backend_singleton_surface():
    """The adapter exposes the method surface the UI relies on."""
    from geniusbot.services.backend_adapter import backend

    for method in (
        "resolve_log_dir",
        "run_graph_query",
        "run_agent_workflow",
        "load_service_layout",
        "fetch_service_widget_data",
    ):
        assert callable(getattr(backend, method)), method


def test_agent_workflow_runs_on_arbora_not_in_process():
    import asyncio

    from geniusbot.services.backend_adapter import BackendAdapter

    class _Gateway:
        async def stream_copilot_query(self, query, progress_cb=None):
            return {"result": f"done: {query}"}

    adapter = BackendAdapter()
    adapter._gateway_client = _Gateway()
    result = asyncio.run(adapter.run_agent_workflow("go"))
    assert result == {"result": "done: go"}

    class _Offline(_Gateway):
        async def stream_copilot_query(self, query, progress_cb=None):
            return {"result": "❌ Gateway is offline."}

    adapter._gateway_client = _Offline()
    try:
        asyncio.run(adapter.run_agent_workflow("go"))
    except RuntimeError:
        pass
    else:
        raise AssertionError("an offline gateway must raise for the caller fallback")
