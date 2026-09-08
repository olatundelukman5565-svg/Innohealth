"""Automatic camera pose estimation.

Two methods are provided:

- ``estimate_pose_pnp``: classic PnP when explicit 3D<->2D correspondences
  are available (e.g. calibration markers).
- ``estimate_camera_pose``: the default, correspondence-free method used
  when only raw thermal arrays are available. It segments the thermal
  foreground and applies a coarse silhouette-bbox correction (translate
  along the viewing axis to match apparent scale, shift laterally to match
  bbox center) on top of the initial pose.
"""

from __future__ import annotations

import cv2
import numpy as np

from thermalmesh.camera.diagnostics import mask_bbox, mask_iou, render_silhouette_mask, segment_thermal_foreground
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.thermal import ThermalImage
from thermalmesh.pipeline.errors import PoseEstimationError


def estimate_pose_pnp(
    camera: Camera,
    world_points: np.ndarray,
    image_points: np.ndarray,
    *,
    initial_pose: CameraPose | None = None,
) -> CameraPose:
    """Estimate pose from known 3D<->2D correspondences via ``cv2.solvePnP``."""
    world_points = np.asarray(world_points, dtype=np.float64)
    image_points = np.asarray(image_points, dtype=np.float64)
    if world_points.shape[0] < 4:
        raise PoseEstimationError(
            f"PnP requires at least 4 correspondences for camera '{camera.camera_id}', got {world_points.shape[0]}",
            source=camera.camera_id, reason="Insufficient correspondences",
            recommendation="Provide more 3D<->2D correspondences or use the correspondence-free estimator",
        )
    distortion = camera.distortion_coefficients if camera.distortion_coefficients is not None else np.zeros(5)

    rvec0 = tvec0 = None
    use_extrinsic_guess = False
    if initial_pose is not None:
        rvec0, _ = cv2.Rodrigues(initial_pose.rotation)
        tvec0 = initial_pose.translation.reshape(3, 1)
        use_extrinsic_guess = True

    ok, rvec, tvec = cv2.solvePnP(
        world_points, image_points, camera.intrinsic_matrix, distortion,
        rvec=rvec0, tvec=tvec0, useExtrinsicGuess=use_extrinsic_guess,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not ok:
        raise PoseEstimationError(
            f"cv2.solvePnP failed to converge for camera '{camera.camera_id}'",
            source=camera.camera_id, reason="Degenerate or insufficient correspondences",
            recommendation="Check correspondence quality/spread",
        )

    rotation, _ = cv2.Rodrigues(rvec)
    projected, _ = cv2.projectPoints(world_points, rvec, tvec, camera.intrinsic_matrix, distortion)
    reprojection_error = float(np.mean(np.linalg.norm(projected.reshape(-1, 2) - image_points, axis=1)))

    return CameraPose(
        camera_id=camera.camera_id,
        rotation=rotation,
        translation=tvec.reshape(3),
        confidence=float(np.clip(1.0 / (1.0 + reprojection_error), 0.0, 1.0)),
        reprojection_error=reprojection_error,
        estimation_method="pnp",
    )


def estimate_camera_pose(
    camera: Camera,
    mesh: MeshData,
    thermal_image: ThermalImage,
    initial_pose: CameraPose,
    *,
    downsample: int = 4,
) -> CameraPose:
    """Correspondence-free coarse pose estimation via thermal-silhouette matching."""
    foreground = segment_thermal_foreground(thermal_image)
    foreground_small = cv2.resize(
        foreground.astype(np.uint8),
        (max(1, camera.image_width // downsample), max(1, camera.image_height // downsample)),
        interpolation=cv2.INTER_NEAREST,
    ).astype(bool)

    rendered = render_silhouette_mask(mesh.vertices, camera, initial_pose, downsample=downsample)
    iou_before = mask_iou(rendered, foreground_small)

    thermal_bbox = mask_bbox(foreground_small)
    render_bbox = mask_bbox(rendered)

    rotation = initial_pose.rotation
    translation = initial_pose.translation.copy()
    method = "silhouette_bbox_estimation"
    notes = {}

    if thermal_bbox is None or render_bbox is None:
        notes["warning"] = "Could not extract a silhouette bounding box; keeping initial pose"
    else:
        tx0, ty0, tx1, ty1 = thermal_bbox
        rx0, ry0, rx1, ry1 = render_bbox
        thermal_size = max(tx1 - tx0, ty1 - ty0, 1e-6)
        render_size = max(rx1 - rx0, ry1 - ry0, 1e-6)
        scale_correction = render_size / thermal_size  # >1 means rendered too big -> move camera back

        # Forward direction of the camera in world space (points from the camera toward the scene).
        forward_world = rotation.T @ np.array([0.0, 0.0, 1.0])
        camera_center = -rotation.T @ translation
        depth_estimate = float(np.linalg.norm(mesh.centroid - camera_center))
        # A too-big render (scale_correction > 1) means the camera is too close and must
        # retreat *away* from the scene, i.e. against forward_world.
        depth_adjustment = depth_estimate * (scale_correction - 1.0)
        new_center = camera_center - forward_world * depth_adjustment

        # Lateral correction: shift so projected bbox center matches thermal bbox center.
        # Moving the camera by +delta along an axis shifts the projected image content by
        # -fx*delta/depth along the corresponding pixel axis, so the required camera shift
        # is the negative of the desired pixel shift (scaled back into world units).
        thermal_center = np.array([(tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0])
        render_center = np.array([(rx0 + rx1) / 2.0, (ry0 + ry1) / 2.0])
        pixel_shift = (thermal_center - render_center) * downsample
        right_world = rotation.T @ np.array([1.0, 0.0, 0.0])
        down_world = rotation.T @ np.array([0.0, 1.0, 0.0])
        lateral_shift = (
            right_world * (pixel_shift[0] / camera.fx) * depth_estimate
            + down_world * (pixel_shift[1] / camera.fy) * depth_estimate
        )
        new_center = new_center - lateral_shift
        translation = -rotation @ new_center
        notes["scale_correction"] = scale_correction
        notes["pixel_shift"] = pixel_shift.tolist()

    candidate = CameraPose(
        camera_id=camera.camera_id, rotation=rotation, translation=translation,
        confidence=initial_pose.confidence, estimation_method=method, metadata=notes,
    )
    rendered_after = render_silhouette_mask(mesh.vertices, camera, candidate, downsample=downsample)
    iou_after = mask_iou(rendered_after, foreground_small)
    candidate.confidence = float(np.clip(iou_after, 0.0, 1.0))
    candidate.metadata["silhouette_iou_before"] = iou_before
    candidate.metadata["silhouette_iou_after"] = iou_after
    return candidate
