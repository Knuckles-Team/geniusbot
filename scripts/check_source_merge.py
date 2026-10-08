"""Mandatory same-main regression checks for the bounded gateway source lane."""

from __future__ import annotations

import io
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

SOURCE_SCOPE = {
    "geniusbot/services/gateway_client.py",
    "tests/test_graph_query_wiring.py",
    "tests/test_source_merge.py",
    "scripts/check_source_merge.py",
    ".pre-commit-config.yaml",
    "AGENTS.md",
}
TESTS = [
    "tests/test_graph_query_wiring.py",
    "tests/security/test_gateway_client_security.py",
]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> int:
    subprocess.run(["git", "diff", "--quiet", "HEAD"], check=True)
    base = git("rev-parse", "origin/main")
    changed = set(git("diff", "--name-only", base).splitlines())
    if not changed <= SOURCE_SCOPE:
        return subprocess.call(
            [
                sys.executable,
                "-m",
                "pre_commit",
                "run",
                "pytest",
                "--hook-stage",
                "manual",
                "--all-files",
            ]
        )
    remote = git("ls-remote", "origin", "refs/heads/main").split()[0]
    if base != remote:
        raise RuntimeError("Remote main changed; fetch and revalidate the candidate")
    subprocess.run(["git", "merge-base", "--is-ancestor", base, "HEAD"], check=True)
    common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir"))
    interpreter = common.parent / ".venv" / "bin" / "python"
    if not interpreter.is_file():
        raise RuntimeError("Qualified existing test environment is unavailable")
    command = [
        str(interpreter),
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-q",
        "--tb=short",
        "--timeout=60",
        *TESTS,
    ]
    print(f"Source baseline: {base}; interpreter: {interpreter}", flush=True)
    archive = subprocess.check_output(["git", "archive", base])
    with tempfile.TemporaryDirectory(prefix="gateway-source-baseline-") as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(directory, filter="data")
        subprocess.run(command, cwd=directory, check=True)
    subprocess.run([*command, "tests/test_source_merge.py"], check=True)
    print(
        "Both baseline and candidate focused tests passed; full release qualification deferred."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
