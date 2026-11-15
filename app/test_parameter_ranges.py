from app.defaults.parameter_ranges import list_default_ranges, resolve_default_range
from app.models.parameter import ParameterRange, ParameterRangeEntry, ParameterResponse


def test_resolve_seawater_classic_reef_bands():
    calcium = resolve_default_range("Calcium", "seawater")
    assert calcium == {"min": 380.0, "max": 450.0}

    salinity = resolve_default_range("Salinity", "seawater")
    assert salinity["min"] == 1.024
    assert salinity["max"] == 1.026
    assert salinity["soft_min"] == 1.022
    assert salinity["soft_max"] == 1.028

    magnesium = resolve_default_range("Magnesium", "seawater")
    assert magnesium["min"] == 1250.0
    assert magnesium["max"] == 1450.0


def test_resolve_freshwater_defaults_and_unknown():
    nitrite = resolve_default_range("Nitrite", "freshwater")
    assert nitrite == {"min": 0.0, "max": 0.1}
    assert resolve_default_range("Magnesium", "freshwater") is None
    assert resolve_default_range("Unknown", "seawater") is None
    # Unknown water type falls back to seawater table.
    assert resolve_default_range("Calcium", "brackish")["min"] == 380.0


def test_list_default_ranges_shapes():
    seawater = {row["name"]: row for row in list_default_ranges("seawater")}
    assert "Calcium" in seawater
    assert "soft_min" in seawater["Salinity"]
    assert "soft_min" not in seawater["Calcium"]

    freshwater = {row["name"]: row for row in list_default_ranges("freshwater")}
    assert "Power of hydrogen" in freshwater
    assert "Salinity" not in freshwater


def test_parameter_response_range_is_optional():
    bare = ParameterResponse(
        id=1,
        name="Calcium",
        sub_name="CA",
        need_value=True,
    )
    assert bare.range is None

    with_range = ParameterResponse(
        id=1,
        name="Calcium",
        sub_name="CA",
        need_value=True,
        range=ParameterRange(min=380, max=450),
    )
    assert with_range.range.min == 380
    assert with_range.range.soft_min is None

    entry = ParameterRangeEntry(name="Calcium", min=380, max=450, soft_min=None, soft_max=None)
    assert entry.name == "Calcium"
