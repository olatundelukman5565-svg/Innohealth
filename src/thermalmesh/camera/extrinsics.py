"""Camera extrinsics helpers: world<->camera rigid transform construction."""

from __future__ import annotations

import numpy as np

from thermalmesh.models.camera import CameraPose
from thermalmesh.models.transforms import CoordinateSystem, Transform


def pose_to_transform(pose: CameraPose) -> Transform:
    """World -> camera transform for a given :class:`CameraPose`."""
    return Transform(
        matrix=pose.transformation_matrix,
        source=CoordinateSystem.WORLD,
        target=CoordinateSystem.CAMERA,
        method=pose.estimation_method,
        confidence=pose.confidence,
    )


def look_at_rotation(camera_position: np.ndarray, target: np.ndarray, up: np.ndarray = np.array([0.0, 1.0, 0.0])) -> np.ndarray:
    """World-to-camera rotation matrix for a camera at ``camera_position`` looking at ``target``.

    Uses a computer-vision camera convention: +Z looks toward the target,
    +X is right, +Y is down.
    """
    forward = target - camera_position
    norm = np.linalg.norm(forward)
    if norm < 1e-12:
        forward = np.array([0.0, 0.0, 1.0])
    else:
        forward = forward / norm

    if abs(np.dot(forward, up)) > 0.999:
        up = np.array([1.0, 0.0, 0.0])

    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    true_down = np.cross(forward, right)
    true_down /= np.linalg.norm(true_down)

    # rows are the camera's axes expressed in world coordinates -> world-to-camera rotation
    rotation = np.stack([right, true_down, forward], axis=0)
    return rotation


def world_to_camera_translation(camera_position: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    return -rotation @ camera_position
