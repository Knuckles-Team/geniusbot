"""The desktop dashboard consumes the Graph OS owner of service widgets."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

_ADAPTER = Path(__file__).resolve().parents[1] / "geniusbot/services/backend_adapter.py"
_SPEC = importlib.util.spec_from_file_location("geniusbot_dashboard_adapter_test", _ADAPTER)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
BackendAdapter = _MODULE.BackendAdapter


@pytest.fixture
def graph_os_dashboard(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []
    graph_os = types.ModuleType("graph_os")
    graph_os.__path__ = []
    gateway = types.ModuleType("graph_os.gateway")
    gateway.__path__ = []
    config = types.ModuleType("graph_os.gateway.config")
    aggregator = types.ModuleType("graph_os.gateway.aggregator")

    class ConfigManager:
        def load(self) -> SimpleNamespace:
            calls.append("layout")
            return SimpleNamespace(groups=[SimpleNamespace(name="Infra")])

    class Aggregator:
        async def fetch_all(self) -> dict[str, SimpleNamespace]:
            calls.append("widgets")
            return {
                "service-a": SimpleNamespace(
                    status="ok",
                    fields=[SimpleNamespace(label="Latency", value=12)],
                    error=None,
                )
            }

    config.ConfigManager = ConfigManager
    aggregator.Aggregator = Aggregator
    for name, module in (
        ("graph_os", graph_os),
        ("graph_os.gateway", gateway),
        ("graph_os.gateway.config", config),
        ("graph_os.gateway.aggregator", aggregator),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    return calls


def test_dashboard_layout_uses_graph_os(graph_os_dashboard: list[str]) -> None:
    layout = BackendAdapter().load_service_layout()
    assert [group.name for group in layout.groups] == ["Infra"]
    assert graph_os_dashboard == ["layout"]


def test_log_directory_uses_existing_xdg_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import platformdirs

    seen: list[tuple[str, str]] = []

    def log_path(app: str, author: str) -> str:
        seen.append((app, author))
        return "/tmp/geniusbot-log-test"

    monkeypatch.setattr(platformdirs, "user_log_path", log_path)
    assert BackendAdapter.resolve_log_dir() == Path("/tmp/geniusbot-log-test")
    assert seen == [("agent-utilities", "knuckles-team")]


def test_log_directory_preserves_configured_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_UTILITIES_LOG_DIR", "/var/tmp/geniusbot-custom-log")
    assert BackendAdapter.resolve_log_dir() == Path("/var/tmp/geniusbot-custom-log")


def test_dashboard_widget_data_uses_graph_os(graph_os_dashboard: list[str]) -> None:
    data = BackendAdapter().fetch_service_widget_data()
    assert data == {
        "service-a": {
            "status": "ok",
            "fields": [{"label": "Latency", "value": "12"}],
            "error": None,
        }
    }
    assert graph_os_dashboard == ["widgets"]
