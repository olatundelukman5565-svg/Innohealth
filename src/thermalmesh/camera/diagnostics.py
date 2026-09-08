"""Shared silhouette/reprojection diagnostics for pose estimation and refinement.

Raw thermal arrays generally lack visual texture features, so pose
estimation/refinement here is correspondence-free: it segments the warm
object from the (cooler) background in the thermal image, renders an
approximate mesh silhouette for a candidate pose, and scores/optimizes
their overlap. This is a real, working geometric technique -- not a
placeholder -- but its accuracy against Innohealth's actual thermal
signatures still needs validation against real data (see docs/alignment.md).
"""

from __future__ import annotations

import cv2
import numpy as np

from thermalmesh.camera.projection import in_image_bounds, project_points
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.thermal import ThermalImage


def segment_thermal_foreground(image: ThermalImage) -> np.ndarray:
    """Otsu-threshold the valid temperature pixels into a foreground/background mask.

    Assumes the object of interest is thermally distinct from its surroundings,
    which is typical for living subjects/warm equipment against ambient
    background -- but is an assumption, not a guarantee, for arbitrary scenes.
    """
    valid = image.validity_mask
    temps = np.where(valid, image.temperature_array, np.nan)
    finite = temps[valid]
    if finite.size == 0:
        return np.zeros_like(valid, dtype=bool)

    normalized = np.zeros_like(temps, dtype=np.uint8)
    lo, hi = finite.min(), finite.max()
    if hi > lo:
        normalized[valid] = np.clip(((temps[valid] - lo) / (hi - lo)) * 255, 0, 255).astype(np.uint8)

    _, mask = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = (mask > 0) & valid

    # The warmer side of the threshold is assumed foreground; if that leaves
    # the majority of the image "foreground" the polarity is likely flipped.
    if mask.mean() > 0.5:
        mask = valid & ~mask
    return mask


def render_silhouette_mask(
    vertices_world: np.ndarray,
    camera: Camera,
    pose: CameraPose,
    downsample: int = 4,
) -> np.ndarray:
    """Approximate mesh silhouette as the convex hull of projected vertices.

    A convex-hull rasterization is a reasonable approximation for the
    roughly-convex objects typical of body/object scans and is cheap enough
    to call repeatedly inside a pose optimization loop. It is not a full
    depth-buffer render (see thermal/occlusion.py for per-sample ray casting
    used during actual thermal projection).
    """
    width = max(1, camera.image_width // downsample)
    height = max(1, camera.image_height // downsample)
    mask = np.zeros((height, width), dtype=np.uint8)

    pixels, depths, in_front = project_points(vertices_world, camera, pose)
    pixels = pixels / downsample
    valid = in_front & in_image_bounds(pixels, width, height)
    if valid.sum() < 3:
        return mask.astype(bool)

    points = pixels[valid].astype(np.float32)
    hull = cv2.convexHull(points)
    cv2.fillConvexPoly(mask, hull.astype(np.int32), 1)
    return mask.astype(bool)


def resize_mask(mask: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    resized = cv2.resize(mask.astype(np.uint8), (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
    return resized.astype(bool)


def mask_iou(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    if mask_a.shape != mask_b.shape:
        mask_b = resize_mask(mask_b, mask_a.shape)
    intersection = np.logical_and(mask_a, mask_b).sum()
    union = np.logical_or(mask_a, mask_b).sum()
    return float(intersection / union) if union else 0.0


def mask_bbox(mask: np.ndarray) -> tuple[float, float, float, float] | None:
    ys, xs = np.nonzero(mask)
    if xs.size == 0:
        return None
    return float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())
