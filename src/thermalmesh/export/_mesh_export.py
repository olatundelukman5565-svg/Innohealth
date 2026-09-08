"""Shared trimesh scene construction for GLB/GLTF export."""

from __future__ import annotations

import numpy as np
import trimesh
from PIL import Image

from thermalmesh.models.mesh import MeshData
from thermalmesh.pipeline.errors import ExportError


def build_trimesh(mesh: MeshData, visualization_texture: np.ndarray | None) -> trimesh.Trimesh:
    if mesh.uv_coordinates is None:
        raise ExportError(
            "Cannot export GLB/GLTF: mesh has no UV coordinates",
            reason="UV generation must run before export",
            recommendation="Run the UV generation stage before export",
        )

    visual = None
    if visualization_texture is not None:
        image = Image.fromarray(
            visualization_texture[:, :, ::-1] if visualization_texture.ndim == 3 else visualization_texture
        )
        material = trimesh.visual.material.PBRMaterial(baseColorTexture=image)
        visual = trimesh.visual.TextureVisuals(uv=mesh.uv_coordinates, material=material)

    return trimesh.Trimesh(
        vertices=mesh.vertices, faces=mesh.faces, vertex_normals=mesh.normals, visual=visual, process=False,
    )
