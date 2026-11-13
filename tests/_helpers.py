"""Helpers for running OsdagBridge code in an isolated interpreter.

Why subprocesses? The system under test has an import-time defect (ISSUE-001): a single
failing import would otherwise poison the pytest process and hide every later result.
Each probe therefore runs in a fresh `python -I` process with the target source tree
injected through sys.path (the -I flag ignores PYTHONPATH and the current directory, so
nothing but the tree under test is importable).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MARKER = "@@RESULT@@"

_PRELUDE = """\
import sys, json
sys.path.insert(0, {src!r})

def attempt(fn, *args, **kwargs):
    try:
        return {{"ok": fn(*args, **kwargs)}}
    except BaseException as exc:  # noqa: BLE001 - we report whatever was raised
        return {{"raised": type(exc).__name__, "msg": str(exc)[:200],
                "mro": [c.__name__ for c in type(exc).__mro__]}}
"""

_EPILOGUE = "\nprint({marker!r} + json.dumps(result, default=str))\n"


class ProbeError(RuntimeError):
    """The probe interpreter itself failed (not an assertion about the target)."""


def run_python(code: str, src: Path, cwd: Path, timeout: int = 60):
    """Run `code` (after injecting `src` on sys.path); return CompletedProcess."""
    full = _PRELUDE.format(src=str(src)) + code
    return subprocess.run(
        [sys.executable, "-I", "-c", full],
        cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
    )


def probe(body: str, src: Path, cwd: Path):
    """Execute `body`, which must assign a JSON-serialisable value to `result`."""
    proc = run_python(body + _EPILOGUE.format(marker=MARKER), src, cwd)
    if proc.returncode != 0:
        raise ProbeError(proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "probe failed")
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(MARKER):
            return json.loads(line[len(MARKER):])
    raise ProbeError("probe produced no result marker")


def try_import(module: str, src: Path, cwd: Path):
    """Return (ok, last_stderr_line) for `import module` in a clean interpreter."""
    proc = run_python(f"import importlib\nimportlib.import_module({module!r})\n", src, cwd)
    err = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""
    return proc.returncode == 0, err


def run_module(module: str, argv: list[str], src: Path, cwd: Path):
    """Equivalent of `python -m module *argv` against the tree under test."""
    code = (
        "import sys, runpy\n"
        f"sys.argv = [{module!r}] + {argv!r}\n"
        f"runpy.run_module({module!r}, run_name='__main__', alter_sys=True)\n"
    )
    return run_python(code, src, cwd)


def module_names(src: Path) -> list[str]:
    """Dotted names of every .py module below src/osdagbridge."""
    pkg = src / "osdagbridge"
    names = []
    for path in sorted(pkg.rglob("*.py")):
        rel = path.relative_to(src).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        names.append(".".join(parts))
    return names


def load_toml(path: Path) -> dict:
    try:
        import tomllib  # Python >= 3.11
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib
    with open(path, "rb") as fh:
        return tomllib.load(fh)
