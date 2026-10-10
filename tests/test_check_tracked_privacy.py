from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "check_tracked_privacy.py"


def _load_gate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_tracked_privacy", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# Shared-fix regression: ``_MACHINE_HOST_ID_RE``'s lookbehind did not exclude
# ``-``, so a hyphen-joined requirement ID (``AU-BOUNDARY-R016``) false-
# positived as a machine host alias. Fixed by widening the lookbehind to
# ``(?<![a-z0-9-])`` -- the same one-character fix as pipelines PR #41
# (pipelines_hooks/privacy/patterns.py) and epistemic-graph's local copy
# (D-EG-PRIVACY-R001-FALSEPOS).
def test_hyphenated_requirement_id_is_not_flagged_as_host_id() -> None:
    gate = _load_gate()
    categories = gate.classify_line(
        "see AU-BOUNDARY-R016 for the full requirement text",
        identifiers=frozenset(),
        deployment_doc=False,
    )
    assert "machine-specific host identifier" not in categories


def test_bare_host_token_is_still_flagged_as_host_id() -> None:
    gate = _load_gate()
    categories = gate.classify_line(
        "reported from " + "host" + "123",
        identifiers=frozenset(),
        deployment_doc=False,
    )
    assert "machine-specific host identifier" in categories
