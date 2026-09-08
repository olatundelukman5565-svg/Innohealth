"""Camera intrinsic/extrinsic data models."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Camera:
    """A thermal camera: intrinsics plus whatever pose information is known."""

    camera_id: str
    image_width: int
    image_height: int
    intrinsic_matrix: np.ndarray  # 3x3
    distortion_coefficients: np.ndarray | None = None
    position: np.ndarray | None = None  # known camera location, world space (may be None)
    rotation: np.ndarray | None = None  # known camera orientation, 3x3 (may be None)
    pose_source: str = "unknown"  # "provided" | "estimated" | "initialized" | "unknown"
    intrinsics_source: str = "unknown"  # "provided" | "estimated_fallback"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.intrinsic_matrix = np.asarray(self.intrinsic_matrix, dtype=np.float64)
        if self.intrinsic_matrix.shape != (3, 3):
            raise ValueError(f"intrinsic_matrix must be 3x3, got {self.intrinsic_matrix.shape}")
        if self.distortion_coefficients is not None:
            self.distortion_coefficients = np.asarray(self.distortion_coefficients, dtype=np.float64)
        if self.position is not None:
            self.position = np.asarray(self.position, dtype=np.float64).reshape(3)
        if self.rotation is not None:
            self.rotation = np.asarray(self.rotation, dtype=np.float64).reshape(3, 3)

    @property
    def fx(self) -> float:
        return float(self.intrinsic_matrix[0, 0])

    @property
    def fy(self) -> float:
        return float(self.intrinsic_matrix[1, 1])

    @property
    def cx(self) -> float:
        return float(self.intrinsic_matrix[0, 2])

    @property
    def cy(self) -> float:
        return float(self.intrinsic_matrix[1, 2])

    def has_full_pose(self) -> bool:
        return self.position is not None and self.rotation is not None

    def extrinsic_matrix(self) -> np.ndarray:
        """4x4 world-to-camera matrix built from rotation/position (camera-to-world convention:
        position is the camera center in world space, rotation maps world axes to camera axes)."""
        if not self.has_full_pose():
            raise ValueError(f"Camera {self.camera_id} does not have a full pose yet")
        matrix = np.eye(4)
        matrix[:3, :3] = self.rotation
        matrix[:3, 3] = -self.rotation @ self.position
        return matrix


@dataclass
class CameraPose:
    """The result of pose initialization/estimation/refinement for one camera."""

    camera_id: str
    rotation: np.ndarray  # 3x3, world-to-camera
    translation: np.ndarray  # 3, world-to-camera
    confidence: float = 0.0
    reprojection_error: float | None = None
    estimation_method: str = "unknown"  # "provided" | "look_at_init" | "pnp" | "refined_optimization"
    iterations: int = 0
    converged: bool = False
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rotation = np.asarray(self.rotation, dtype=np.float64).reshape(3, 3)
        self.translation = np.asarray(self.translation, dtype=np.float64).reshape(3)

    @property
    def transformation_matrix(self) -> np.ndarray:
        """4x4 world-to-camera matrix."""
        matrix = np.eye(4)
        matrix[:3, :3] = self.rotation
        matrix[:3, 3] = self.translation
        return matrix

    @property
    def camera_center(self) -> np.ndarray:
        """Camera position in world coordinates."""
        return -self.rotation.T @ self.translation

    def to_dict(self) -> dict:
        return {
            "camera_id": self.camera_id,
            "rotation": self.rotation.tolist(),
            "translation": self.translation.tolist(),
            "camera_center": self.camera_center.tolist(),
            "confidence": self.confidence,
            "reprojection_error": self.reprojection_error,
            "estimation_method": self.estimation_method,
            "iterations": self.iterations,
            "converged": self.converged,
            "metadata": self.metadata,
        }
