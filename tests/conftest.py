"""Shared fixtures.

The repository under test is located through the OSDAGBRIDGE_REPO environment variable
(default: a sibling directory called OsdagBridge). Nothing in the target repo is modified:
the `patched_src` fixture works on a temporary copy of its source tree.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent


def _find_repo() -> Path | None:
    env = os.environ.get("OSDAGBRIDGE_REPO")
    candidates = [Path(env)] if env else [PROJECT_ROOT.parent / "OsdagBridge", PROJECT_ROOT / "OsdagBridge"]
    for cand in candidates:
        if (cand / "src" / "osdagbridge").is_dir():
            return cand.resolve()
    return None


def _git_head(repo: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def pytest_report_header(config):
    repo = _find_repo()
    if repo is None:
        return "osdagbridge repo: NOT FOUND (set OSDAGBRIDGE_REPO)"
    return f"osdagbridge repo: {repo} @ {_git_head(repo)}"


@pytest.fixture(scope="session")
def repo() -> Path:
    found = _find_repo()
    if found is None:
        pytest.skip("OsdagBridge repository not found; set OSDAGBRIDGE_REPO")
    return found


@pytest.fixture(scope="session")
def src(repo) -> Path:
    """Unmodified source tree - what a user gets after `pip install`."""
    return repo / "src"


@pytest.fixture(scope="session")
def patched_src(src, tmp_path_factory) -> Path:
    """Copy of the source tree with ONLY the ISSUE-001 blocker worked around.

    `osdagbridge/core/__init__.py` imports a non-existent `models` module, which makes every
    `osdagbridge.core.*` module unimportable. To keep testing the rest of the core we add an
    empty `core/models.py` to a temporary copy. This is a test-environment workaround, not a fix.
    """
    dest = tmp_path_factory.mktemp("patched") / "src"
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    models = dest / "osdagbridge" / "core" / "models.py"
    if not models.exists():
        models.write_text('"""Shim added by the test-suite to isolate ISSUE-001."""\n')
    return dest


@pytest.fixture()
def work(tmp_path) -> Path:
    """Neutral working directory for subprocesses."""
    return tmp_path
