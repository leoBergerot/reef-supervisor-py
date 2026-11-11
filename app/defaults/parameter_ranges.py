"""
Default recommended min/max bands by water type and catalog parameter name.

Used for soft display warnings only — measure create/update must never reject
values based on these defaults. Per-tank overrides are out of scope for now.
"""

from __future__ import annotations

from typing import Any

WaterType = str

# Catalog `parameter.name` → recommended band.
# Optional soft_min / soft_max widen the soft-warn pad; when omitted the client
# (and evaluate helpers) pad ~20% of the span.
DEFAULT_PARAMETER_RANGES: dict[str, dict[str, dict[str, float]]] = {
    "seawater": {
        # Classic mixed reef (SPS/LPS community) norms.
        "Temperature": {"min": 24.0, "max": 27.0, "soft_min": 22.0, "soft_max": 29.0},
        "Alkalinity": {"min": 7.0, "max": 11.0},
        "Calcium": {"min": 380.0, "max": 450.0},
        "Magnesium": {"min": 1250.0, "max": 1450.0},
        "Nitrate": {"min": 1.0, "max": 20.0},
        "Phosphate": {"min": 0.02, "max": 0.15},
        # Catalog Salinity uses unit "Density" (specific gravity), not ppt.
        "Salinity": {"min": 1.024, "max": 1.026, "soft_min": 1.022, "soft_max": 1.028},
        "Density": {"min": 1.024, "max": 1.026, "soft_min": 1.022, "soft_max": 1.028},
        "Power of hydrogen": {"min": 7.8, "max": 8.5},
        "Nitrite": {"min": 0.0, "max": 0.05},
        "Silicate": {"min": 0.0, "max": 0.5},
        "Water hardness": {"min": 6.0, "max": 12.0},
    },
    "freshwater": {
        "Temperature": {"min": 22.0, "max": 28.0, "soft_min": 18.0, "soft_max": 32.0},
        "Power of hydrogen": {"min": 6.5, "max": 7.8},
        "Alkalinity": {"min": 3.0, "max": 8.0},
        "Nitrite": {"min": 0.0, "max": 0.1},
        "Nitrate": {"min": 0.0, "max": 40.0},
        "Water hardness": {"min": 4.0, "max": 12.0},
        "Phosphate": {"min": 0.0, "max": 1.0},
        "Calcium": {"min": 40.0, "max": 120.0},
    },
}


def normalize_water_type(water_type: str | None) -> str:
    return "freshwater" if water_type == "freshwater" else "seawater"


def resolve_default_range(parameter_name: str | None, water_type: str | None) -> dict[str, float] | None:
    if not parameter_name:
        return None
    table = DEFAULT_PARAMETER_RANGES.get(normalize_water_type(water_type), {})
    band = table.get(parameter_name)
    if not band:
        return None
    return dict(band)


def list_default_ranges(water_type: str | None) -> list[dict[str, Any]]:
    table = DEFAULT_PARAMETER_RANGES.get(normalize_water_type(water_type), {})
    rows: list[dict[str, Any]] = []
    for name, band in table.items():
        row: dict[str, Any] = {"name": name, "min": band["min"], "max": band["max"]}
        if "soft_min" in band:
            row["soft_min"] = band["soft_min"]
        if "soft_max" in band:
            row["soft_max"] = band["soft_max"]
        rows.append(row)
    return rows
