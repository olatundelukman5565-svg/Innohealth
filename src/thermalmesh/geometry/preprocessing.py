"""Mesh preprocessing: cleanup and optional simplification."""

from __future__ import annotations

import numpy as np
import trimesh

from thermalmesh.models.mesh import MeshData


def preprocess_mesh(mesh: MeshData, *, simplify: bool = False, target_faces: int | None = None) -> MeshData:
    """Remove degenerate/duplicate geometry and optionally simplify.

    Returns a new :class:`MeshData`; the input is left untouched.
    """
    tm = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=False)
    tm.remove_infinite_values()
    tm.update_faces(tm.nondegenerate_faces())
    tm.merge_vertices()

    if simplify and target_faces and tm.faces.shape[0] > target_faces:
        try:
            tm = tm.simplify_quadric_decimation(face_count=target_faces)
        except Exception:  # noqa: BLE001 - simplification is best-effort
            pass

    result = mesh.copy()
    result.vertices = np.asarray(tm.vertices, dtype=np.float64)
    result.faces = np.asarray(tm.faces, dtype=np.int64)
    result.normals = np.asarray(tm.vertex_normals, dtype=np.float64)
    result.uv_coordinates = None
    result.vertex_temperatures = None
    result.face_temperatures = None
    result.metadata = dict(mesh.metadata)
    result.metadata["preprocessing"] = {
        "simplified": bool(simplify and target_faces),
        "original_vertex_count": mesh.num_vertices,
        "original_face_count": mesh.num_faces,
        "final_vertex_count": result.num_vertices,
        "final_face_count": result.num_faces,
    }
    return result
