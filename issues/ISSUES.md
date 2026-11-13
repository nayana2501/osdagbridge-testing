# OsdagBridge - Issue Register

Target: https://github.com/osdag-admin/OsdagBridge @ `2cb7ddc` (2025-12-07)  
Environment: Python 3.13.18, pytest 9.1.1, Linux 6.18 (x86_64)

| Severity | Count |
|---|---|
| Critical | 1 |
| High | 4 |
| Medium | 9 |
| Low | 10 |
| **Total** | **24** |

| ID | Severity | Component | Title |
|---|---|---|---|
| ISSUE-001 | Critical | core | Every osdagbridge.core.* import fails: core/__init__.py imports a missing `models` module |
| ISSUE-002 | Low | packaging | pyproject.toml declares license file `LICENSE`, but the repository contains `LICENSE.txt` |
| ISSUE-003 | Medium | packaging / CLI | No console-script entry point, so the documented `osdagbridge ...` command does not exist |
| ISSUE-004 | High | CLI | CLI is a stub: ignores all arguments, never fails, has no `report` command |
| ISSUE-005 | Medium | desktop | Desktop app cannot be launched as documented; PySide6 is not a declared dependency |
| ISSUE-006 | Low | packaging / reports | LaTeX report template is not shipped in the built wheel |
| ISSUE-007 | Medium | codes | Code registry knows only IRC:6-2017; IRC:22-2015 and IRC:24-2010 are listed in README but unavailable |
| ISSUE-008 | High | loads | IRC:6 vehicle loads and Class A vehicle are empty lists |
| ISSUE-009 | Medium | utils | to_si() never converts units and silently accepts unknown units |
| ISSUE-010 | Medium | utils | validate_project() returns True for every input, including None, {} and negative span |
| ISSUE-011 | Medium | plate_girder | PlateGirderDTO has a single field (`name`); no span, width, loading or section data |
| ISSUE-012 | Medium | plate_girder | preliminary_sizing() returns the girder name as `depth_m` |
| ISSUE-013 | Medium | plate_girder / solvers | design(), analyse() and run_native_analysis() report success for any input; solver errors use RuntimeError |
| ISSUE-014 | High | bridge_components | Girder area() and check_local_buckling() take no inputs; the check always passes |
| ISSUE-015 | Low | packaging | Three different versions: __version__ = 0.0.0, pyproject 0.1.0, setup.cfg 0.0.0 |
| ISSUE-016 | Low | packaging | requires-python >=3.9 but classifiers list only Python 3.10 and 3.11 |
| ISSUE-017 | Low | packaging | Author e-mail domain looks like a typo: `contact-osdag@efossee.in` |
| ISSUE-018 | Low | packaging | core/bridge_components/super_structure/ has no __init__.py |
| ISSUE-019 | Medium | CI | README cites .github/workflows/ci.yml but the repository has no CI |
| ISSUE-020 | Low | documentation | README paths are wrong: bridge_types/, bridge_components/ and web/ are not under src/osdagbridge/ |
| ISSUE-021 | Low | documentation | docs/architecture.md, developer_guide.md and user_guide.md are one-line placeholders |
| ISSUE-022 | Low | examples | examples/plate_girder/verification_case_01.yaml and _02.yaml contain only a comment |
| ISSUE-023 | High | tests | Upstream test suite is `assert True` placeholders, so it passes while the package's core is unimportable |
| ISSUE-024 | Low | tests | tests/integration/verification_ddcl_cases.py is never collected by pytest |

## ISSUE-001 - Every osdagbridge.core.* import fails: core/__init__.py imports a missing `models` module

**Severity:** Critical | **Component:** core

**Steps to reproduce**

1. pip install -e .
2. python -c "import osdagbridge.core.utils.units"

**Expected:** The module imports.

**Actual:** ModuleNotFoundError: No module named 'osdagbridge.core.models'. Because core/__init__.py runs `from .models import *`, 67 of the package's 74 modules are unimportable (everything under osdagbridge.core: utils, solvers, bridge_types, loads, reports, components). Only the top-level package and the CLI/desktop stubs still import.

**Covered by:** test_01_imports.py::test_core_package_imports, ::test_every_module_is_importable (xfail); ::test_issue_001_root_cause_is_the_missing_models_module (passes)

**Suggested fix:** Remove the star-import or add core/models.py. With an empty models.py all modules import, confirmed in a temporary copy.

---

## ISSUE-002 - pyproject.toml declares license file `LICENSE`, but the repository contains `LICENSE.txt`

**Severity:** Low | **Component:** packaging

**Steps to reproduce**

pip wheel --no-deps .

**Expected:** Build completes without license warnings.

**Actual:** BuildBackendWarning: File '.../LICENSE' cannot be found. Also reported: `project.license` as a TOML table and License classifiers are deprecated (setuptools will stop accepting them in 2027).

**Covered by:** test_03_packaging.py::test_pyproject_license_file_exists

**Suggested fix:** Rename the file or point to LICENSE.txt; migrate to `license = "MIT"` and `license-files`.

---

## ISSUE-003 - No console-script entry point, so the documented `osdagbridge ...` command does not exist

**Severity:** Medium | **Component:** packaging / CLI

**Steps to reproduce**

1. pip install -e .
2. osdagbridge --help

**Expected:** README documents `osdagbridge analyze project.yaml --solver native`.

**Actual:** Command not found: pyproject.toml has no [project.scripts]; the built wheel has no entry_points.txt.

**Covered by:** test_02_cli.py::test_console_script_is_declared

**Suggested fix:** Add `[project.scripts] osdagbridge = "osdagbridge.cli.__main__:main"` once the CLI parses arguments.

---

## ISSUE-004 - CLI is a stub: ignores all arguments, never fails, has no `report` command

**Severity:** High | **Component:** CLI

**Steps to reproduce**

1. python -m osdagbridge.cli analyze does_not_exist.yaml --solver native
2. echo $?

**Expected:** An error for the missing file and a non-zero exit status; `--help` lists `analyze` and `report`.

**Actual:** Prints `osdagbridge CLI (stub)` and exits 0 for every input, including unknown sub-commands.

**Covered by:** test_02_cli.py (4 xfail tests: help, acknowledge file, missing file, unknown command)

**Suggested fix:** Implement argparse/click sub-commands and return non-zero exit codes on error.

---

## ISSUE-005 - Desktop app cannot be launched as documented; PySide6 is not a declared dependency

**Severity:** Medium | **Component:** desktop

**Steps to reproduce**

python -m osdagbridge.desktop

**Expected:** Starts the desktop UI (README).

**Actual:** `No module named osdagbridge.desktop.__main__; 'osdagbridge.desktop' is a package and cannot be directly executed`. README says the GUI uses PySide6, but no optional-dependency group lists it. desktop/main.py only defines `start()` which prints a message.

**Covered by:** test_02_cli.py::test_desktop_package_is_runnable_with_dash_m, ::test_pyside6_is_declared_as_a_dependency

**Suggested fix:** Add desktop/__main__.py calling start(); add a `desktop = ["PySide6"]` extra.

---

## ISSUE-006 - LaTeX report template is not shipped in the built wheel

**Severity:** Low | **Component:** packaging / reports

**Steps to reproduce**

Build a wheel and list its contents.

**Expected:** core/reports/templates/default_template.tex is included.

**Actual:** Not included: no package-data / MANIFEST configuration, and the templates directory is not a package.

**Covered by:** test_03_packaging.py::test_report_templates_are_shipped_in_the_wheel

**Suggested fix:** Declare `[tool.setuptools.package-data]` for `*.tex`.

---

## ISSUE-007 - Code registry knows only IRC:6-2017; IRC:22-2015 and IRC:24-2010 are listed in README but unavailable

**Severity:** Medium | **Component:** codes

**Steps to reproduce**

get_code('IRC:22-2015')

**Expected:** Returns the code module (README: `Included under core/utils/codes/`).

**Actual:** Returns None. irc22_2015.py and irc24_2010.py contain only a docstring.

**Covered by:** test_04_core_behaviour.py::test_registry_contains_all_documented_codes (2 params)

**Suggested fix:** Register the modules once implemented, or mark them 'planned' in README.

---

## ISSUE-008 - IRC:6 vehicle loads and Class A vehicle are empty lists

**Severity:** High | **Component:** loads

**Steps to reproduce**

get_vehicle_loads(); class_a()

**Expected:** Axle loads and spacings per IRC:6-2017.

**Actual:** Both return []. Any analysis built on them would run with no live load.

**Covered by:** test_04_core_behaviour.py::test_irc6_defines_vehicle_loads, ::test_class_a_vehicle_has_axles

**Suggested fix:** Implement the load models with unit tests against IRC:6 tables.

---

## ISSUE-009 - to_si() never converts units and silently accepts unknown units

**Severity:** Medium | **Component:** utils

**Steps to reproduce**

to_si(250.0, 'mm'); to_si(1.0, 'furlong')

**Expected:** 0.25 for mm to m; an error for an unknown unit.

**Actual:** Returns the input unchanged (250.0) in every case. A 250 mm value would be treated as 250 m.

**Covered by:** test_04_core_behaviour.py::test_to_si_converts_units (3 params), ::test_to_si_rejects_unknown_unit

**Suggested fix:** Implement a unit table and raise OsdagError on unknown units.

---

## ISSUE-010 - validate_project() returns True for every input, including None, {} and negative span

**Severity:** Medium | **Component:** utils

**Steps to reproduce**

validate_project(None); validate_project({'project': {'span_m': -5.0}})

**Expected:** Invalid projects are rejected.

**Actual:** Always True.

**Covered by:** test_04_core_behaviour.py::test_validate_project_rejects_invalid_input (4 params)

**Suggested fix:** Validate with pydantic (already a declared dependency) and raise OsdagError.

---

## ISSUE-011 - PlateGirderDTO has a single field (`name`); no span, width, loading or section data

**Severity:** Medium | **Component:** plate_girder

**Steps to reproduce**

dataclasses.fields(PlateGirderDTO)

**Expected:** An input schema able to represent examples/plate_girder/example_basic.yaml (span_m: 30.0).

**Actual:** Only `name: str`.

**Covered by:** test_04_core_behaviour.py::test_dto_models_basic_geometry

**Suggested fix:** Model the YAML schema (pydantic) and load it from file.

---

## ISSUE-012 - preliminary_sizing() returns the girder name as `depth_m`

**Severity:** Medium | **Component:** plate_girder

**Steps to reproduce**

preliminary_sizing(PlateGirderDTO(name='demo'))

**Expected:** A numeric depth in metres.

**Actual:** {'depth_m': 'demo'}: a string where a length is expected; downstream arithmetic would raise or mislead.

**Covered by:** test_04_core_behaviour.py::test_preliminary_sizing_depth_is_numeric

**Suggested fix:** Compute depth from span (e.g. span/L-over-d ratio) and return a float.

---

## ISSUE-013 - design(), analyse() and run_native_analysis() report success for any input; solver errors use RuntimeError

**Severity:** Medium | **Component:** plate_girder / solvers

**Steps to reproduce**

design(None); analyse(object(), solver='no-such-solver'); run_native_analysis(None)

**Expected:** Invalid input or an unknown solver is rejected with an OsdagError.

**Actual:** Each returns an 'ok' result. The OpenSees/OspGrillage adapters raise a bare RuntimeError instead of the project's own OsdagError.

**Covered by:** test_04_core_behaviour.py::test_design_rejects_garbage_input, ::test_analyse_rejects_unknown_solver, ::test_native_solver_rejects_null_model, ::test_adapters_use_project_exception_type

**Suggested fix:** Validate inputs, dispatch on the solver name, derive adapter errors from OsdagError.

---

## ISSUE-014 - Girder area() and check_local_buckling() take no inputs; the check always passes

**Severity:** High | **Component:** bridge_components

**Steps to reproduce**

check_local_buckling(b=1.0, t=0.001, fy=250.0)

**Expected:** An absurdly slender plate (b/t = 1000) fails the check; area() derives from the section.

**Actual:** TypeError: unexpected keyword argument (no parameters at all). With no arguments the check returns True and area() returns 0.0, so a structural check that cannot fail would give false assurance.

**Covered by:** test_04_core_behaviour.py::test_girder_area_computes_from_section, ::test_local_buckling_check_uses_section

**Suggested fix:** Implement per IS 800 / IRC:24 limits and add boundary-value tests.

---

## ISSUE-015 - Three different versions: __version__ = 0.0.0, pyproject 0.1.0, setup.cfg 0.0.0

**Severity:** Low | **Component:** packaging

**Steps to reproduce**

python -c "import osdagbridge, importlib.metadata as m; print(osdagbridge.__version__, m.version('osdagbridge'))"

**Expected:** One version everywhere.

**Actual:** Prints `0.0.0 0.1.0`.

**Covered by:** test_03_packaging.py::test_version_is_single_sourced, ::test_setup_cfg_version_matches_pyproject

**Suggested fix:** Single-source the version (dynamic = ["version"]) and delete setup.cfg.

---

## ISSUE-016 - requires-python >=3.9 but classifiers list only Python 3.10 and 3.11

**Severity:** Low | **Component:** packaging

**Steps to reproduce**

Read pyproject.toml.

**Expected:** Declared floor equals the oldest tested version.

**Actual:** Floor 3.9 versus oldest classifier 3.10; 3.12+ not classified (install succeeded on 3.13).

**Covered by:** test_03_packaging.py::test_requires_python_matches_classifiers

**Suggested fix:** Align requires-python, classifiers, ruff/mypy targets, and add a CI matrix.

---

## ISSUE-017 - Author e-mail domain looks like a typo: `contact-osdag@efossee.in`

**Severity:** Low | **Component:** packaging

**Steps to reproduce**

Read pyproject.toml [project].authors.

**Expected:** The FOSSEE pages use contact-osdag@fossee.in.

**Actual:** Domain is efossee.in, so mail to the package contact would not reach the team.

**Covered by:** test_03_packaging.py::test_author_email_domain_looks_valid

**Suggested fix:** Correct the address.

---

## ISSUE-018 - core/bridge_components/super_structure/ has no __init__.py

**Severity:** Low | **Component:** packaging

**Steps to reproduce**

List packages for src/osdagbridge.

**Expected:** Every package directory is a regular package.

**Actual:** Implicit namespace package: it works in the wheel, but is inconsistent with every sibling and can be skipped by tools that do not support namespace packages.

**Covered by:** test_03_packaging.py::test_every_package_directory_has_init

**Suggested fix:** Add an __init__.py.

---

## ISSUE-019 - README cites .github/workflows/ci.yml but the repository has no CI

**Severity:** Medium | **Component:** CI

**Steps to reproduce**

ls .github

**Expected:** Workflow file exists (README: `Continuous integration runs automatically`).

**Actual:** No .github directory.

**Covered by:** test_05_docs_and_repo.py::test_ci_workflow_mentioned_in_readme_exists

**Suggested fix:** Add a workflow. A ready-made one is in this project: .github/workflows/ci.yml.

---

## ISSUE-020 - README paths are wrong: bridge_types/, bridge_components/ and web/ are not under src/osdagbridge/

**Severity:** Low | **Component:** documentation

**Steps to reproduce**

Follow README: `python src/osdagbridge/web/backend/manage.py runserver`.

**Expected:** Documented paths exist.

**Actual:** Real locations are core/bridge_types, core/bridge_components and top-level web/. The runserver command fails with file-not-found; the real manage.py is a stub that prints `Django manage stub`.

**Covered by:** test_05_docs_and_repo.py::test_readme_code_locations_exist, ::test_readme_runserver_path_exists

**Suggested fix:** Update the README (project-structure tree and Key Code Locations).

---

## ISSUE-021 - docs/architecture.md, developer_guide.md and user_guide.md are one-line placeholders

**Severity:** Low | **Component:** documentation

**Steps to reproduce**

cat docs/*.md

**Expected:** Usable documentation.

**Actual:** Each reads 'Documentation placeholder.'

**Covered by:** test_05_docs_and_repo.py::test_docs_are_not_placeholders (3 params)

**Suggested fix:** Write the guides; this report's findings can seed the developer guide.

---

## ISSUE-022 - examples/plate_girder/verification_case_01.yaml and _02.yaml contain only a comment

**Severity:** Low | **Component:** examples

**Steps to reproduce**

python -c "import yaml; print(yaml.safe_load(open('verification_case_01.yaml')))"

**Expected:** Benchmark input data for verification.

**Actual:** Parses to None.

**Covered by:** test_05_docs_and_repo.py::test_verification_cases_contain_data (2 params)

**Suggested fix:** Add the DDCL benchmark inputs and expected outputs.

---

## ISSUE-023 - Upstream test suite is `assert True` placeholders, so it passes while the package's core is unimportable

**Severity:** High | **Component:** tests

**Steps to reproduce**

pytest -q in a fresh install

**Expected:** Failing tests when the package is broken.

**Actual:** `......` all pass, yet ISSUE-001 makes osdagbridge.core unusable. All 7 test files are placeholders.

**Covered by:** test_05_docs_and_repo.py::test_upstream_tests_contain_real_assertions

**Suggested fix:** Replace the placeholders. This project's tests can be ported as a starting point.

---

## ISSUE-024 - tests/integration/verification_ddcl_cases.py is never collected by pytest

**Severity:** Low | **Component:** tests

**Steps to reproduce**

pytest --collect-only -q

**Expected:** 7 test files are collected.

**Actual:** 6 are collected; verification_ddcl_cases.py does not match the default `test_*.py` pattern, so even once filled in, the verification cases would never run.

**Covered by:** test_05_docs_and_repo.py::test_every_upstream_test_file_is_collectable

**Suggested fix:** Rename it to test_verification_ddcl_cases.py.

---
