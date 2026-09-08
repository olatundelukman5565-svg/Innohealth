"""Multi-view thermal blending.

A small, extensible strategy hierarchy: :class:`BaseBlender` defines the
interface, :class:`WeightedTemperatureBlender` is the configurable baseline
implementation. Future strategies (uncertainty-aware, temporal, physics-based)
plug in by subclassing :class:`BaseBlender` without touching callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from thermalmesh.models.projection import TemperatureObservation


@dataclass
class BlendResult:
    temperature: float | None
    confidence: float
    observation_count: int
    source_image_ids: list[str]


class BaseBlender(ABC):
    """Interface for combining multiple :class:`TemperatureObservation` into one value."""

    @abstractmethod
    def blend(self, observations: list[TemperatureObservation]) -> BlendResult:
        raise NotImplementedError


class WeightedTemperatureBlender(BaseBlender):
    """Baseline temperature-aware blending: ``T = sum(w_i * T_i) / sum(w_i)``.

    Each weight component is independently toggleable via configuration so
    the weighting model is not hard-coded permanently.
    """

    def __init__(
        self,
        *,
        use_distance_weight: bool = True,
        use_angle_weight: bool = True,
        use_confidence_weight: bool = True,
        min_confidence: float = 0.0,
    ) -> None:
        self.use_distance_weight = use_distance_weight
        self.use_angle_weight = use_angle_weight
        self.use_confidence_weight = use_confidence_weight
        self.min_confidence = min_confidence

    def _weight(self, obs: TemperatureObservation) -> float:
        weight = 1.0
        if self.use_distance_weight:
            weight *= 1.0 / (1.0 + obs.camera_distance)
        if self.use_angle_weight:
            weight *= max(np.cos(obs.viewing_angle), 0.0)
        if self.use_confidence_weight:
            weight *= max(obs.confidence, 0.0)
        return weight

    def blend(self, observations: list[TemperatureObservation]) -> BlendResult:
        usable = [o for o in observations if o.is_usable() and o.confidence >= self.min_confidence]
        if not usable:
            return BlendResult(temperature=None, confidence=0.0, observation_count=0, source_image_ids=[])

        weights = np.array([self._weight(o) for o in usable])
        temps = np.array([o.temperature for o in usable])

        if weights.sum() <= 0:
            weights = np.ones_like(weights)

        blended_temp = float(np.sum(weights * temps) / np.sum(weights))
        blended_confidence = float(np.mean([o.confidence for o in usable]))
        return BlendResult(
            temperature=blended_temp,
            confidence=blended_confidence,
            observation_count=len(usable),
            source_image_ids=[o.image_id for o in usable],
        )


def blend_all(observation_store, blender: BaseBlender, num_geometry: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Blend every geometry element in an :class:`ObservationStore`.

    Returns ``(temperatures, confidences, observation_counts)`` arrays of
    length ``num_geometry``; unobserved elements get ``NaN`` temperature.
    """
    temperatures = np.full(num_geometry, np.nan)
    confidences = np.zeros(num_geometry)
    counts = np.zeros(num_geometry, dtype=np.int64)

    for geometry_id in observation_store.geometry_ids():
        result = blender.blend(observation_store.get(geometry_id))
        if result.temperature is not None:
            temperatures[geometry_id] = result.temperature
            confidences[geometry_id] = result.confidence
            counts[geometry_id] = result.observation_count
    return temperatures, confidences, counts
