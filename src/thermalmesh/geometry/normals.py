"""Normal computation for meshes and point clouds."""

from __future__ import annotations

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from thermalmesh.models.mesh import MeshData
from thermalmesh.models.pointcloud import PointCloudData


def compute_mesh_normals(mesh: MeshData) -> np.ndarray:
    """Angle-weighted vertex normals via trimesh."""
    tm = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=False)
    return np.asarray(tm.vertex_normals, dtype=np.float64)


def estimate_point_cloud_normals(cloud: PointCloudData, k: int = 16) -> np.ndarray:
    """Estimate normals via local PCA over the k nearest neighbors.

    Orientation is resolved by pointing every normal away from the cloud
    centroid, which is adequate for roughly convex/closed acquisition scans.
    """
    points = cloud.points
    n = points.shape[0]
    k = min(k, max(n - 1, 1))
    tree = cKDTree(points)
    _, neighbor_idx = tree.query(points, k=k + 1)
    centroid = points.mean(axis=0)

    normals = np.zeros_like(points)
    for i in range(n):
        neighbors = points[neighbor_idx[i]]
        centered = neighbors - neighbors.mean(axis=0)
        cov = centered.T @ centered
        eigvals, eigvecs = np.linalg.eigh(cov)
        normal = eigvecs[:, 0]  # eigenvector for smallest eigenvalue
        if np.dot(normal, points[i] - centroid) < 0:
            normal = -normal
        normals[i] = normal
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return normals / norms
