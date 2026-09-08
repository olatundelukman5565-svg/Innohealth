"""GLTF web-visualization export (see export/glb.py for the binary variant)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from thermalmesh.export._mesh_export import build_trimesh
from thermalmesh.models.mesh import MeshData


def export_gltf(mesh: MeshData, visualization_texture: np.ndarray | None, output_path: str | Path) -> Path:
    tm = build_trimesh(mesh, visualization_texture)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tm.export(output_path, file_type="gltf")
    return output_path
