"""Repository hygiene: does the repository deliver what its README and docs promise?"""
import re

import pytest
import yaml


def _readme(repo):
    return (repo / "README.md").read_text(encoding="utf-8")


def test_readme_documents_install_and_test_commands(repo):
    text = _readme(repo)
    assert "pip install -e ." in text and "pytest" in text


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-019: README references .github/workflows/ci.yml, which does not exist")
def test_ci_workflow_mentioned_in_readme_exists(repo):
    m = re.search(r"`(\.github/workflows/[\w.-]+)`", _readme(repo))
    assert m, "README no longer mentions a CI workflow"
    assert (repo / m.group(1)).is_file()


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-020: README 'Key Code Locations' point at paths that do not exist")
def test_readme_code_locations_exist(repo):
    section = _readme(repo).split("### Key Code Locations", 1)[1].split("###", 1)[0]
    paths = re.findall(r"`([\w./-]+/)`", section)
    assert paths
    missing = [p for p in paths if not (repo / p).exists()]
    assert not missing, f"documented paths that do not exist: {missing}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-020: README web-backend command points at src/osdagbridge/web/..., which does not exist")
def test_readme_runserver_path_exists(repo):
    m = re.search(r"python (\S*manage\.py) runserver", _readme(repo))
    assert m
    assert (repo / m.group(1)).is_file()


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-021: all docs/*.md files are one-line placeholders")
@pytest.mark.parametrize("name", ["architecture.md", "developer_guide.md", "user_guide.md"])
def test_docs_are_not_placeholders(repo, name):
    text = (repo / "docs" / name).read_text(encoding="utf-8")
    assert "placeholder" not in text.lower() and len(text.split()) > 30


def test_example_input_is_valid_yaml(repo):
    data = yaml.safe_load((repo / "examples/plate_girder/example_basic.yaml").read_text())
    assert data["project"]["span_m"] == 30.0


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-022: verification_case_*.yaml contain only a comment (parse to None)")
@pytest.mark.parametrize("name", ["verification_case_01.yaml", "verification_case_02.yaml"])
def test_verification_cases_contain_data(repo, name):
    data = yaml.safe_load((repo / "examples/plate_girder" / name).read_text())
    assert isinstance(data, dict) and data


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-023: the upstream test-suite is made of `assert True` placeholders and tests nothing")
def test_upstream_tests_contain_real_assertions(repo):
    offenders = []
    for path in (repo / "tests").rglob("*.py"):
        body = path.read_text(encoding="utf-8")
        if re.search(r"assert True\b", body):
            offenders.append(path.relative_to(repo).as_posix())
    assert not offenders, f"{len(offenders)} placeholder test files: {sorted(offenders)}"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-024: tests/integration/verification_ddcl_cases.py is never collected (name does not match test_*.py)")
def test_every_upstream_test_file_is_collectable(repo):
    bad = [p.name for p in (repo / "tests").rglob("*.py")
           if p.name != "__init__.py" and not (p.name.startswith("test_") or p.name.endswith("_test.py"))]
    assert not bad, f"files pytest will silently skip: {bad}"


def test_upstream_tests_count_is_known(repo):
    """Records the baseline: 7 upstream test files exist (all placeholders today)."""
    files = [p for p in (repo / "tests").rglob("*.py")]
    assert len(files) == 7
