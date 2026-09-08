"""Per-observation and per-image projection data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class Visibility(Enum):
    """Not a ``str`` mixin: numpy silently corrupts ``str``-subclass Enum members
    when they're stored in object arrays (``np.full``/broadcasted assignment
    coerce them to garbage single-character strings), so this stays a plain
    Enum and callers needing the label use ``.value``.
    """

    VISIBLE = "visible"
    OCCLUDED = "occluded"
    OUTSIDE_IMAGE = "outside_image"
    INVALID = "invalid"
    BACK_FACING = "back_facing"


@dataclass
class TemperatureObservation:
    """A single raw temperature reading of one geometry element from one image.

    Individual observations are never discarded before blending -- this is
    the unit of "keep individual thermal observations" (Rule 7).
    """

    image_id: str
    geometry_id: int  # vertex index / face index / point index
    temperature: float
    pixel_x: float
    pixel_y: float
    visibility: Visibility
    camera_distance: float
    viewing_angle: float  # radians, angle between surface normal and view direction
    confidence: float
    reprojection_error: float | None = None
    occlusion: bool = False

    def is_usable(self) -> bool:
        return self.visibility == Visibility.VISIBLE and not self.occlusion


@dataclass
class ProjectionResult:
    """The result of projecting the mesh into a single thermal image."""

    image_id: str
    visible_geometry: np.ndarray  # indices of geometry elements found visible
    projected_pixels: np.ndarray  # (N, 2) pixel coordinates for visible_geometry
    temperatures: np.ndarray  # (N,) sampled temperatures for visible_geometry
    confidence_map: np.ndarray  # (N,)
    visibility_mask: np.ndarray  # (num_geometry,) of Visibility values (as strings/ints)
    occlusion_mask: np.ndarray  # (num_geometry,) bool, True where occluded
    metadata: dict = field(default_factory=dict)

    def coverage(self, num_geometry: int) -> float:
        return float(len(self.visible_geometry)) / num_geometry if num_geometry else 0.0
