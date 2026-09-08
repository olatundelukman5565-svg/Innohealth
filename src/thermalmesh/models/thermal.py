"""Thermal image data model.

Thermal data is stored as a height x width floating-point *temperature*
array plus a validity mask -- never only as an RGB visualization.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class ThermalImage:
    image_id: str
    temperature_array: np.ndarray  # (H, W) float32/float64, raw/calibrated temperature
    unit: str = "unknown"
    source_file: str | None = None
    validity_mask: np.ndarray | None = None
    raw_values: np.ndarray | None = None  # untouched values as parsed, before calibration
    calibration_applied: bool = False
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.temperature_array = np.asarray(self.temperature_array, dtype=np.float64)
        if self.temperature_array.ndim != 2:
            raise ValueError(f"temperature_array must be 2D (H, W), got shape {self.temperature_array.shape}")
        if self.raw_values is None:
            self.raw_values = self.temperature_array.copy()
        if self.validity_mask is None:
            self.validity_mask = np.isfinite(self.temperature_array)
        else:
            self.validity_mask = np.asarray(self.validity_mask, dtype=bool)

    @property
    def height(self) -> int:
        return self.temperature_array.shape[0]

    @property
    def width(self) -> int:
        return self.temperature_array.shape[1]

    def valid_fraction(self) -> float:
        return float(self.validity_mask.mean()) if self.validity_mask.size else 0.0

    def statistics(self) -> dict:
        valid = self.temperature_array[self.validity_mask]
        if valid.size == 0:
            return {"valid_pixels": 0, "invalid_pixels": int(self.validity_mask.size), "min": None,
                    "max": None, "mean": None, "median": None, "std": None}
        return {
            "valid_pixels": int(valid.size),
            "invalid_pixels": int(self.validity_mask.size - valid.size),
            "min": float(valid.min()),
            "max": float(valid.max()),
            "mean": float(valid.mean()),
            "median": float(np.median(valid)),
            "std": float(valid.std()),
        }
