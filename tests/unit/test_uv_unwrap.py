import numpy as np
import trimesh

from thermalmesh.models.mesh import MeshData
from thermalmesh.uv.unwrap import generate_uvs
from thermalmesh.uv.validation import validate_uvs


def _box_mesh():
    box = trimesh.creation.box(extents=(1, 1, 1))
    return MeshData(vertices=np.asarray(box.vertices), faces=np.asarray(box.faces))


def test_generate_uvs_produces_valid_range():
    mesh = _box_mesh()
    uv_mesh = generate_uvs(mesh, resolution=128)
    assert uv_mesh.uv_coordinates is not None
    assert uv_mesh.uv_coordinates.shape[1] == 2
    quality = validate_uvs(uv_mesh)
    assert quality["finite"]
    assert quality["in_unit_range"]


def test_generate_uvs_raises_without_faces():
    mesh = MeshData(vertices=np.zeros((3, 3)), faces=np.zeros((0, 3), dtype=np.int64))
    import pytest

    from thermalmesh.pipeline.errors import UVGenerationError

    with pytest.raises(UVGenerationError):
        generate_uvs(mesh)
