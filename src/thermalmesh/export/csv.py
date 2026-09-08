"""CSV numerical export."""

from __future__ import annotations

import csv as csv_module
from pathlib import Path

import numpy as np

from thermalmesh.models.mesh import MeshData


def export_vertex_csv(
    mesh: MeshData,
    vertex_temperatures: np.ndarray,
    confidences: np.ndarray,
    observation_counts: np.ndarray,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv_module.writer(f)
        writer.writerow(["vertex_id", "x", "y", "z", "temperature", "confidence", "observation_count"])
        for i in range(mesh.num_vertices):
            temp = vertex_temperatures[i]
            writer.writerow([
                i, *mesh.vertices[i],
                "" if np.isnan(temp) else temp,
                confidences[i],
                observation_counts[i],
            ])
    return output_path
