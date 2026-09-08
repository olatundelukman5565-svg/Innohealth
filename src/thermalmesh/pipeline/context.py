"""Mutable state shared across pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh

from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.mesh import MeshData
from thermalmesh.models.pointcloud import PointCloudData
from thermalmesh.models.thermal import ThermalImage
from thermalmesh.models.transforms import Transform
from thermalmesh.thermal.observations import ObservationStore


@dataclass
class PipelineContext:
    config: dict

    mesh_path: Path
    initial_mesh_path: Path | None
    thermal_dir: Path
    cameras_path: Path
    output_dir: Path

    mesh: MeshData | None = None
    initial_cloud: PointCloudData | None = None
    cameras: dict[str, Camera] = field(default_factory=dict)
    thermal_images: dict[str, ThermalImage] = field(default_factory=dict)

    alignment_transform: Transform | None = None
    alignment_diagnostics: dict = field(default_factory=dict)

    camera_poses: dict[str, CameraPose] = field(default_factory=dict)
    pose_diagnostics: dict = field(default_factory=dict)

    trimesh_mesh: trimesh.Trimesh | None = None

    projection_results: dict = field(default_factory=dict)  # image_id -> ProjectionResult
    observation_store: ObservationStore = field(default_factory=ObservationStore)

    vertex_temperatures: np.ndarray | None = None
    vertex_confidences: np.ndarray | None = None
    vertex_observation_counts: np.ndarray | None = None
    face_temperatures: np.ndarray | None = None
    point_temperatures: np.ndarray | None = None

    uv_mesh: MeshData | None = None
    thermal_layers: dict = field(default_factory=dict)
    blended_layer: object = None

    output_files: dict[str, str] = field(default_factory=dict)
    quality_metrics: dict = field(default_factory=dict)
    stage_log: list[str] = field(default_factory=list)

    def log_stage(self, message: str) -> None:
        self.stage_log.append(message)
