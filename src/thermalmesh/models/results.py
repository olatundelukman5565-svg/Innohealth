"""Top-level pipeline result aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from thermalmesh.models.camera import CameraPose
from thermalmesh.models.mesh import MeshData


@dataclass
class PipelineResult:
    aligned_mesh: MeshData | None = None
    camera_poses: dict[str, CameraPose] = field(default_factory=dict)
    thermal_observations: dict = field(default_factory=dict)  # geometry_id -> list[TemperatureObservation]
    vertex_temperatures: np.ndarray | None = None
    face_temperatures: np.ndarray | None = None
    point_temperatures: np.ndarray | None = None
    uv_maps: np.ndarray | None = None
    thermal_layers: dict = field(default_factory=dict)  # image_id -> layer dict
    blended_texture: np.ndarray | None = None
    output_files: dict = field(default_factory=dict)
    quality_metrics: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
