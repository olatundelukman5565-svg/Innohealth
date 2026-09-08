"""Map blended vertex temperatures onto faces and (optionally) a point cloud."""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

from thermalmesh.models.mesh import MeshData
from thermalmesh.models.pointcloud import PointCloudData


def map_vertex_to_face_temperature(mesh: MeshData, vertex_temperatures: np.ndarray) -> np.ndarray:
    """Face temperature = mean of its vertices' temperatures (NaN if any vertex is unobserved)."""
    if mesh.faces.size == 0:
        return np.zeros(0)
    face_vertex_temps = vertex_temperatures[mesh.faces]  # (num_faces, 3)
    with np.errstate(invalid="ignore"):
        return np.nanmean(face_vertex_temps, axis=1)


def map_mesh_to_point_cloud_temperature(
    cloud: PointCloudData, mesh_vertices_in_cloud_space: np.ndarray, vertex_temperatures: np.ndarray
) -> np.ndarray:
    """Transfer temperature to point-cloud points via nearest-vertex lookup.

    ``mesh_vertices_in_cloud_space`` must already be expressed in the same
    coordinate system as ``cloud.points`` (apply the inverse alignment
    transform first).
    """
    tree = cKDTree(mesh_vertices_in_cloud_space)
    _, nearest_vertex = tree.query(cloud.points)
    return vertex_temperatures[nearest_vertex]
