"""Synthetic validation dataset generator.

Produces a known 3D mesh, a known initial-acquisition point cloud (related
to the final mesh by a known rigid transform), a known analytic temperature
field, and ``num_views`` rendered thermal images from cameras with known
(but not given to the pipeline) intrinsics/poses.

Because ground truth is known, this lets engineering validate the pipeline's
math end-to-end. It does NOT validate the pipeline against Innohealth's
actual thermal signatures, camera hardware, or acquisition geometry -- see
docs/development.md for the real-data validation checklist.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import trimesh

from thermalmesh.camera.extrinsics import look_at_rotation, world_to_camera_translation
from thermalmesh.models.camera import Camera, CameraPose


def known_temperature_field(vertices: np.ndarray, base: float = 36.0, coeffs: tuple[float, float, float] = (2.0, 1.0, 0.5)) -> np.ndarray:
    """A deterministic spatial temperature function used as ground truth."""
    ax, ay, az = coeffs
    return base + ax * vertices[:, 0] + ay * vertices[:, 1] + az * vertices[:, 2]


def _camera_positions(num_views: int, radius: float, height: float, rng: np.random.Generator) -> np.ndarray:
    angles = np.linspace(0, 2 * np.pi, num_views, endpoint=False)
    angles = angles + rng.uniform(-0.05, 0.05, size=num_views)
    xs = radius * np.cos(angles)
    zs = radius * np.sin(angles)
    ys = np.full(num_views, height) + rng.uniform(-0.1, 0.1, size=num_views)
    return np.stack([xs, ys, zs], axis=1)


def generate_synthetic_dataset(
    output_dir: str | Path,
    *,
    num_views: int = 12,
    image_width: int = 160,
    image_height: int = 120,
    subdivisions: int = 2,
    radius_factor: float = 3.0,
    noise_std: float = 0.15,
    background_temperature: float = 20.0,
    seed: int = 0,
) -> dict:
    output_dir = Path(output_dir)
    thermal_dir = output_dir / "thermal"
    thermal_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    # 1. Known geometry: an icosphere is a reasonable stand-in for a roughly
    # convex scanned object and keeps ray casting fast.
    sphere = trimesh.creation.icosphere(subdivisions=subdivisions, radius=0.5)
    vertices = np.asarray(sphere.vertices, dtype=np.float64)
    faces = np.asarray(sphere.faces, dtype=np.int64)
    sphere.export(output_dir / "final_mesh.ply")

    # 2. Known analytic temperature field on the final mesh.
    vertex_temperatures = known_temperature_field(vertices)
    face_vertex_temps = vertex_temperatures[faces]

    # 3. Known rigid transform relating an "initial acquisition" point cloud
    # to the final mesh: final = R @ acquisition + t.
    angle = np.deg2rad(12.0)
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    known_rotation = np.array([[cos_a, 0, sin_a], [0, 1, 0], [-sin_a, 0, cos_a]])
    known_translation = np.array([0.04, -0.02, 0.03])
    acquisition_points = (known_rotation.T @ (vertices - known_translation).T).T
    acquisition_points += rng.normal(scale=0.002, size=acquisition_points.shape)
    trimesh.points.PointCloud(acquisition_points).export(output_dir / "initial_mesh.ply")

    # 4. Cameras placed on a ring around the object, looking at its centroid.
    bbox_diag = float(np.linalg.norm(vertices.max(axis=0) - vertices.min(axis=0)))
    radius = bbox_diag * radius_factor
    centroid = vertices.mean(axis=0)
    positions = _camera_positions(num_views, radius=radius, height=0.0, rng=rng) + centroid

    focal = (image_width / 2.0) / np.tan(np.deg2rad(50.0) / 2.0)
    intrinsic_matrix = np.array([[focal, 0, image_width / 2.0], [0, focal, image_height / 2.0], [0, 0, 1]])

    camera_entries = []
    ground_truth_cameras = {}

    for i, position in enumerate(positions):
        camera_id = f"cam_{i:02d}"
        rotation = look_at_rotation(position, centroid)
        translation = world_to_camera_translation(position, rotation)
        camera = Camera(
            camera_id=camera_id, image_width=image_width, image_height=image_height,
            intrinsic_matrix=intrinsic_matrix,
        )
        pose = CameraPose(camera_id=camera_id, rotation=rotation, translation=translation)

        thermal_array = _render_thermal_image(
            sphere, face_vertex_temps, camera, pose, background_temperature, noise_std, rng
        )
        thermal_path = thermal_dir / f"{camera_id}.csv"
        _write_csv(thermal_array, thermal_path)

        camera_entries.append({
            "camera_id": camera_id,
            "image_width": image_width,
            "image_height": image_height,
            "intrinsics": {"fx": focal, "fy": focal, "cx": image_width / 2.0, "cy": image_height / 2.0},
            "position": position.tolist(),
            # Orientation intentionally withheld: the pipeline must estimate it,
            # matching Innohealth's "camera location known, orientation not
            # guaranteed aligned" scenario.
            "thermal_file": f"{camera_id}.csv",
        })
        ground_truth_cameras[camera_id] = {"position": position.tolist(), "rotation": rotation.tolist(), "translation": translation.tolist()}

    cameras_payload = {"cameras": camera_entries}
    (output_dir / "cameras.json").write_text(json.dumps(cameras_payload, indent=2))

    ground_truth = {
        "vertex_temperatures": vertex_temperatures.tolist(),
        "alignment_rotation": known_rotation.tolist(),
        "alignment_translation": known_translation.tolist(),
        "cameras": ground_truth_cameras,
        "temperature_field": {"base": 36.0, "coeffs": [2.0, 1.0, 0.5]},
    }
    (output_dir / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2))
    return ground_truth


def _render_thermal_image(
    mesh: trimesh.Trimesh,
    face_vertex_temps: np.ndarray,
    camera: Camera,
    pose: CameraPose,
    background_temperature: float,
    noise_std: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Ray-cast one pixel per texel to render a physically-grounded synthetic thermal image."""
    xs, ys = np.meshgrid(np.arange(camera.image_width), np.arange(camera.image_height))
    pixels = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], axis=1)

    from thermalmesh.camera.projection import pixel_to_world_ray

    origin, directions = pixel_to_world_ray(camera, pose, pixels)
    origins = np.tile(origin, (pixels.shape[0], 1))

    locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=origins, ray_directions=directions, multiple_hits=False
    )

    image = np.full(pixels.shape[0], background_temperature)
    if len(index_ray):
        hit_faces = mesh.faces[index_tri]
        v0, v1, v2 = mesh.vertices[hit_faces[:, 0]], mesh.vertices[hit_faces[:, 1]], mesh.vertices[hit_faces[:, 2]]
        bary = trimesh.triangles.points_to_barycentric(np.stack([v0, v1, v2], axis=1), locations)
        temps = np.sum(bary * face_vertex_temps[index_tri], axis=1)
        image[index_ray] = temps

    image += rng.normal(scale=noise_std, size=image.shape)
    return image.reshape(camera.image_height, camera.image_width)


def _write_csv(array: np.ndarray, path: Path) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        for row in array:
            writer.writerow([f"{v:.4f}" for v in row])
