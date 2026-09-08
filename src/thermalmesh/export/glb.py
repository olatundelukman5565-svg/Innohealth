"""GLB web-visualization export.

The exported texture is a visualization only; the numerical exports
(export/csv.py, numpy.py, json.py, hdf5.py) remain the authoritative
temperature data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from thermalmesh.export._mesh_export import build_trimesh
from thermalmesh.models.mesh import MeshData


def export_glb(mesh: MeshData, visualization_texture: np.ndarray | None, output_path: str | Path) -> Path:
    tm = build_trimesh(mesh, visualization_texture)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tm.export(output_path, file_type="glb")
    return output_path
