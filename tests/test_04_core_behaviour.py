"""Behaviour of core functions.

These tests run against `patched_src` (ISSUE-001 shimmed) so that they exercise the functions
themselves. Tests that pass document today's behaviour; xfail tests document what the README /
function names promise but the code does not do.
"""
import pytest

from _helpers import probe


def P(body, patched_src, work):
    return probe(body, patched_src, work)


# ---------------------------------------------------------------- code registry
def test_registry_returns_irc6(patched_src, work):
    r = P("from osdagbridge.core.utils.codes.registry import get_code\n"
          "result = get_code('IRC:6-2017') is not None", patched_src, work)
    assert r is True


def test_registry_unknown_code_returns_none(patched_src, work):
    r = P("from osdagbridge.core.utils.codes.registry import get_code\n"
          "result = get_code('NOT-A-CODE')", patched_src, work)
    assert r is None


@pytest.mark.parametrize("key", ["IRC:22-2015", "IRC:24-2010"])
@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-007: README lists IRC:22/IRC:24 but the registry only knows IRC:6")
def test_registry_contains_all_documented_codes(key, patched_src, work):
    r = P(f"from osdagbridge.core.utils.codes.registry import get_code\nresult = get_code({key!r}) is not None",
          patched_src, work)
    assert r is True


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-008: IRC:6 'vehicle loads' is an empty list - no load models implemented")
def test_irc6_defines_vehicle_loads(patched_src, work):
    r = P("from osdagbridge.core.utils.codes import irc6_2017 as c\nresult = len(c.get_vehicle_loads())",
          patched_src, work)
    assert r > 0


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-008: class_a() returns no axle data")
def test_class_a_vehicle_has_axles(patched_src, work):
    r = P("from osdagbridge.core.loads.vehicle import class_a\nresult = len(class_a())", patched_src, work)
    assert r > 0


# ---------------------------------------------------------------- units & validation
def test_to_si_identity_for_si_units(patched_src, work):
    assert P("from osdagbridge.core.utils.units import to_si\nresult = to_si(5.0, 'm')", patched_src, work) == 5.0


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-009: to_si() never converts (kN->N, mm->m, ...)")
@pytest.mark.parametrize("val,unit,expected", [(1.0, "kN", 1000.0), (250.0, "mm", 0.25), (1.0, "MPa", 1.0e6)])
def test_to_si_converts_units(val, unit, expected, patched_src, work):
    r = P(f"from osdagbridge.core.utils.units import to_si\nresult = to_si({val!r}, {unit!r})", patched_src, work)
    assert r == pytest.approx(expected)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-009: to_si() silently accepts unknown units")
def test_to_si_rejects_unknown_unit(patched_src, work):
    r = P("from osdagbridge.core.utils.units import to_si\nresult = attempt(to_si, 1.0, 'furlong')",
          patched_src, work)
    assert "raised" in r


@pytest.mark.parametrize("bad", ["{}", "None", "{'project': {'span_m': -5.0}}", "{'project': {'span_m': 'abc'}}"])
@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-010: validate_project() returns True for every input")
def test_validate_project_rejects_invalid_input(bad, patched_src, work):
    r = P(f"from osdagbridge.core.utils.validation import validate_project\n"
          f"result = attempt(validate_project, {bad})", patched_src, work)
    assert r.get("ok") is False or "raised" in r


def test_validate_project_accepts_a_valid_project(patched_src, work):
    r = P("from osdagbridge.core.utils.validation import validate_project\n"
          "result = validate_project({'project': {'name': 'x', 'span_m': 30.0}})", patched_src, work)
    assert r is True


# ---------------------------------------------------------------- plate girder
def test_dto_stores_name(patched_src, work):
    r = P("from osdagbridge.core.bridge_types.plate_girder.dto import PlateGirderDTO\n"
          "result = PlateGirderDTO(name='demo').name", patched_src, work)
    assert r == "demo"


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-011: PlateGirderDTO has no span/width/loading fields")
def test_dto_models_basic_geometry(patched_src, work):
    r = P("from dataclasses import fields\n"
          "from osdagbridge.core.bridge_types.plate_girder.dto import PlateGirderDTO\n"
          "result = [f.name for f in fields(PlateGirderDTO)]", patched_src, work)
    assert any("span" in n for n in r)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-012: preliminary_sizing() returns the girder NAME as 'depth_m'")
def test_preliminary_sizing_depth_is_numeric(patched_src, work):
    r = P("from osdagbridge.core.bridge_types.plate_girder.dto import PlateGirderDTO\n"
          "from osdagbridge.core.bridge_types.plate_girder.initial_sizing import preliminary_sizing\n"
          "result = preliminary_sizing(PlateGirderDTO(name='demo'))['depth_m']", patched_src, work)
    assert isinstance(r, (int, float)) and not isinstance(r, bool)


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-013: design() reports success for any input, performs no checks")
def test_design_rejects_garbage_input(patched_src, work):
    r = P("from osdagbridge.core.bridge_types.plate_girder.designer import design\n"
          "result = attempt(design, None)", patched_src, work)
    assert "raised" in r


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-013: analyse() ignores the solver argument and reports 'ok' for unknown solvers")
def test_analyse_rejects_unknown_solver(patched_src, work):
    r = P("from osdagbridge.core.bridge_types.plate_girder.analyser import analyse\n"
          "result = attempt(analyse, object(), solver='no-such-solver')", patched_src, work)
    assert "raised" in r


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-013: native solver returns status 'ok' for a null model")
def test_native_solver_rejects_null_model(patched_src, work):
    r = P("from osdagbridge.core.solvers.native_solver import run_native_analysis\n"
          "result = attempt(run_native_analysis, None)", patched_src, work)
    assert "raised" in r


# ---------------------------------------------------------------- section properties / checks
@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-014: girder area() takes no section arguments, always returns 0.0")
def test_girder_area_computes_from_section(patched_src, work):
    r = P("from osdagbridge.core.bridge_components.super_structure.girder.properties import area\n"
          "result = attempt(area, 0.4, 0.02, 1.5, 0.012)", patched_src, work)
    assert r.get("ok") == pytest.approx(0.4 * 0.02 * 2 + 1.5 * 0.012), r


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-014: check_local_buckling() takes no inputs and always returns True")
def test_local_buckling_check_uses_section(patched_src, work):
    r = P("from osdagbridge.core.bridge_components.super_structure.girder.checks import check_local_buckling\n"
          "result = attempt(check_local_buckling, b=1.0, t=0.001, fy=250.0)", patched_src, work)
    assert r.get("ok") is False, r  # an absurdly slender plate must fail


# ---------------------------------------------------------------- solver adapters
@pytest.mark.parametrize("mod,fn", [("opensees_adapter", "run_with_opensees"),
                                    ("ospgrillage_adapter", "run_with_ospgrillage")])
def test_missing_solver_adapter_raises_runtimeerror(mod, fn, patched_src, work):
    r = P(f"from osdagbridge.core.solvers.{mod} import {fn}\nresult = attempt({fn}, None)", patched_src, work)
    assert r.get("raised") == "RuntimeError"


def test_osdag_error_is_an_exception_subclass(patched_src, work):
    r = P("from osdagbridge.core.exceptions import OsdagError\nresult = attempt(lambda: (_ for _ in ()).throw(OsdagError('boom')))",
          patched_src, work)
    assert r["raised"] == "OsdagError" and "Exception" in r["mro"]


@pytest.mark.xfail(strict=True, raises=AssertionError,
                   reason="ISSUE-013: solver adapters raise bare RuntimeError instead of the project's OsdagError")
def test_adapters_use_project_exception_type(patched_src, work):
    r = P("from osdagbridge.core.solvers.opensees_adapter import run_with_opensees\n"
          "result = attempt(run_with_opensees, None)", patched_src, work)
    assert "OsdagError" in r["mro"]
