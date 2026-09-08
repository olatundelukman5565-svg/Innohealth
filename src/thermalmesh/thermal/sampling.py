"""Sub-pixel temperature sampling from a thermal array."""

from __future__ import annotations

import numpy as np

from thermalmesh.models.thermal import ThermalImage


def sample_nearest(image: ThermalImage, pixels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Nearest-neighbor sample. Returns (temperatures, valid) for each pixel row."""
    pixels = np.asarray(pixels, dtype=np.float64)
    xs = np.round(pixels[:, 0]).astype(np.int64)
    ys = np.round(pixels[:, 1]).astype(np.int64)
    in_bounds = (xs >= 0) & (xs < image.width) & (ys >= 0) & (ys < image.height)

    temps = np.full(pixels.shape[0], np.nan)
    valid = np.zeros(pixels.shape[0], dtype=bool)
    xs_c, ys_c = np.clip(xs, 0, image.width - 1), np.clip(ys, 0, image.height - 1)
    sampled = image.temperature_array[ys_c, xs_c]
    sampled_valid = image.validity_mask[ys_c, xs_c]
    ok = in_bounds & sampled_valid
    temps[ok] = sampled[ok]
    valid[ok] = True
    return temps, valid


def sample_bilinear(image: ThermalImage, pixels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Bilinear-interpolate temperature at sub-pixel coordinates.

    A sample is only marked valid if all four surrounding pixels are valid,
    so invalid pixels never silently leak into a valid sample's value.
    """
    pixels = np.asarray(pixels, dtype=np.float64)
    x = pixels[:, 0]
    y = pixels[:, 1]

    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1

    in_bounds = (x0 >= 0) & (x1 < image.width) & (y0 >= 0) & (y1 < image.height)

    temps = np.full(pixels.shape[0], np.nan)
    valid = np.zeros(pixels.shape[0], dtype=bool)
    if not in_bounds.any():
        return temps, valid

    idx = np.nonzero(in_bounds)[0]
    x0i, x1i, y0i, y1i = x0[idx], x1[idx], y0[idx], y1[idx]

    v00 = image.temperature_array[y0i, x0i]
    v01 = image.temperature_array[y0i, x1i]
    v10 = image.temperature_array[y1i, x0i]
    v11 = image.temperature_array[y1i, x1i]

    m00 = image.validity_mask[y0i, x0i]
    m01 = image.validity_mask[y0i, x1i]
    m10 = image.validity_mask[y1i, x0i]
    m11 = image.validity_mask[y1i, x1i]
    all_valid = m00 & m01 & m10 & m11

    wx = (x[idx] - x0i)
    wy = (y[idx] - y0i)

    top = v00 * (1 - wx) + v01 * wx
    bottom = v10 * (1 - wx) + v11 * wx
    interpolated = top * (1 - wy) + bottom * wy

    temps[idx[all_valid]] = interpolated[all_valid]
    valid[idx[all_valid]] = True
    return temps, valid


def sample_temperature(image: ThermalImage, pixels: np.ndarray, method: str = "bilinear") -> tuple[np.ndarray, np.ndarray]:
    if method == "bilinear":
        return sample_bilinear(image, pixels)
    if method == "nearest":
        return sample_nearest(image, pixels)
    raise ValueError(f"Unknown sampling method '{method}'")
