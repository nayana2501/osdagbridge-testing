"""Importability of the package and of every module in it."""
import pytest

from _helpers import module_names, probe, try_import

ISSUE_001 = "ISSUE-001: osdagbridge/core/__init__.py does `from .models import *` but models.py does not exist"


def test_top_level_package_imports(src, work):
    ok, err = try_import("osdagbridge", src, work)
    assert ok, err


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=ISSUE_001)
def test_core_package_imports(src, work):
    ok, err = try_import("osdagbridge.core", src, work)
    assert ok, err


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=ISSUE_001)
def test_every_module_is_importable(src, work):
    names = module_names(src)
    body = (
        "import importlib\n"
        f"names = {names!r}\n"
        "failed = {}\n"
        "for n in names:\n"
        "    try:\n"
        "        importlib.import_module(n)\n"
        "    except Exception as exc:\n"
        "        failed[n] = type(exc).__name__\n"
        "result = failed\n"
    )
    failed = probe(body, src, work)
    assert not failed, f"{len(failed)}/{len(names)} modules fail to import, e.g. {sorted(failed)[:3]}"


def test_issue_001_root_cause_is_the_missing_models_module(src, patched_src, work):
    """Documents that ISSUE-001 is a single root cause: with an (empty) models module present,
    all modules import. This test passes today and keeps passing after the real fix."""
    init = (src / "osdagbridge" / "core" / "__init__.py").read_text()
    models_exists = (src / "osdagbridge" / "core" / "models.py").exists() or \
                    (src / "osdagbridge" / "core" / "models").is_dir()
    if models_exists:
        pytest.skip("models module now exists upstream - ISSUE-001 appears fixed")
    assert "from .models import" in init

    names = module_names(patched_src)
    body = (
        "import importlib\n"
        f"names = {names!r}\n"
        "failed = []\n"
        "for n in names:\n"
        "    try:\n"
        "        importlib.import_module(n)\n"
        "    except Exception as exc:\n"
        "        failed.append((n, type(exc).__name__))\n"
        "result = failed\n"
    )
    assert probe(body, patched_src, work) == []
