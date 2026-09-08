import numpy as np
import pytest

from thermalmesh.camera.extrinsics import look_at_rotation, world_to_camera_translation
from thermalmesh.camera.projection import in_image_bounds, pixel_to_world_ray, project_points
from thermalmesh.models.camera import Camera, CameraPose


def _simple_camera_and_pose():
    intrinsics = np.array([[500.0, 0, 320.0], [0, 500.0, 240.0], [0, 0, 1]])
    camera = Camera(camera_id="cam", image_width=640, image_height=480, intrinsic_matrix=intrinsics)
    position = np.array([0.0, 0.0, -2.0])
    rotation = look_at_rotation(position, np.array([0.0, 0.0, 0.0]))
    translation = world_to_camera_translation(position, rotation)
    pose = CameraPose(camera_id="cam", rotation=rotation, translation=translation)
    return camera, pose


def test_project_points_centers_origin_at_principal_point():
    camera, pose = _simple_camera_and_pose()
    pixels, depths, in_front = project_points(np.array([[0.0, 0.0, 0.0]]), camera, pose)
    assert in_front[0]
    np.testing.assert_allclose(pixels[0], [camera.cx, camera.cy], atol=1e-6)
    assert depths[0] == pytest.approx(2.0)


def test_pixel_to_world_ray_hits_known_point():
    camera, pose = _simple_camera_and_pose()
    origin, directions = pixel_to_world_ray(camera, pose, np.array([[camera.cx, camera.cy]]))
    np.testing.assert_allclose(origin, np.array([0.0, 0.0, -2.0]), atol=1e-6)
    # The central ray should point straight along +Z toward the origin.
    np.testing.assert_allclose(directions[0], np.array([0.0, 0.0, 1.0]), atol=1e-6)


def test_in_image_bounds():
    pixels = np.array([[0, 0], [639, 479], [-1, 10], [10, 480]])
    result = in_image_bounds(pixels, 640, 480)
    np.testing.assert_array_equal(result, [True, True, False, False])
