"""Mesh data model."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from thermalmesh.models.transforms import CoordinateSystem


@dataclass
class MeshData:
    """A triangle mesh with optional per-vertex thermal/UV attributes.

    Raw geometry is never discarded; per-vertex/per-face temperature arrays
    are populated by later pipeline stages and kept alongside the geometry
    rather than baked into color.
    """

    vertices: np.ndarray
    faces: np.ndarray
    normals: np.ndarray | None = None
    colors: np.ndarray | None = None
    uv_coordinates: np.ndarray | None = None
    vertex_temperatures: np.ndarray | None = None
    face_temperatures: np.ndarray | None = None
    coordinate_system: CoordinateSystem = CoordinateSystem.FINAL_MESH
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.vertices = np.asarray(self.vertices, dtype=np.float64)
        self.faces = np.asarray(self.faces, dtype=np.int64)
        if self.vertices.ndim != 2 or self.vertices.shape[1] != 3:
            raise ValueError(f"vertices must be (N, 3), got {self.vertices.shape}")
        if self.faces.size and (self.faces.ndim != 2 or self.faces.shape[1] != 3):
            raise ValueError(f"faces must be (M, 3), got {self.faces.shape}")

    @property
    def num_vertices(self) -> int:
        return self.vertices.shape[0]

    @property
    def num_faces(self) -> int:
        return self.faces.shape[0]

    @property
    def bounding_box(self) -> tuple[np.ndarray, np.ndarray]:
        return self.vertices.min(axis=0), self.vertices.max(axis=0)

    @property
    def centroid(self) -> np.ndarray:
        return self.vertices.mean(axis=0)

    @property
    def dimensions(self) -> np.ndarray:
        lo, hi = self.bounding_box
        return hi - lo

    def is_valid(self) -> bool:
        if self.num_vertices == 0:
            return False
        if not np.all(np.isfinite(self.vertices)):
            return False
        if self.faces.size and (self.faces.min() < 0 or self.faces.max() >= self.num_vertices):
            return False
        return True

    def copy(self) -> "MeshData":
        return MeshData(
            vertices=self.vertices.copy(),
            faces=self.faces.copy(),
            normals=None if self.normals is None else self.normals.copy(),
            colors=None if self.colors is None else self.colors.copy(),
            uv_coordinates=None if self.uv_coordinates is None else self.uv_coordinates.copy(),
            vertex_temperatures=None if self.vertex_temperatures is None else self.vertex_temperatures.copy(),
            face_temperatures=None if self.face_temperatures is None else self.face_temperatures.copy(),
            coordinate_system=self.coordinate_system,
            metadata=dict(self.metadata),
        )
