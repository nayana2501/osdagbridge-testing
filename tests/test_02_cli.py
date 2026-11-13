"""Command-line interface and entry points, as documented in the README."""
import pytest

from _helpers import load_toml, run_module


def _cli(args, src, work):
    return run_module("osdagbridge.cli", args, src, work)


def test_cli_module_runs_and_exits_cleanly(src, work):
    proc = _cli([], src, work)
    assert proc.returncode == 0
    assert proc.stdout.strip() != ""


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-004: CLI is a stub; no argument parsing or sub-commands")
def test_cli_help_lists_documented_commands(src, work):
    out = _cli(["--help"], src, work).stdout.lower()
    assert "analyze" in out and "report" in out


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-004: `analyze` ignores its arguments")
def test_cli_analyze_acknowledges_the_project_file(src, work):
    proc = _cli(["analyze", "my_project.yaml", "--solver", "native"], src, work)
    assert "my_project.yaml" in proc.stdout + proc.stderr


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-004: nonexistent input file still exits with status 0")
def test_cli_analyze_missing_file_fails(src, work):
    proc = _cli(["analyze", "does_not_exist.yaml"], src, work)
    assert proc.returncode != 0


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-004: unknown sub-commands are not rejected")
def test_cli_unknown_command_is_rejected(src, work):
    proc = _cli(["frobnicate"], src, work)
    assert proc.returncode != 0


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-003: no [project.scripts] entry, so `osdagbridge ...` from the README cannot work")
def test_console_script_is_declared(repo):
    scripts = load_toml(repo / "pyproject.toml").get("project", {}).get("scripts", {})
    assert "osdagbridge" in scripts


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-005: osdagbridge.desktop has no __main__.py")
def test_desktop_package_is_runnable_with_dash_m(src, work):
    proc = run_module("osdagbridge.desktop", [], src, work)
    assert proc.returncode == 0, proc.stderr.strip().splitlines()[-1:]


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-005: README says the desktop GUI is PySide6 but no extra declares it")
def test_pyside6_is_declared_as_a_dependency(repo):
    extras = load_toml(repo / "pyproject.toml")["project"].get("optional-dependencies", {})
    deps = [d.lower() for group in extras.values() for d in group]
    assert any(d.startswith("pyside6") for d in deps)
