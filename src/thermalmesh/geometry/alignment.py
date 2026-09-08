"""Initial/final geometry alignment with automatic strategy selection.

Applies centroid + PCA coarse alignment before ICP refinement so that ICP
is never blindly run on badly-misaligned data (Rule 6 / section 8).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from thermalmesh.geometry.registration import RegistrationResult, centroid_align, icp, pca_align
from thermalmesh.models.transforms import CoordinateSystem, Transform


@dataclass
class AlignmentDiagnostics:
    source_centroid: np.ndarray
    target_centroid: np.ndarray
    source_scale: float
    target_scale: float
    scale_ratio: float
    coarse_method: str
    coarse_result: RegistrationResult
    refined_result: RegistrationResult | None
    confidence: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "source_centroid": self.source_centroid.tolist(),
            "target_centroid": self.target_centroid.tolist(),
            "source_scale": self.source_scale,
            "target_scale": self.target_scale,
            "scale_ratio": self.scale_ratio,
            "coarse_method": self.coarse_method,
            "coarse_fitness": self.coarse_result.fitness,
            "coarse_rmse": self.coarse_result.rmse,
            "refined_method": self.refined_result.method if self.refined_result else None,
            "refined_fitness": self.refined_result.fitness if self.refined_result else None,
            "refined_rmse": self.refined_result.rmse if self.refined_result else None,
            "refined_iterations": self.refined_result.iterations if self.refined_result else 0,
            "confidence": self.confidence,
            "notes": self.notes,
        }


def _scale_estimate(points: np.ndarray) -> float:
    lo, hi = points.min(axis=0), points.max(axis=0)
    return float(np.linalg.norm(hi - lo))


def align_point_sets(
    source_points: np.ndarray,
    target_points: np.ndarray,
    *,
    method: str = "auto",
    max_iterations: int = 100,
    convergence_tolerance: float = 1e-6,
    max_points: int = 20000,
) -> tuple[Transform, AlignmentDiagnostics]:
    """Align ``source_points`` (e.g. initial acquisition) onto ``target_points`` (final mesh).

    Returns the ACQUISITION -> FINAL_MESH transform plus diagnostics.
    """
    notes: list[str] = []

    rng = np.random.default_rng(0)

    def subsample(points: np.ndarray) -> np.ndarray:
        if points.shape[0] <= max_points:
            return points
        idx = rng.choice(points.shape[0], size=max_points, replace=False)
        return points[idx]

    src = subsample(source_points)
    tgt = subsample(target_points)

    source_scale = _scale_estimate(source_points)
    target_scale = _scale_estimate(target_points)
    scale_ratio = target_scale / source_scale if source_scale > 0 else float("inf")
    if not (0.5 < scale_ratio < 2.0):
        notes.append(
            f"Source/target scale ratio is {scale_ratio:.3f}; geometry may not be at a "
            "comparable scale. Only rigid alignment is attempted."
        )

    # Coarse alignment strategy selection.
    if method in ("auto", "pca"):
        centroid_result = centroid_align(src, tgt)
        pca_result = pca_align(src, tgt)
        if method == "pca" or pca_result.rmse < centroid_result.rmse:
            coarse = pca_result
        else:
            coarse = centroid_result
    elif method == "centroid":
        coarse = centroid_align(src, tgt)
    elif method == "none":
        coarse = centroid_align(src, tgt)
        coarse.rotation = np.eye(3)
        coarse.translation = np.zeros(3)
        coarse.method = "none"
    else:
        raise ValueError(f"Unknown registration method '{method}'")

    refined: RegistrationResult | None = None
    if method != "none":
        refined = icp(
            src, tgt,
            initial_rotation=coarse.rotation,
            initial_translation=coarse.translation,
            max_iterations=max_iterations,
            tolerance=convergence_tolerance,
        )
        final_rotation, final_translation = refined.rotation, refined.translation
        final_fitness, final_rmse = refined.fitness, refined.rmse
        if not refined.converged:
            notes.append(f"ICP did not fully converge within {max_iterations} iterations")
    else:
        final_rotation, final_translation = coarse.rotation, coarse.translation
        final_fitness, final_rmse = coarse.fitness, coarse.rmse

    if final_fitness < 0.3:
        notes.append(
            f"Low registration fitness ({final_fitness:.2f}); alignment confidence is low and "
            "should not be trusted without visual/manual verification."
        )

    confidence = float(np.clip(final_fitness * (1.0 / (1.0 + final_rmse)) if final_rmse < np.inf else 0.0, 0.0, 1.0))

    transform = Transform.from_rotation_translation(
        final_rotation, final_translation,
        source=CoordinateSystem.ACQUISITION, target=CoordinateSystem.FINAL_MESH,
        method=f"{coarse.method}+icp" if refined else coarse.method,
        confidence=confidence,
    )
    diagnostics = AlignmentDiagnostics(
        source_centroid=source_points.mean(axis=0),
        target_centroid=target_points.mean(axis=0),
        source_scale=source_scale,
        target_scale=target_scale,
        scale_ratio=scale_ratio,
        coarse_method=coarse.method,
        coarse_result=coarse,
        refined_result=refined,
        confidence=confidence,
        notes=notes,
    )
    return transform, diagnostics
