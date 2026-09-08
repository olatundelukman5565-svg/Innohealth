"""Camera pose refinement via local optimization.

Refines the 6 DOF pose (as a rotation-vector delta composed onto the
current rotation, plus a translation delta) to maximize silhouette overlap
between the rendered mesh and the segmented thermal foreground. Bounded,
iteration-limited, and reports convergence/objective diagnostics rather
than running unconstrained.
"""

from __future__ import annotations

import cv2
import numpy as np
from scipy.optimize import minimize

from thermalmesh.camera.diagnostics import mask_iou, render_silhouette_mask, segment_thermal_foreground
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.thermal import ThermalImage


def refine_camera_pose(
    camera: Camera,
    mesh: MeshData,
    thermal_image: ThermalImage,
    initial_pose: CameraPose,
    *,
    max_iterations: int = 60,
    downsample: int = 4,
    max_rotation_delta_deg: float = 15.0,
    max_translation_fraction: float = 0.25,
) -> CameraPose:
    """Refine ``initial_pose`` by maximizing rendered/thermal silhouette IoU."""
    foreground = segment_thermal_foreground(thermal_image)
    foreground_small = cv2.resize(
        foreground.astype(np.uint8),
        (max(1, camera.image_width // downsample), max(1, camera.image_height // downsample)),
        interpolation=cv2.INTER_NEAREST,
    ).astype(bool)

    if foreground_small.sum() == 0:
        return CameraPose(
            camera_id=camera.camera_id,
            rotation=initial_pose.rotation, translation=initial_pose.translation,
            confidence=0.0, estimation_method="refined_optimization",
            iterations=0, converged=False,
            metadata={"warning": "No thermal foreground detected; refinement skipped"},
        )

    base_rotation = initial_pose.rotation
    base_translation = initial_pose.translation
    scene_scale = float(np.linalg.norm(mesh.dimensions)) or 1.0
    max_translation = scene_scale * max_translation_fraction
    max_rotation_rad = np.deg2rad(max_rotation_delta_deg)

    def build_pose(params: np.ndarray) -> CameraPose:
        rvec_delta = params[:3]
        t_delta = params[3:]
        delta_rotation, _ = cv2.Rodrigues(rvec_delta)
        rotation = delta_rotation @ base_rotation
        translation = base_translation + t_delta
        return CameraPose(camera_id=camera.camera_id, rotation=rotation, translation=translation, confidence=0.0,
                           estimation_method="refined_optimization")

    iteration_count = 0

    def objective(params: np.ndarray) -> float:
        nonlocal iteration_count
        iteration_count += 1
        pose = build_pose(params)
        rendered = render_silhouette_mask(mesh.vertices, camera, pose, downsample=downsample)
        iou = mask_iou(rendered, foreground_small)
        return 1.0 - iou

    x0 = np.zeros(6)
    bounds = [(-max_rotation_rad, max_rotation_rad)] * 3 + [(-max_translation, max_translation)] * 3

    result = minimize(
        objective, x0, method="Powell", bounds=bounds,
        options={"maxiter": max_iterations, "xtol": 1e-3, "ftol": 1e-4},
    )

    final_pose = build_pose(result.x)
    rendered_final = render_silhouette_mask(mesh.vertices, camera, final_pose, downsample=downsample)
    final_iou = mask_iou(rendered_final, foreground_small)

    final_pose.confidence = float(np.clip(final_iou, 0.0, 1.0))
    final_pose.reprojection_error = float(1.0 - final_iou)
    final_pose.iterations = iteration_count
    final_pose.converged = bool(result.success)
    final_pose.metadata = {
        "objective": "1 - silhouette_iou",
        "initial_confidence": initial_pose.confidence,
        "final_silhouette_iou": final_iou,
    }
    return final_pose
