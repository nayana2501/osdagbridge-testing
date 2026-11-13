"""Packaging and metadata consistency."""
import re
import zipfile
import subprocess
import sys
from pathlib import Path

import pytest

from _helpers import load_toml, probe


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-002: pyproject declares license file 'LICENSE' but repo has LICENSE.txt")
def test_pyproject_license_file_exists(repo):
    spec = load_toml(repo / "pyproject.toml")["project"]["license"]
    fname = spec["file"] if isinstance(spec, dict) else None
    if fname is None:
        pytest.skip("license is not declared via a file")
    assert (repo / fname).is_file(), f"{fname} is declared but missing; repo has: {[p.name for p in repo.glob('LICENSE*')]}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-015: __version__ (0.0.0) disagrees with pyproject.toml (0.1.0)")
def test_version_is_single_sourced(repo, src, work):
    pyproject = load_toml(repo / "pyproject.toml")["project"]["version"]
    pkg = probe("import osdagbridge; result = osdagbridge.__version__", src, work)
    assert pkg == pyproject, f"__version__={pkg!r} but pyproject.toml says {pyproject!r}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-015: setup.cfg says 0.0.0, pyproject.toml says 0.1.0")
def test_setup_cfg_version_matches_pyproject(repo):
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(repo / "setup.cfg")
    assert cfg["metadata"]["version"] == load_toml(repo / "pyproject.toml")["project"]["version"]


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-016: requires-python >=3.9 but classifiers start at 3.10")
def test_requires_python_matches_classifiers(repo):
    proj = load_toml(repo / "pyproject.toml")["project"]
    minimum = tuple(int(x) for x in re.search(r">=\s*(\d+)\.(\d+)", proj["requires-python"]).groups())
    listed = [tuple(int(x) for x in m.groups())
              for c in proj["classifiers"] if (m := re.search(r"Python :: (\d+)\.(\d+)$", c))]
    assert listed, "no version-specific Python classifiers"
    assert min(listed) <= minimum <= max(listed)
    # Declared support floor (3.9) is lower than the oldest classifier (3.10):
    assert min(listed) == minimum, f"requires-python floor {minimum} but oldest classifier is {min(listed)}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-017: author email domain is 'efossee.in' (typo for fossee.in)")
def test_author_email_domain_looks_valid(repo):
    email = load_toml(repo / "pyproject.toml")["project"]["authors"][0]["email"]
    assert email.endswith("@fossee.in"), f"suspicious domain in author email: {email}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-018: super_structure/ has no __init__.py")
def test_every_package_directory_has_init(src):
    pkg = src / "osdagbridge"
    missing = [str(d.relative_to(src)) for d in sorted(pkg.rglob("*"))
               if d.is_dir() and d.name != "__pycache__" and any(d.glob("*.py")) is False
               and any(p.is_dir() for p in d.iterdir()) and not (d / "__init__.py").exists()]
    assert not missing, f"namespace-only directories (no __init__.py): {missing}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-006: report templates are not declared as package data")
def test_report_templates_are_shipped_in_the_wheel(repo, tmp_path):
    # Isolated build first (downloads setuptools itself, so it works in a bare venv);
    # fall back to the current environment's setuptools when offline.
    last = ""
    for extra in ([], ["--no-build-isolation"]):
        out = tmp_path / ("wheel" + str(len(extra)))
        proc = subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", *extra,
                               "-w", str(out), str(repo)], capture_output=True, text=True, timeout=300)
        wheels = list(out.glob("*.whl"))
        if proc.returncode == 0 and wheels:
            names = zipfile.ZipFile(wheels[0]).namelist()
            assert any(n.endswith("default_template.tex") for n in names)
            return
        last = proc.stderr.strip()[-160:]
    pytest.fail(f"could not build a wheel either with or without build isolation: {last}", pytrace=False)
