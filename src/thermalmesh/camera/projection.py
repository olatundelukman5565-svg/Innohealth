"""Perspective 3D->2D projection and 2D->3D ray casting.

Vectorized via OpenCV, which handles the pinhole model plus radial/tangential
distortion in one call.
"""

from __future__ import annotations

import cv2
import numpy as np

from thermalmesh.models.camera import Camera, CameraPose


def project_points(points_world: np.ndarray, camera: Camera, pose: CameraPose) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project world points into image pixel coordinates.

    Returns ``(pixels, depths, in_front)`` where ``depths`` is the camera-space
    Z coordinate (>0 means in front of the camera) and ``in_front`` is a
    boolean mask of points with positive depth (i.e. not behind the camera).
    """
    points_world = np.asarray(points_world, dtype=np.float64).reshape(-1, 3)
    rvec, _ = cv2.Rodrigues(pose.rotation)
    tvec = pose.translation.reshape(3, 1)
    distortion = camera.distortion_coefficients
    if distortion is None:
        distortion = np.zeros(5)

    pixels, _ = cv2.projectPoints(points_world, rvec, tvec, camera.intrinsic_matrix, distortion)
    pixels = pixels.reshape(-1, 2)

    camera_space = (pose.rotation @ points_world.T).T + pose.translation
    depths = camera_space[:, 2]
    in_front = depths > 1e-9
    return pixels, depths, in_front


def in_image_bounds(pixels: np.ndarray, width: int, height: int) -> np.ndarray:
    return (pixels[:, 0] >= 0) & (pixels[:, 0] < width) & (pixels[:, 1] >= 0) & (pixels[:, 1] < height)


def pixel_to_camera_ray(camera: Camera, pixel: np.ndarray) -> np.ndarray:
    """Unit direction (in camera space) of the ray through a pixel."""
    pixel = np.asarray(pixel, dtype=np.float64).reshape(-1, 2)
    x = (pixel[:, 0] - camera.cx) / camera.fx
    y = (pixel[:, 1] - camera.cy) / camera.fy
    z = np.ones_like(x)
    directions = np.stack([x, y, z], axis=1)
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    return directions


def pixel_to_world_ray(camera: Camera, pose: CameraPose, pixel: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Ray origin (camera center, world space) and unit direction (world space) through a pixel."""
    cam_dirs = pixel_to_camera_ray(camera, pixel)
    world_dirs = (pose.rotation.T @ cam_dirs.T).T
    origin = pose.camera_center
    return origin, world_dirs
