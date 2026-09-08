"""Rasterize per-vertex scalar values (temperature, confidence, ...) into UV space.

Used both per thermal image (to build individual thermal UV layers, kept
separate per section 24) and once more for the final blended result.
"""

from __future__ import annotations

import numpy as np

from thermalmesh.models.mesh import MeshData


def rasterize_vertex_values_to_uv(
    mesh: MeshData,
    vertex_values: np.ndarray,
    vertex_valid: np.ndarray,
    resolution: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Barycentric-rasterize per-vertex values into a ``(resolution, resolution)`` texture.

    Returns ``(value_texture, valid_mask)``. Texels not covered by any valid
    triangle stay at 0 with ``valid_mask=False`` (never a fabricated value).
    """
    if mesh.uv_coordinates is None:
        raise ValueError("Mesh has no UV coordinates; run UV generation first")

    value_texture = np.zeros((resolution, resolution), dtype=np.float64)
    valid_mask = np.zeros((resolution, resolution), dtype=bool)

    uv = mesh.uv_coordinates
    px = uv[:, 0] * (resolution - 1)
    py = (1.0 - uv[:, 1]) * (resolution - 1)  # flip V so image row 0 is the top

    for face in mesh.faces:
        if not (vertex_valid[face[0]] and vertex_valid[face[1]] and vertex_valid[face[2]]):
            continue

        xs = px[face]
        ys = py[face]
        vals = vertex_values[face]

        min_x = max(int(np.floor(xs.min())), 0)
        max_x = min(int(np.ceil(xs.max())), resolution - 1)
        min_y = max(int(np.floor(ys.min())), 0)
        max_y = min(int(np.ceil(ys.max())), resolution - 1)
        if min_x > max_x or min_y > max_y:
            continue

        grid_x, grid_y = np.meshgrid(np.arange(min_x, max_x + 1), np.arange(min_y, max_y + 1))
        grid_x = grid_x.astype(np.float64) + 0.5
        grid_y = grid_y.astype(np.float64) + 0.5

        denom = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(denom) < 1e-12:
            continue

        w0 = ((ys[1] - ys[2]) * (grid_x - xs[2]) + (xs[2] - xs[1]) * (grid_y - ys[2])) / denom
        w1 = ((ys[2] - ys[0]) * (grid_x - xs[2]) + (xs[0] - xs[2]) * (grid_y - ys[2])) / denom
        w2 = 1.0 - w0 - w1

        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue

        interpolated = w0 * vals[0] + w1 * vals[1] + w2 * vals[2]
        sub_x = (np.arange(min_x, max_x + 1)[None, :] * np.ones_like(inside, dtype=int))
        sub_y = (np.arange(min_y, max_y + 1)[:, None] * np.ones_like(inside, dtype=int))

        value_texture[sub_y[inside], sub_x[inside]] = interpolated[inside]
        valid_mask[sub_y[inside], sub_x[inside]] = True

    return value_texture, valid_mask
