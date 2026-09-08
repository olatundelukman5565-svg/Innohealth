"""Mesh and registration quality diagnostics."""

from __future__ import annotations

import numpy as np

from thermalmesh.geometry.alignment import AlignmentDiagnostics
from thermalmesh.models.mesh import MeshData


def mesh_quality_metrics(mesh: MeshData) -> dict:
    lo, hi = mesh.bounding_box
    metrics = {
        "num_vertices": mesh.num_vertices,
        "num_faces": mesh.num_faces,
        "bounding_box_min": lo.tolist(),
        "bounding_box_max": hi.tolist(),
        "dimensions": mesh.dimensions.tolist(),
        "centroid": mesh.centroid.tolist(),
        "is_valid": mesh.is_valid(),
    }
    if mesh.num_faces:
        v0, v1, v2 = mesh.vertices[mesh.faces[:, 0]], mesh.vertices[mesh.faces[:, 1]], mesh.vertices[mesh.faces[:, 2]]
        areas = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)
        metrics["surface_area"] = float(areas.sum())
        metrics["degenerate_faces"] = int(np.sum(areas < 1e-12))
    return metrics


def registration_quality_metrics(diagnostics: AlignmentDiagnostics) -> dict:
    return diagnostics.to_dict()
