"""Camera intrinsic matrix helpers."""

from __future__ import annotations

import numpy as np

from thermalmesh.models.camera import Camera
from thermalmesh.pipeline.errors import InvalidCameraDataError


def build_intrinsic_matrix(fx: float, fy: float, cx: float, cy: float) -> np.ndarray:
    return np.array([[fx, 0.0, cx], [0.0, fy, cy], [0.0, 0.0, 1.0]], dtype=np.float64)


def validate_intrinsics(camera: Camera) -> None:
    if camera.fx <= 0 or camera.fy <= 0:
        raise InvalidCameraDataError(
            f"Camera {camera.camera_id} has non-positive focal length",
            source=camera.camera_id, reason="fx/fy must be > 0",
            recommendation="Correct the intrinsics in camera metadata",
        )
    if not (0 <= camera.cx <= camera.image_width and 0 <= camera.cy <= camera.image_height):
        raise InvalidCameraDataError(
            f"Camera {camera.camera_id} principal point is outside the image bounds",
            source=camera.camera_id, reason=f"cx={camera.cx}, cy={camera.cy} vs "
            f"image ({camera.image_width}x{camera.image_height})",
            recommendation="Correct cx/cy or image dimensions",
        )


def distortion_vector(camera: Camera) -> np.ndarray:
    if camera.distortion_coefficients is not None:
        return camera.distortion_coefficients.astype(np.float64)
    return np.zeros(5, dtype=np.float64)
