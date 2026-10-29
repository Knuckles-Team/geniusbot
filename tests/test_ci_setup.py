"""Exercise the declared CI setup without installing system packages in tests."""

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.spec("AXIL-CLIENT-R016.3")


def test_ci_setup_installs_locked_tests_and_headless_qt(tmp_path):
    workflow = yaml.safe_load(
        (Path(__file__).parents[1] / ".github/workflows/ci.yml").read_text()
    )
    settings = workflow["jobs"]["gates"]["with"]
    assert settings["test-scope"] == "tests"
    assert settings["all-files"] is True
    log = tmp_path / "commands.jsonl"
    env_file = tmp_path / "environment"
    for name in ("sudo", "uv"):
        executable = tmp_path / name
        executable.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "with open(os.environ['COMMAND_LOG'], 'a') as output:\n"
            "    output.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        )
        executable.chmod(0o755)
    subprocess.run(
        ["bash", "-c", settings["setup-command"]],
        check=True,
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "COMMAND_LOG": str(log),
            "GITHUB_ENV": str(env_file),
        },
    )
    commands = [json.loads(line) for line in log.read_text().splitlines()]
    assert commands == [
        ["apt-get", "update", "-q"],
        [
            "apt-get",
            "install",
            "-y",
            "-q",
            "libegl1",
            "libgl1",
            "libxkbcommon0",
            "libfontconfig1",
            "libpulse0",
        ],
        ["sync", "--frozen", "--extra", "test"],
    ]
    assert env_file.read_text().splitlines() == [
        "QT_QPA_PLATFORM=offscreen",
        "QT_AUDIO_BACKEND=pulseaudio",
    ]

    env_file.unlink()
    with (tmp_path / "uv").open("a") as failing_uv:
        failing_uv.write("raise SystemExit(9)\n")
    with pytest.raises(subprocess.CalledProcessError) as failure:
        subprocess.run(
            ["bash", "-c", settings["setup-command"]],
            check=True,
            env={
                **os.environ,
                "PATH": f"{tmp_path}:{os.environ['PATH']}",
                "COMMAND_LOG": str(log),
                "GITHUB_ENV": str(env_file),
            },
        )
    assert failure.value.returncode == 9
    assert not env_file.exists()
