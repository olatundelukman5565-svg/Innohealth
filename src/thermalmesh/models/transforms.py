"""Explicit coordinate-system tracking and homogeneous transform utilities.

Every geometric quantity in the pipeline is tagged with the coordinate
system it lives in, and every conversion between systems goes through an
explicit 4x4 homogeneous :class:`Transform`. Nothing is silently assumed
to already be aligned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class CoordinateSystem(str, Enum):
    """Named coordinate spaces tracked throughout the pipeline."""

    ACQUISITION = "acquisition"
    FINAL_MESH = "final_mesh"
    WORLD = "world"
    CAMERA = "camera"
    IMAGE = "image"
    UV = "uv"


@dataclass
class Transform:
    """A homogeneous 4x4 rigid/affine transform between two named spaces."""

    matrix: np.ndarray
    source: CoordinateSystem
    target: CoordinateSystem
    method: str = "identity"
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.matrix = np.asarray(self.matrix, dtype=np.float64)
        if self.matrix.shape != (4, 4):
            raise ValueError(f"Transform matrix must be 4x4, got {self.matrix.shape}")

    @classmethod
    def identity(cls, source: CoordinateSystem, target: CoordinateSystem) -> "Transform":
        return cls(matrix=np.eye(4), source=source, target=target, method="identity")

    @classmethod
    def from_rotation_translation(
        cls,
        rotation: np.ndarray,
        translation: np.ndarray,
        source: CoordinateSystem,
        target: CoordinateSystem,
        method: str = "rigid",
        confidence: float = 1.0,
    ) -> "Transform":
        matrix = np.eye(4)
        matrix[:3, :3] = np.asarray(rotation, dtype=np.float64)
        matrix[:3, 3] = np.asarray(translation, dtype=np.float64).reshape(3)
        return cls(matrix=matrix, source=source, target=target, method=method, confidence=confidence)

    @property
    def rotation(self) -> np.ndarray:
        return self.matrix[:3, :3]

    @property
    def translation(self) -> np.ndarray:
        return self.matrix[:3, 3]

    def inverse(self) -> "Transform":
        inv = np.linalg.inv(self.matrix)
        return Transform(
            matrix=inv,
            source=self.target,
            target=self.source,
            method=f"inverse({self.method})",
            confidence=self.confidence,
            metadata=dict(self.metadata),
        )

    def compose(self, other: "Transform") -> "Transform":
        """Return the transform ``self`` applied after ``other`` (self.matrix @ other.matrix).

        Requires ``other.target == self.source``.
        """
        if other.target != self.source:
            raise ValueError(
                f"Cannot compose transform {other.source}->{other.target} with "
                f"{self.source}->{self.target}: target/source mismatch"
            )
        return Transform(
            matrix=self.matrix @ other.matrix,
            source=other.source,
            target=self.target,
            method=f"{self.method}∘{other.method}",
            confidence=min(self.confidence, other.confidence),
        )

    def apply(self, points: np.ndarray) -> np.ndarray:
        """Apply this transform to an (N, 3) array of points."""
        points = np.asarray(points, dtype=np.float64)
        single = points.ndim == 1
        if single:
            points = points[None, :]
        homogeneous = np.hstack([points, np.ones((points.shape[0], 1))])
        transformed = (self.matrix @ homogeneous.T).T[:, :3]
        return transformed[0] if single else transformed

    def apply_vector(self, vectors: np.ndarray) -> np.ndarray:
        """Apply only the rotation part (for directions/normals)."""
        vectors = np.asarray(vectors, dtype=np.float64)
        single = vectors.ndim == 1
        if single:
            vectors = vectors[None, :]
        transformed = (self.rotation @ vectors.T).T
        return transformed[0] if single else transformed

    def to_dict(self) -> dict:
        return {
            "matrix": self.matrix.tolist(),
            "source": self.source.value,
            "target": self.target.value,
            "method": self.method,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transform":
        return cls(
            matrix=np.array(data["matrix"]),
            source=CoordinateSystem(data["source"]),
            target=CoordinateSystem(data["target"]),
            method=data.get("method", "unknown"),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )
