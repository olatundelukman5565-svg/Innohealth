"""Project a single thermal image onto mesh geometry.

Each image is processed independently and produces its own
:class:`ProjectionResult` plus a list of :class:`TemperatureObservation` --
images are never blended at this stage (section 18).
"""

from __future__ import annotations

import numpy as np
import trimesh

from thermalmesh.camera.projection import project_points
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.projection import ProjectionResult, TemperatureObservation, Visibility
from thermalmesh.models.thermal import ThermalImage
from thermalmesh.thermal.occlusion import compute_visibility
from thermalmesh.thermal.sampling import sample_temperature


def project_thermal_image(
    mesh: MeshData,
    trimesh_mesh: trimesh.Trimesh,
    image: ThermalImage,
    camera: Camera,
    pose: CameraPose,
    *,
    occlusion_check: bool = True,
    sampling_method: str = "bilinear",
) -> tuple[ProjectionResult, list[TemperatureObservation]]:
    if mesh.normals is None:
        raise ValueError("Mesh normals are required for thermal projection; run geometry preprocessing first")

    visibility, occlusion_mask, distances, viewing_angle = compute_visibility(
        trimesh_mesh, mesh.vertices, mesh.normals, camera, pose, occlusion_check=occlusion_check
    )
    pixels, _depths, _in_front = project_points(mesh.vertices, camera, pose)

    candidate_idx = np.nonzero(visibility == Visibility.VISIBLE)[0]
    observations: list[TemperatureObservation] = []

    visible_geometry: list[int] = []
    projected_pixels: list[np.ndarray] = []
    temperatures: list[float] = []
    confidence_values: list[float] = []

    if candidate_idx.size:
        sampled_temps, sample_valid = sample_temperature(image, pixels[candidate_idx], method=sampling_method)
        for local_i, vertex_idx in enumerate(candidate_idx):
            if not sample_valid[local_i]:
                visibility[vertex_idx] = Visibility.INVALID
                continue
            distance = float(distances[vertex_idx])
            angle = float(viewing_angle[vertex_idx])
            angle_weight = max(np.cos(angle), 0.0)
            distance_weight = 1.0 / (1.0 + distance)
            confidence = float(np.clip(angle_weight * distance_weight, 0.0, 1.0))

            observations.append(
                TemperatureObservation(
                    image_id=image.image_id,
                    geometry_id=int(vertex_idx),
                    temperature=float(sampled_temps[local_i]),
                    pixel_x=float(pixels[vertex_idx, 0]),
                    pixel_y=float(pixels[vertex_idx, 1]),
                    visibility=Visibility.VISIBLE,
                    camera_distance=distance,
                    viewing_angle=angle,
                    confidence=confidence,
                    reprojection_error=pose.reprojection_error,
                    occlusion=False,
                )
            )
            visible_geometry.append(int(vertex_idx))
            projected_pixels.append(pixels[vertex_idx])
            temperatures.append(float(sampled_temps[local_i]))
            confidence_values.append(confidence)

    result = ProjectionResult(
        image_id=image.image_id,
        visible_geometry=np.array(visible_geometry, dtype=np.int64),
        projected_pixels=np.array(projected_pixels, dtype=np.float64) if projected_pixels else np.zeros((0, 2)),
        temperatures=np.array(temperatures, dtype=np.float64),
        confidence_map=np.array(confidence_values, dtype=np.float64),
        visibility_mask=visibility,
        occlusion_mask=occlusion_mask,
        metadata={
            "num_visible": len(visible_geometry),
            "num_occluded": int(occlusion_mask.sum()),
            "num_outside_image": int(np.sum(visibility == Visibility.OUTSIDE_IMAGE)),
            "num_back_facing": int(np.sum(visibility == Visibility.BACK_FACING)),
        },
    )
    return result, observations
