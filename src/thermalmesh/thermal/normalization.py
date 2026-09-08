"""Visualization-only colorization of temperature data.

The numerical temperature array is always authoritative; everything in this
module produces a *separate* visualization artifact and never overwrites or
replaces the numerical data (Rules 1 and 8).
"""

from __future__ import annotations

import cv2
import numpy as np

from thermalmesh.models.thermal import ThermalImage


def normalize_temperature(image: ThermalImage, vmin: float | None = None, vmax: float | None = None) -> np.ndarray:
    """Map valid temperatures to [0, 1]; invalid pixels become 0."""
    valid = image.validity_mask
    temps = image.temperature_array
    finite = temps[valid]
    if finite.size == 0:
        return np.zeros_like(temps)
    lo = finite.min() if vmin is None else vmin
    hi = finite.max() if vmax is None else vmax
    normalized = np.zeros_like(temps, dtype=np.float64)
    if hi > lo:
        normalized[valid] = np.clip((temps[valid] - lo) / (hi - lo), 0.0, 1.0)
    return normalized


def colorize_temperature(image: ThermalImage, colormap: int = cv2.COLORMAP_INFERNO) -> np.ndarray:
    """Return an (H, W, 3) uint8 BGR visualization image. Not used for any numerical output."""
    normalized = normalize_temperature(image)
    gray = (normalized * 255).astype(np.uint8)
    colored = cv2.applyColorMap(gray, colormap)
    colored[~image.validity_mask] = 0
    return colored
