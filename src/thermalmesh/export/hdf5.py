"""HDF5 numerical export with logical groups (/mesh, /cameras, /thermal, /results)."""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

from thermalmesh.models.camera import CameraPose
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.thermal import ThermalImage


def export_hdf5(
    output_path: str | Path,
    *,
    mesh: MeshData,
    camera_poses: dict[str, CameraPose],
    thermal_images: dict[str, ThermalImage],
    vertex_temperature: np.ndarray,
    face_temperature: np.ndarray | None = None,
    point_temperature: np.ndarray | None = None,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(output_path, "w") as f:
        mesh_group = f.create_group("mesh")
        mesh_group.create_dataset("vertices", data=mesh.vertices)
        mesh_group.create_dataset("faces", data=mesh.faces)
        if mesh.uv_coordinates is not None:
            mesh_group.create_dataset("uv", data=mesh.uv_coordinates)

        cameras_group = f.create_group("cameras")
        poses_group = cameras_group.create_group("poses")
        for camera_id, pose in camera_poses.items():
            cam_group = poses_group.create_group(camera_id)
            cam_group.create_dataset("rotation", data=pose.rotation)
            cam_group.create_dataset("translation", data=pose.translation)
            cam_group.attrs["confidence"] = pose.confidence
            cam_group.attrs["estimation_method"] = pose.estimation_method

        thermal_group = f.create_group("thermal")
        images_group = thermal_group.create_group("images")
        for image_id, image in thermal_images.items():
            img_group = images_group.create_group(image_id)
            img_group.create_dataset("temperature", data=image.temperature_array, compression="gzip")
            img_group.create_dataset("validity_mask", data=image.validity_mask, compression="gzip")

        results_group = f.create_group("results")
        results_group.create_dataset("vertex_temperature", data=np.nan_to_num(vertex_temperature, nan=np.nan))
        if face_temperature is not None:
            results_group.create_dataset("face_temperature", data=face_temperature)
        if point_temperature is not None:
            results_group.create_dataset("point_temperature", data=point_temperature)

    return output_path
