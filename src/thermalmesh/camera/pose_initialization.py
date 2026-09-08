"""Camera pose initialization.

Buyer data may provide a camera location without a complete orientation.
This module produces a best-effort INITIAL pose -- never treated as ground
truth (Rule 6) -- which later stages (pose estimation/refinement) improve.
"""

from __future__ import annotations

import numpy as np

from thermalmesh.camera.extrinsics import look_at_rotation, world_to_camera_translation
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.pipeline.errors import PoseEstimationError


def initialize_camera_pose(camera: Camera, target_centroid: np.ndarray, up: np.ndarray | None = None) -> CameraPose:
    """Initialize a :class:`CameraPose` for ``camera``.

    - If the camera already has a full provided pose, use it directly (method="provided").
    - If only a position is known, orient it via look-at toward ``target_centroid``
      (method="look_at_init"), marked with reduced confidence.
    - If neither is known, raise -- fabricating a camera location would
      silently invent data (Rule 6).
    """
    up = np.array([0.0, 1.0, 0.0]) if up is None else np.asarray(up, dtype=np.float64)

    if camera.has_full_pose():
        translation = world_to_camera_translation(camera.position, camera.rotation)
        return CameraPose(
            camera_id=camera.camera_id,
            rotation=camera.rotation,
            translation=translation,
            confidence=1.0,
            estimation_method="provided",
        )

    if camera.position is not None:
        rotation = look_at_rotation(camera.position, target_centroid, up)
        translation = world_to_camera_translation(camera.position, rotation)
        return CameraPose(
            camera_id=camera.camera_id,
            rotation=rotation,
            translation=translation,
            confidence=0.4,
            estimation_method="look_at_init",
            metadata={"note": "Orientation unknown; initialized via look-at toward geometry centroid."},
        )

    raise PoseEstimationError(
        f"Cannot initialize pose for camera '{camera.camera_id}': no position or orientation is known",
        source=camera.camera_id,
        reason="Camera metadata provided neither position nor rotation",
        recommendation="Provide at least an approximate camera position, or supply correspondences for PnP",
    )
