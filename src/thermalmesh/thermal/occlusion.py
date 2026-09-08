"""Visibility / occlusion analysis via ray casting.

For each geometry sample, a ray is cast from the surface toward the camera
and tested against the mesh itself; if something else along that ray is
struck first, the sample is OCCLUDED. Back-facing samples (surface normal
pointing away from the camera) are rejected before ray casting. This
prevents assigning background/occluded-surface temperatures to hidden
geometry (Rule / section 19).
"""

from __future__ import annotations

import numpy as np
import trimesh

from thermalmesh.camera.projection import in_image_bounds, project_points
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.projection import Visibility

_RAY_OFFSET = 1e-4  # fraction of scene scale, offsets ray origin along the normal to avoid self-hits


def compute_visibility(
    mesh: trimesh.Trimesh,
    points_world: np.ndarray,
    normals_world: np.ndarray,
    camera: Camera,
    pose: CameraPose,
    *,
    occlusion_check: bool = True,
    scene_scale: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(visibility, occlusion_mask, camera_distance, viewing_angle)`` arrays,
    one entry per input point."""
    n = points_world.shape[0]
    visibility = np.full(n, Visibility.INVALID, dtype=object)
    occlusion_mask = np.zeros(n, dtype=bool)
    camera_center = pose.camera_center
    view_vectors = camera_center[None, :] - points_world
    distances = np.linalg.norm(view_vectors, axis=1)
    safe_distances = np.where(distances > 1e-12, distances, 1.0)
    view_dirs = view_vectors / safe_distances[:, None]

    cos_angle = np.einsum("ij,ij->i", normals_world, view_dirs)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    viewing_angle = np.arccos(cos_angle)

    front_facing = cos_angle > 0
    visibility[~front_facing] = Visibility.BACK_FACING

    pixels, depths, in_front = project_points(points_world, camera, pose)
    in_bounds = in_front & in_image_bounds(pixels, camera.image_width, camera.image_height)
    candidate = front_facing & in_bounds
    visibility[front_facing & ~in_bounds] = Visibility.OUTSIDE_IMAGE

    if candidate.any():
        if occlusion_check:
            scale = scene_scale if scene_scale else float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))
            offset = _RAY_OFFSET * max(scale, 1e-6)
            idx = np.nonzero(candidate)[0]
            origins = points_world[idx] + normals_world[idx] * offset
            directions = view_dirs[idx]

            locations, index_ray, _ = mesh.ray.intersects_location(
                ray_origins=origins, ray_directions=directions, multiple_hits=False
            )
            hit_distance = np.full(idx.shape[0], np.inf)
            if len(index_ray):
                hit_distance[index_ray] = np.linalg.norm(locations - origins[index_ray], axis=1)

            occluded_local = hit_distance < (distances[idx] - offset - 1e-6)
            occlusion_mask[idx[occluded_local]] = True
            visibility[idx[occluded_local]] = Visibility.OCCLUDED
            visibility[idx[~occluded_local]] = Visibility.VISIBLE
        else:
            visibility[candidate] = Visibility.VISIBLE

    return visibility, occlusion_mask, distances, viewing_angle
