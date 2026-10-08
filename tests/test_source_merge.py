"""Fail-closed behavior of the bounded source merge gate."""

from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_source_merge.py"


def _gate(monkeypatch, changed: str, *, remote: str = "base"):
    gate = runpy.run_path(str(_SCRIPT))["main"]
    values = {
        ("rev-parse", "origin/main"): "base",
        ("diff", "--name-only", "base"): changed,
        ("ls-remote", "origin", "refs/heads/main"): remote + "\trefs/heads/main",
        ("rev-parse", "--path-format=absolute", "--git-common-dir"): "/missing/.git",
    }
    monkeypatch.setitem(gate.__globals__, "git", lambda *args: values[args])
    return gate


@pytest.mark.parametrize("changed", ["pyproject.toml", "geniusbot/qt/tool_guard.py"])
def test_changes_outside_gateway_scope_require_full_pytest(monkeypatch, changed):
    gate = _gate(monkeypatch, changed)
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    monkeypatch.setattr(subprocess, "call", lambda command: calls.append(command) or 7)

    assert gate() == 7
    assert calls[0][-4:] == ["pytest", "--hook-stage", "manual", "--all-files"]


def test_dirty_candidate_is_rejected_before_test_selection(monkeypatch):
    gate = _gate(monkeypatch, "geniusbot/services/gateway_client.py")

    def reject(command, **kwargs):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(subprocess, "run", reject)
    with pytest.raises(subprocess.CalledProcessError):
        gate()


def test_changed_remote_main_fails_closed(monkeypatch):
    gate = _gate(monkeypatch, "geniusbot/services/gateway_client.py", remote="new-main")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="Remote main changed"):
        gate()


def test_missing_qualified_environment_fails_closed(monkeypatch):
    gate = _gate(monkeypatch, "geniusbot/services/gateway_client.py")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="environment is unavailable"):
        gate()
