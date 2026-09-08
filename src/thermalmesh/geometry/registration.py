"""Point-set registration primitives: centroid/PCA coarse alignment and ICP.

Implemented directly with NumPy/SciPy (Kabsch SVD solve + KD-tree nearest
neighbor search) so the pipeline does not require Open3D.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.spatial import cKDTree


@dataclass
class RegistrationResult:
    rotation: np.ndarray  # 3x3
    translation: np.ndarray  # 3
    fitness: float  # fraction of source points with a close correspondence
    rmse: float
    num_correspondences: int
    method: str
    iterations: int = 0
    converged: bool = True
    metadata: dict = field(default_factory=dict)

    @property
    def matrix(self) -> np.ndarray:
        m = np.eye(4)
        m[:3, :3] = self.rotation
        m[:3, 3] = self.translation
        return m


def kabsch(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Optimal rigid rotation+translation mapping ``source`` onto ``target`` (matched, same order)."""
    src_centroid = source.mean(axis=0)
    tgt_centroid = target.mean(axis=0)
    src_centered = source - src_centroid
    tgt_centered = target - tgt_centroid

    h_matrix = src_centered.T @ tgt_centered
    u_mat, _, vt_mat = np.linalg.svd(h_matrix)
    d = np.sign(np.linalg.det(vt_mat.T @ u_mat.T))
    correction = np.diag([1.0, 1.0, d])
    rotation = vt_mat.T @ correction @ u_mat.T
    translation = tgt_centroid - rotation @ src_centroid
    return rotation, translation


def centroid_align(source: np.ndarray, target: np.ndarray) -> RegistrationResult:
    """Coarse alignment: identity rotation, translate source centroid onto target centroid."""
    translation = target.mean(axis=0) - source.mean(axis=0)
    rotation = np.eye(3)
    aligned = source + translation
    fitness, rmse, n_corr = _correspondence_quality(aligned, target)
    return RegistrationResult(rotation, translation, fitness, rmse, n_corr, method="centroid")


def pca_align(source: np.ndarray, target: np.ndarray) -> RegistrationResult:
    """Coarse alignment via principal-axis matching (handles unknown relative orientation)."""

    def principal_axes(points: np.ndarray) -> np.ndarray:
        centered = points - points.mean(axis=0)
        cov = centered.T @ centered
        eigvals, eigvecs = np.linalg.eigh(cov)
        order = np.argsort(eigvals)[::-1]
        axes = eigvecs[:, order]
        if np.linalg.det(axes) < 0:
            axes[:, -1] *= -1
        return axes

    src_axes = principal_axes(source)
    tgt_axes = principal_axes(target)
    rotation = tgt_axes @ src_axes.T
    translation = target.mean(axis=0) - rotation @ source.mean(axis=0)
    aligned = (rotation @ source.T).T + translation
    fitness, rmse, n_corr = _correspondence_quality(aligned, target)
    return RegistrationResult(rotation, translation, fitness, rmse, n_corr, method="pca")


def icp(
    source: np.ndarray,
    target: np.ndarray,
    *,
    initial_rotation: np.ndarray | None = None,
    initial_translation: np.ndarray | None = None,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
    max_correspondence_distance: float | None = None,
) -> RegistrationResult:
    """Point-to-point iterative closest point registration.

    ``max_correspondence_distance`` rejects far correspondences (robust to
    partial overlap); if not given it defaults to a generous multiple of the
    target's bounding diagonal.
    """
    rotation = np.eye(3) if initial_rotation is None else np.array(initial_rotation, dtype=np.float64)
    translation = np.zeros(3) if initial_translation is None else np.array(initial_translation, dtype=np.float64)

    if max_correspondence_distance is None:
        diag = np.linalg.norm(target.max(axis=0) - target.min(axis=0))
        max_correspondence_distance = 0.5 * diag if diag > 0 else np.inf

    target_tree = cKDTree(target)
    prev_rmse = np.inf
    converged = False
    iterations_run = 0

    for iterations_run in range(1, max_iterations + 1):
        current = (rotation @ source.T).T + translation
        distances, indices = target_tree.query(current)
        valid = distances <= max_correspondence_distance
        if valid.sum() < 3:
            break

        matched_src = source[valid]
        matched_tgt = target[indices[valid]]
        rotation, translation = kabsch(matched_src, matched_tgt)

        rmse = float(np.sqrt(np.mean(distances[valid] ** 2)))
        if abs(prev_rmse - rmse) < tolerance:
            converged = True
            prev_rmse = rmse
            break
        prev_rmse = rmse

    final = (rotation @ source.T).T + translation
    fitness, rmse, n_corr = _correspondence_quality(final, target, max_correspondence_distance)
    return RegistrationResult(
        rotation, translation, fitness, rmse, n_corr,
        method="icp", iterations=iterations_run, converged=converged,
    )


def _correspondence_quality(
    aligned: np.ndarray, target: np.ndarray, max_distance: float | None = None
) -> tuple[float, float, int]:
    tree = cKDTree(target)
    distances, _ = tree.query(aligned)
    if max_distance is None:
        diag = np.linalg.norm(target.max(axis=0) - target.min(axis=0))
        max_distance = 0.5 * diag if diag > 0 else np.inf
    valid = distances <= max_distance
    fitness = float(valid.mean()) if len(valid) else 0.0
    rmse = float(np.sqrt(np.mean(distances[valid] ** 2))) if valid.any() else float("inf")
    return fitness, rmse, int(valid.sum())
