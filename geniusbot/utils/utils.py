#!/usr/bin/env python3
import importlib.metadata
import logging
import os

# Resolve centralized log directory
try:
    from agent_utilities.core.paths import log_dir

    geniusbot_log_dir = log_dir()
except ImportError:
    from pathlib import Path

    import platformdirs

    geniusbot_log_dir = Path(
        platformdirs.user_log_path("agent-utilities", "knuckles-team")
    )

geniusbot_log_dir.mkdir(parents=True, exist_ok=True)
geniusbot_log_path = geniusbot_log_dir / "geniusbot.log"

logger = logging.getLogger("geniusbot")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.FileHandler(geniusbot_log_path)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


def check_package(package: str = "None") -> bool:
    found = False
    try:
        version = importlib.metadata.version(package)
        logger.info(f"{package} ({version}) is installed")
        found = True
    except importlib.metadata.PackageNotFoundError:
        logger.info(f"{package} is NOT installed")
    return found


def resource_path(relative_path: str = "None") -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = ""
    try:
        if "_MEIPASS" in os.environ:
            base_path = os.environ["_MEIPASS"]
        if "_MEIPASS2" in os.environ:
            base_path = os.environ["_MEIPASS2"]
    except Exception:
        base_path = os.path.dirname(os.path.dirname(__file__))
    if not os.path.exists(base_path) or base_path == "":
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)
