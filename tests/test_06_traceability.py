"""Keeps the test-suite and issues/issues.yaml in sync (no orphan IDs in either direction)."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r"ISSUE-\d{3}")


def _registered():
    data = yaml.safe_load((ROOT / "issues" / "issues.yaml").read_text(encoding="utf-8"))
    return {i["id"]: i for i in data["issues"]}


def _referenced():
    found = set()
    for path in (ROOT / "tests").glob("test_0[1-5]_*.py"):
        found |= set(ID.findall(path.read_text(encoding="utf-8")))
    return found


def test_every_issue_referenced_by_a_test_is_registered():
    assert _referenced() - set(_registered()) == set()


def test_every_registered_issue_has_at_least_one_test():
    assert set(_registered()) - _referenced() == set()


def test_issue_records_are_complete_and_ids_are_sequential():
    issues = _registered()
    assert list(issues) == [f"ISSUE-{n:03d}" for n in range(1, len(issues) + 1)]
    required = {"title", "severity", "component", "steps", "expected", "actual", "tests", "fix"}
    for iid, rec in issues.items():
        assert required <= set(rec), f"{iid} missing {required - set(rec)}"
        assert rec["severity"] in {"Critical", "High", "Medium", "Low"}, iid
