"""Thermal calibration layer.

Applies an optional configured scale/offset/unit conversion. Raw values are
never modified in place -- calibration always produces a new array, and if
no calibration is configured, the data is passed through unchanged with
``calibration_applied=False`` so downstream consumers know the units are
whatever the source file provided.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from thermalmesh.models.thermal import ThermalImage

_CELSIUS_TO_FAHRENHEIT = lambda c: c * 9.0 / 5.0 + 32.0  # noqa: E731
_FAHRENHEIT_TO_CELSIUS = lambda f: (f - 32.0) * 5.0 / 9.0  # noqa: E731
_CELSIUS_TO_KELVIN = lambda c: c + 273.15  # noqa: E731
_KELVIN_TO_CELSIUS = lambda k: k - 273.15  # noqa: E731


@dataclass
class CalibrationConfig:
    scale: float = 1.0
    offset: float = 0.0
    source_unit: str | None = None  # unit the raw file is actually in, if known
    target_unit: str = "celsius"


def apply_calibration(image: ThermalImage, config: CalibrationConfig | None) -> ThermalImage:
    """Return a new ThermalImage with calibration applied, preserving ``raw_values``."""
    if config is None:
        image.metadata.setdefault("calibration", "none (raw values preserved as-is)")
        return image

    values = image.raw_values.copy()
    values = values * config.scale + config.offset

    if config.source_unit and config.source_unit != config.target_unit:
        values = _convert_unit(values, config.source_unit, config.target_unit)

    calibrated = ThermalImage(
        image_id=image.image_id,
        temperature_array=values,
        unit=config.target_unit,
        source_file=image.source_file,
        validity_mask=image.validity_mask.copy(),
        raw_values=image.raw_values.copy(),
        calibration_applied=True,
        metadata={**image.metadata, "calibration": {"scale": config.scale, "offset": config.offset,
                                                       "source_unit": config.source_unit,
                                                       "target_unit": config.target_unit}},
    )
    return calibrated


def _convert_unit(values: np.ndarray, source_unit: str, target_unit: str) -> np.ndarray:
    conversions = {
        ("fahrenheit", "celsius"): _FAHRENHEIT_TO_CELSIUS,
        ("celsius", "fahrenheit"): _CELSIUS_TO_FAHRENHEIT,
        ("kelvin", "celsius"): _KELVIN_TO_CELSIUS,
        ("celsius", "kelvin"): _CELSIUS_TO_KELVIN,
    }
    key = (source_unit.lower(), target_unit.lower())
    if key not in conversions:
        if source_unit.lower() == target_unit.lower():
            return values
        raise ValueError(f"Unsupported unit conversion {source_unit} -> {target_unit}")
    return conversions[key](values)
