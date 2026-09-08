"""Build per-image thermal UV layers and the final blended UV texture.

Each layer keeps numerical temperature separate from its PNG visualization
(Rule 8): ``temperature.npy`` is authoritative, ``visualization.png`` is a
colorized rendering for humans only.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from thermalmesh.models.mesh import MeshData
from thermalmesh.uv.thermal_projection import rasterize_vertex_values_to_uv


@dataclass
class ThermalLayer:
    image_id: str
    temperature: np.ndarray
    valid_mask: np.ndarray
    confidence: np.ndarray
    occlusion_mask: np.ndarray

    def visualization(self) -> np.ndarray:
        finite = self.temperature[self.valid_mask]
        vis = np.zeros((*self.temperature.shape, 3), dtype=np.uint8)
        if finite.size == 0:
            return vis
        lo, hi = finite.min(), finite.max()
        normalized = np.zeros_like(self.temperature)
        if hi > lo:
            normalized[self.valid_mask] = (self.temperature[self.valid_mask] - lo) / (hi - lo)
        gray = (normalized * 255).astype(np.uint8)
        colored = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        colored[~self.valid_mask] = 0
        return colored


def build_thermal_layer(
    mesh: MeshData,
    image_id: str,
    per_vertex_temperature: np.ndarray,
    per_vertex_confidence: np.ndarray,
    per_vertex_visible: np.ndarray,
    resolution: int,
) -> ThermalLayer:
    temperature, valid_mask = rasterize_vertex_values_to_uv(mesh, per_vertex_temperature, per_vertex_visible, resolution)
    confidence, _ = rasterize_vertex_values_to_uv(mesh, per_vertex_confidence, per_vertex_visible, resolution)
    occlusion_mask = ~valid_mask
    return ThermalLayer(
        image_id=image_id, temperature=temperature, valid_mask=valid_mask,
        confidence=confidence, occlusion_mask=occlusion_mask,
    )


def build_blended_texture(mesh: MeshData, vertex_temperatures: np.ndarray, resolution: int) -> ThermalLayer:
    valid = np.isfinite(vertex_temperatures)
    safe_values = np.where(valid, vertex_temperatures, 0.0)
    temperature, valid_mask = rasterize_vertex_values_to_uv(mesh, safe_values, valid, resolution)
    confidence = np.ones_like(temperature) * valid_mask
    return ThermalLayer(
        image_id="blended", temperature=temperature, valid_mask=valid_mask,
        confidence=confidence, occlusion_mask=~valid_mask,
    )
