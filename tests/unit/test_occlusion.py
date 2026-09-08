import numpy as np
import trimesh

from thermalmesh.camera.extrinsics import look_at_rotation, world_to_camera_translation
from thermalmesh.models.camera import Camera, CameraPose
from thermalmesh.models.projection import Visibility
from thermalmesh.thermal.occlusion import compute_visibility


def _sphere_camera_pose():
    sphere = trimesh.creation.icosphere(subdivisions=2, radius=0.5)
    intrinsics = np.array([[300.0, 0, 80.0], [0, 300.0, 60.0], [0, 0, 1]])
    camera = Camera(camera_id="cam", image_width=160, image_height=120, intrinsic_matrix=intrinsics)
    position = np.array([3.0, 0.0, 0.0])
    rotation = look_at_rotation(position, np.array([0.0, 0.0, 0.0]))
    translation = world_to_camera_translation(position, rotation)
    pose = CameraPose(camera_id="cam", rotation=rotation, translation=translation)
    return sphere, camera, pose


def test_far_side_of_sphere_is_occluded_or_back_facing():
    sphere, camera, pose = _sphere_camera_pose()
    vertices = np.asarray(sphere.vertices)
    normals = np.asarray(sphere.vertex_normals)

    visibility, occlusion_mask, distances, angles = compute_visibility(sphere, vertices, normals, camera, pose)

    near_side = vertices[:, 0] > 0.45
    far_side = vertices[:, 0] < -0.45

    assert np.all(visibility[near_side] == Visibility.VISIBLE)
    assert np.all(np.isin(visibility[far_side], [Visibility.BACK_FACING, Visibility.OCCLUDED]))


def test_occlusion_disabled_marks_back_facing_only_as_hidden():
    sphere, camera, pose = _sphere_camera_pose()
    vertices = np.asarray(sphere.vertices)
    normals = np.asarray(sphere.vertex_normals)

    visibility, occlusion_mask, _, _ = compute_visibility(
        sphere, vertices, normals, camera, pose, occlusion_check=False
    )
    assert not occlusion_mask.any()
