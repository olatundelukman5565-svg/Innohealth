import numpy as np
import pytest

from thermalmesh.models.mesh import MeshData
from thermalmesh.models.thermal import ThermalImage
from thermalmesh.models.transforms import CoordinateSystem, Transform


def test_transform_identity_apply():
    t = Transform.identity(CoordinateSystem.ACQUISITION, CoordinateSystem.FINAL_MESH)
    points = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    np.testing.assert_allclose(t.apply(points), points)


def test_transform_inverse_round_trip():
    rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float64)
    translation = np.array([1.0, 2.0, 3.0])
    t = Transform.from_rotation_translation(rotation, translation, CoordinateSystem.ACQUISITION, CoordinateSystem.FINAL_MESH)
    points = np.random.default_rng(0).normal(size=(10, 3))
    transformed = t.apply(points)
    recovered = t.inverse().apply(transformed)
    np.testing.assert_allclose(recovered, points, atol=1e-10)


def test_transform_compose_matches_manual_matmul():
    t1 = Transform.from_rotation_translation(np.eye(3), np.array([1, 0, 0]), CoordinateSystem.ACQUISITION, CoordinateSystem.FINAL_MESH)
    t2 = Transform.from_rotation_translation(np.eye(3), np.array([0, 1, 0]), CoordinateSystem.FINAL_MESH, CoordinateSystem.WORLD)
    composed = t2.compose(t1)
    point = np.array([0.0, 0.0, 0.0])
    np.testing.assert_allclose(composed.apply(point), np.array([1.0, 1.0, 0.0]))


def test_mesh_data_validates_shapes():
    vertices = np.zeros((4, 3))
    faces = np.array([[0, 1, 2]])
    mesh = MeshData(vertices=vertices, faces=faces)
    assert mesh.is_valid()
    assert mesh.num_vertices == 4
    assert mesh.num_faces == 1


def test_mesh_data_rejects_out_of_range_faces():
    vertices = np.zeros((3, 3))
    faces = np.array([[0, 1, 5]])
    mesh = MeshData(vertices=vertices, faces=faces)
    assert not mesh.is_valid()


def test_thermal_image_preserves_raw_values():
    array = np.array([[1.0, np.nan], [3.0, 4.0]])
    image = ThermalImage(image_id="cam_00", temperature_array=array)
    assert image.valid_fraction() == 0.75
    np.testing.assert_array_equal(image.raw_values, array)
    stats = image.statistics()
    assert stats["valid_pixels"] == 3
