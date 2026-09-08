"""Point cloud data model."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from thermalmesh.models.transforms import CoordinateSystem


@dataclass
class PointCloudData:
    """A raw point cloud, typically the optional initial acquisition scan."""

    points: np.ndarray
    normals: np.ndarray | None = None
    temperature_values: np.ndarray | None = None
    coordinate_system: CoordinateSystem = CoordinateSystem.ACQUISITION
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.points = np.asarray(self.points, dtype=np.float64)
        if self.points.ndim != 2 or self.points.shape[1] != 3:
            raise ValueError(f"points must be (N, 3), got {self.points.shape}")

    @property
    def num_points(self) -> int:
        return self.points.shape[0]

    @property
    def centroid(self) -> np.ndarray:
        return self.points.mean(axis=0)

    @property
    def bounding_box(self) -> tuple[np.ndarray, np.ndarray]:
        return self.points.min(axis=0), self.points.max(axis=0)

    def is_valid(self) -> bool:
        return self.num_points > 0 and bool(np.all(np.isfinite(self.points)))
