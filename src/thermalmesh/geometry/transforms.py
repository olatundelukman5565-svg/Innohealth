"""Named coordinate-conversion utilities built on top of :class:`Transform`.

These wrap the generic :meth:`Transform.apply` with clearer names matching
the coordinate systems in play, per the coordinate-system management
requirements (section 9). 3D<->2D camera math lives in
:mod:`thermalmesh.camera.projection`; this module only covers mesh<->world.
"""

from __future__ import annotations

import numpy as np

from thermalmesh.models.transforms import Transform


def mesh_to_world(points: np.ndarray, mesh_to_world_transform: Transform) -> np.ndarray:
    return mesh_to_world_transform.apply(points)


def world_to_mesh(points: np.ndarray, mesh_to_world_transform: Transform) -> np.ndarray:
    return mesh_to_world_transform.inverse().apply(points)
