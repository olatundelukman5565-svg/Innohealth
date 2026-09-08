"""Storage for per-geometry-element, per-image temperature observations.

Keeps every raw observation (Rule 7) so blending, debugging, and future
advanced analysis all have access to the full observation history rather
than only a single blended value.
"""

from __future__ import annotations

from collections import defaultdict

from thermalmesh.models.projection import TemperatureObservation


class ObservationStore:
    def __init__(self) -> None:
        self._by_geometry: dict[int, list[TemperatureObservation]] = defaultdict(list)

    def add(self, observation: TemperatureObservation) -> None:
        self._by_geometry[observation.geometry_id].append(observation)

    def add_many(self, observations: list[TemperatureObservation]) -> None:
        for obs in observations:
            self.add(obs)

    def get(self, geometry_id: int) -> list[TemperatureObservation]:
        return self._by_geometry.get(geometry_id, [])

    def geometry_ids(self):
        return self._by_geometry.keys()

    def items(self):
        return self._by_geometry.items()

    def __len__(self) -> int:
        return len(self._by_geometry)

    def total_observations(self) -> int:
        return sum(len(v) for v in self._by_geometry.values())

    def summary(self) -> dict:
        counts = [len(v) for v in self._by_geometry.values()]
        return {
            "geometry_elements_with_observations": len(self._by_geometry),
            "total_observations": sum(counts),
            "min_observations_per_element": min(counts) if counts else 0,
            "max_observations_per_element": max(counts) if counts else 0,
            "mean_observations_per_element": (sum(counts) / len(counts)) if counts else 0.0,
        }

    def to_serializable(self) -> dict:
        return {
            str(geometry_id): [
                {
                    "image_id": o.image_id,
                    "temperature": o.temperature,
                    "confidence": o.confidence,
                    "pixel_x": o.pixel_x,
                    "pixel_y": o.pixel_y,
                    "camera_distance": o.camera_distance,
                    "viewing_angle": o.viewing_angle,
                }
                for o in observations
            ]
            for geometry_id, observations in self._by_geometry.items()
        }
