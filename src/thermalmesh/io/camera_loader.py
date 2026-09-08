"""Loading camera metadata (intrinsics, and whatever pose info is known).

Expected JSON schema (see examples/sample_camera.json)::

    {
      "cameras": [
        {
          "camera_id": "cam_01",
          "image_width": 640,
          "image_height": 480,
          "intrinsics": {"fx": 525.0, "fy": 525.0, "cx": 320.0, "cy": 240.0},
          "distortion": [0.0, 0.0, 0.0, 0.0, 0.0],
          "position": [1.2, 0.0, 0.5],
          "rotation": [[...], [...], [...]],
          "thermal_file": "thermal_01.csv"
        }
      ]
    }

``position``/``rotation``/``distortion`` are optional. Missing intrinsics
are never fabricated: if absent, a configurable fallback estimate is used
and the camera's ``intrinsics_source`` is marked ``"estimated_fallback"``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from thermalmesh.models.camera import Camera
from thermalmesh.pipeline.errors import InvalidCameraDataError


def load_cameras(path: str | Path, *, default_fov_degrees: float = 50.0) -> dict[str, Camera]:
    path = Path(path)
    if not path.exists():
        raise InvalidCameraDataError(
            f"Camera metadata file not found: {path}",
            source=str(path), reason="File does not exist",
            recommendation="Verify --cameras path",
        )
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise InvalidCameraDataError(
            f"Camera metadata file {path} is not valid JSON",
            source=str(path), reason=str(exc),
            recommendation="Validate the JSON syntax of the camera file",
        ) from exc

    entries = data.get("cameras")
    if not entries:
        raise InvalidCameraDataError(
            f"Camera metadata file {path} has no 'cameras' entries",
            source=str(path), reason="Missing or empty 'cameras' list",
            recommendation="Add at least one camera entry",
        )

    cameras: dict[str, Camera] = {}
    for i, entry in enumerate(entries):
        camera_id = entry.get("camera_id", f"cam_{i:03d}")
        width = entry.get("image_width")
        height = entry.get("image_height")
        if not width or not height:
            raise InvalidCameraDataError(
                f"Camera '{camera_id}' in {path} is missing image_width/image_height",
                source=str(path), reason="Required fields absent",
                recommendation="Add image_width/image_height for every camera",
            )

        intrinsics_source = "provided"
        intrinsics = entry.get("intrinsics")
        if intrinsics:
            fx = intrinsics["fx"]
            fy = intrinsics.get("fy", fx)
            cx = intrinsics.get("cx", width / 2.0)
            cy = intrinsics.get("cy", height / 2.0)
        else:
            # Fallback estimate from a configurable field of view. Marked explicitly
            # as estimated so downstream diagnostics never treat it as ground truth.
            intrinsics_source = "estimated_fallback"
            focal = (width / 2.0) / np.tan(np.deg2rad(default_fov_degrees) / 2.0)
            fx = fy = focal
            cx, cy = width / 2.0, height / 2.0

        k_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
        distortion = entry.get("distortion")
        position = entry.get("position")
        rotation = entry.get("rotation")

        pose_source = "provided" if (position is not None and rotation is not None) else (
            "position_only" if position is not None else "unknown"
        )

        cameras[camera_id] = Camera(
            camera_id=camera_id,
            image_width=int(width),
            image_height=int(height),
            intrinsic_matrix=k_matrix,
            distortion_coefficients=distortion,
            position=position,
            rotation=rotation,
            pose_source=pose_source,
            intrinsics_source=intrinsics_source,
            metadata={"thermal_file": entry.get("thermal_file")},
        )
    return cameras
