"""UV coordinate validation and quality metrics."""

from __future__ import annotations

import numpy as np

from thermalmesh.models.mesh import MeshData


def validate_uvs(mesh: MeshData) -> dict:
    if mesh.uv_coordinates is None:
        return {"valid": False, "reason": "No UV coordinates present"}

    uv = mesh.uv_coordinates
    finite = np.all(np.isfinite(uv))
    in_range = bool(np.all(uv >= -1e-6) and np.all(uv <= 1 + 1e-6))

    degenerate_faces = 0
    if mesh.num_faces:
        tri_uv = uv[mesh.faces]
        areas = 0.5 * np.abs(
            (tri_uv[:, 1, 0] - tri_uv[:, 0, 0]) * (tri_uv[:, 2, 1] - tri_uv[:, 0, 1])
            - (tri_uv[:, 2, 0] - tri_uv[:, 0, 0]) * (tri_uv[:, 1, 1] - tri_uv[:, 0, 1])
        )
        degenerate_faces = int(np.sum(areas < 1e-9))
        total_uv_area = float(areas.sum())
    else:
        total_uv_area = 0.0

    return {
        "valid": bool(finite and in_range),
        "finite": bool(finite),
        "in_unit_range": in_range,
        "degenerate_faces": degenerate_faces,
        "total_uv_area": total_uv_area,
        "method": mesh.metadata.get("uv_method", "unknown"),
    }
