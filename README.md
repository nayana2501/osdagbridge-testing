# OsdagBridge Test Suite and Issue Register

Screening-task submission for **FOSSEE Winter Internship 2026, Osdag: OsdagBridge Software Testing & Issue Reporting**.

This project tests [osdag-admin/OsdagBridge](https://github.com/osdag-admin/OsdagBridge) (commit `2cb7ddc`, 7 Dec 2025)
from the outside, the way a user or CI would, and records every defect found.

* **63 automated tests** (pytest): 17 pass, 46 are *expected failures* that each document one verified defect.
* **24 issues** (1 Critical, 4 High, 9 Medium, 10 Low), each with steps to reproduce, expected/actual
  behaviour, the test that proves it, and a suggested fix. See [`issues/ISSUES.md`](issues/ISSUES.md).
* A LaTeX report in [`report/`](report/) (`report/report.pdf`).

## Headline findings

| | |
|---|---|
| **ISSUE-001 (Critical)** | `osdagbridge/core/__init__.py` does `from .models import *`, but there is no `models` module. **67 of 74 modules cannot be imported.** |
| **ISSUE-023 (High)** | The upstream test-suite is `assert True` placeholders, so it is green even though the core is unusable. |
| **ISSUE-014 (High)** | `check_local_buckling()` takes no inputs and always returns `True`: a structural check that cannot fail. |
| **ISSUE-004 (High)** | The CLI ignores its arguments and exits `0` for everything, including a missing input file. |

## Run it

```bash
git clone https://github.com/osdag-admin/OsdagBridge.git ../OsdagBridge   # system under test
git -C ../OsdagBridge checkout 2cb7ddc                                      # the audited commit
pip install -r requirements-test.txt
OSDAGBRIDGE_REPO=../OsdagBridge pytest          # 17 passed, 46 xfailed
OSDAGBRIDGE_REPO=../OsdagBridge pytest --runxfail   # shows the 46 raw failures
python tools/render_issues.py                   # regenerate ISSUES.md from issues/issues.yaml
./demo.sh                                       # paced walkthrough, for the screencast
```

The target repository is never modified. `OSDAGBRIDGE_REPO` defaults to `../OsdagBridge`.

## Design

| Decision | Why |
|---|---|
| Each probe runs in a fresh `python -I` subprocess | ISSUE-001 is an import-time failure; in-process it would poison every later test. `-I` also guarantees only the tree under test is importable. |
| Known defects are `xfail(strict=True, raises=AssertionError)` | The suite is green today, but the moment someone fixes a bug the test XPASSes and **fails the build**, forcing the test to be promoted to a normal regression test. `raises=` ensures a test cannot "pass" by crashing for the wrong reason. |
| `patched_src` fixture (copy of the source + empty `core/models.py`) | Lets us test the behaviour of everything *behind* ISSUE-001 without hiding it. The upstream tree is untouched. |
| `issues/issues.yaml` is the single source of truth | `ISSUES.md` and the report tables are generated; `test_06_traceability.py` fails if a test cites an unregistered issue or an issue has no test. |

Verified: simulating upstream fixes in a copy (adding `models.py`, `LICENSE`, correct version) turned exactly
the corresponding tests into strict XPASS failures.

## Layout

```
tests/test_01_imports.py        importability of all 74 modules
tests/test_02_cli.py            CLI, console script, desktop launch
tests/test_03_packaging.py      pyproject / setup.cfg / wheel consistency
tests/test_04_core_behaviour.py registry, units, validation, DTO, sizing, solvers, checks
tests/test_05_docs_and_repo.py  README/doc/CI/example/test-suite promises vs reality
tests/test_06_traceability.py   tests <-> issues stay in sync
issues/                         issues.yaml (source) and ISSUES.md (generated)
report/                         LaTeX report
.github/workflows/ci.yml        runs the suite on Python 3.10 and 3.12 (also fixes ISSUE-019 for this project)
```

## Scope

Tested: importability, CLI behaviour, packaging metadata, wheel contents, core function behaviour, repository
documentation and examples. Not tested: the PySide6 desktop GUI, the Django/React web app and the
OpenSees/OspGrillage/pythonOCC integrations, because the audited commit contains only stubs for them (so the
tests record that fact rather than exercising them).
