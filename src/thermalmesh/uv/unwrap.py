"""Automatic UV generation.

Uses ``xatlas`` (a robust, widely used automatic atlas/unwrap library) when
available. ``xatlas`` may duplicate vertices along UV seams, so this module
remaps every per-vertex attribute (normals, temperatures) onto the new
vertex indexing it produces.

If ``xatlas`` is not installed, a spherical-projection fallback is used
instead -- it does not split vertices (no seam duplication) but produces
lower-quality UVs with pole distortion; this is flagged in the mesh
metadata so it is never mistaken for the primary method.
"""

from __future__ import annotations

import numpy as np

from thermalmesh.models.mesh import MeshData
from thermalmesh.pipeline.errors import UVGenerationError

try:
    import xatlas  # type: ignore

    _HAS_XATLAS = True
except ImportError:  # pragma: no cover - optional dependency
    _HAS_XATLAS = False


def generate_uvs(mesh: MeshData, *, resolution: int = 2048) -> MeshData:
    if mesh.num_faces == 0:
        raise UVGenerationError(
            "Cannot generate UVs for a mesh with no faces",
            reason="UV unwrapping requires triangle connectivity",
            recommendation="Ensure the input mesh has valid face data",
        )
    if _HAS_XATLAS:
        return _generate_uvs_xatlas(mesh, resolution)
    return _generate_uvs_spherical_fallback(mesh, resolution)


def _remap_attribute(attribute: np.ndarray | None, vmapping: np.ndarray) -> np.ndarray | None:
    return None if attribute is None else attribute[vmapping]


def _generate_uvs_xatlas(mesh: MeshData, resolution: int) -> MeshData:
    vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

    result = MeshData(
        vertices=mesh.vertices[vmapping],
        faces=indices.astype(np.int64),
        normals=_remap_attribute(mesh.normals, vmapping),
        colors=_remap_attribute(mesh.colors, vmapping),
        uv_coordinates=np.asarray(uvs, dtype=np.float64),
        vertex_temperatures=_remap_attribute(mesh.vertex_temperatures, vmapping),
        coordinate_system=mesh.coordinate_system,
        metadata={**mesh.metadata, "uv_method": "xatlas", "uv_resolution": resolution,
                  "uv_vertex_mapping": vmapping.tolist()},
    )
    return result


def _generate_uvs_spherical_fallback(mesh: MeshData, resolution: int) -> MeshData:
    centered = mesh.vertices - mesh.centroid
    radius = np.linalg.norm(centered, axis=1)
    radius[radius == 0] = 1e-9
    normalized = centered / radius[:, None]

    u = 0.5 + np.arctan2(normalized[:, 0], normalized[:, 2]) / (2 * np.pi)
    v = 0.5 - np.arcsin(np.clip(normalized[:, 1], -1.0, 1.0)) / np.pi
    uvs = np.stack([u, v], axis=1)

    result = mesh.copy()
    result.uv_coordinates = uvs
    result.metadata["uv_method"] = "spherical_projection_fallback"
    result.metadata["uv_resolution"] = resolution
    result.metadata["uv_warning"] = "xatlas not installed; using lower-quality spherical projection UVs"
    return result
