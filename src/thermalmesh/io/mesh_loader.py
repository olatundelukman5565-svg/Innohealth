"""Loading PLY meshes / point clouds (final reconstruction and optional
initial acquisition data) via trimesh, which handles both binary and ASCII
PLY transparently.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from thermalmesh.models.mesh import MeshData
from thermalmesh.models.pointcloud import PointCloudData
from thermalmesh.models.transforms import CoordinateSystem
from thermalmesh.pipeline.errors import InvalidMeshError


def load_mesh(path: str | Path, coordinate_system: CoordinateSystem = CoordinateSystem.FINAL_MESH) -> MeshData:
    """Load a PLY (or other trimesh-supported) file as a triangle mesh."""
    path = Path(path)
    if not path.exists():
        raise InvalidMeshError(
            f"Mesh file not found: {path}",
            source=str(path),
            reason="File does not exist",
            recommendation="Verify --mesh/--initial-mesh path",
        )
    try:
        loaded = trimesh.load(path, process=False, force="mesh")
    except Exception as exc:  # noqa: BLE001
        raise InvalidMeshError(
            f"Failed to parse mesh file {path}",
            source=str(path),
            reason=str(exc),
            recommendation="Verify the file is a valid PLY mesh",
        ) from exc

    if not isinstance(loaded, trimesh.Trimesh) or loaded.vertices.shape[0] == 0:
        raise InvalidMeshError(
            f"File {path} did not load as a mesh with vertices",
            source=str(path),
            reason="trimesh returned an empty or non-mesh object; the PLY may be a point cloud only",
            recommendation="Use load_point_cloud() for point-cloud-only PLY files",
        )

    normals = np.asarray(loaded.vertex_normals) if loaded.vertex_normals is not None else None
    colors = None
    if loaded.visual is not None and hasattr(loaded.visual, "vertex_colors"):
        try:
            vc = np.asarray(loaded.visual.vertex_colors)
            if vc.shape[0] == loaded.vertices.shape[0]:
                colors = vc
        except Exception:  # noqa: BLE001
            colors = None

    mesh = MeshData(
        vertices=np.asarray(loaded.vertices, dtype=np.float64),
        faces=np.asarray(loaded.faces, dtype=np.int64),
        normals=normals,
        colors=colors,
        coordinate_system=coordinate_system,
        metadata={"source_file": str(path)},
    )
    if not mesh.is_valid():
        raise InvalidMeshError(
            f"Mesh loaded from {path} failed validation",
            source=str(path),
            reason="Non-finite vertices or face indices out of range",
            recommendation="Repair the mesh in a 3D tool before reprocessing",
        )
    return mesh


def load_point_cloud(
    path: str | Path, coordinate_system: CoordinateSystem = CoordinateSystem.ACQUISITION
) -> PointCloudData:
    """Load a PLY file as a point cloud (used for the optional initial acquisition scan)."""
    path = Path(path)
    if not path.exists():
        raise InvalidMeshError(
            f"Point cloud file not found: {path}",
            source=str(path),
            reason="File does not exist",
            recommendation="Verify --initial-mesh path",
        )
    try:
        loaded = trimesh.load(path, process=False)
    except Exception as exc:  # noqa: BLE001
        raise InvalidMeshError(
            f"Failed to parse point cloud file {path}", source=str(path), reason=str(exc),
            recommendation="Verify the file is a valid PLY point cloud",
        ) from exc

    if isinstance(loaded, trimesh.Trimesh):
        points = np.asarray(loaded.vertices, dtype=np.float64)
        normals = np.asarray(loaded.vertex_normals) if loaded.vertex_normals is not None else None
    elif isinstance(loaded, trimesh.points.PointCloud):
        points = np.asarray(loaded.vertices, dtype=np.float64)
        normals = None
    else:
        raise InvalidMeshError(
            f"File {path} did not load as mesh or point cloud",
            source=str(path), reason="Unrecognized trimesh geometry type",
            recommendation="Confirm the PLY file contains point/vertex data",
        )

    cloud = PointCloudData(points=points, normals=normals, coordinate_system=coordinate_system,
                            metadata={"source_file": str(path)})
    if not cloud.is_valid():
        raise InvalidMeshError(
            f"Point cloud loaded from {path} failed validation",
            source=str(path), reason="No points or non-finite coordinates",
            recommendation="Repair the point cloud before reprocessing",
        )
    return cloud
