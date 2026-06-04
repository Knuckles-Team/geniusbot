"""Enforce the backend-adapter seam invariant.

Only ``geniusbot/services/backend_adapter.py`` may import from
``agent_utilities``. Every other module must route backend access through the
adapter facade. This test scans the source tree to guarantee the coupling
stays a single swappable seam.
"""

import re
from pathlib import Path

# Repo layout: <repo>/tests/this_file.py  and  <repo>/geniusbot/<package>
PACKAGE_ROOT = Path(__file__).resolve().parent.parent / "geniusbot"

# Files allowed to import agent_utilities directly (the seam itself).
ALLOWED = {"services/backend_adapter.py"}

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


def test_only_adapter_imports_agent_utilities():
    offenders = _offending_files()
    assert not offenders, (
        "These modules import agent_utilities directly and must route through "
        f"geniusbot.services.backend_adapter instead: {offenders}"
    )


def test_adapter_actually_imports_agent_utilities():
    """Sanity check that the seam file genuinely owns the coupling."""
    adapter = PACKAGE_ROOT / "services" / "backend_adapter.py"
    assert adapter.exists()
    assert _IMPORT_RE.search(adapter.read_text(encoding="utf-8"))


def test_backend_singleton_surface():
    """The adapter exposes the method surface the UI relies on."""
    from geniusbot.services.backend_adapter import backend

    for method in (
        "resolve_log_dir",
        "run_graph_query",
        "run_workspace_graph",
        "load_service_layout",
        "fetch_service_widget_data",
    ):
        assert callable(getattr(backend, method)), method
